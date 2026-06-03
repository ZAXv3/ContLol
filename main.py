from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI()

# Replace with your Wispbyte HTTP address (no trailing slash)
TARGET_URL = "http://93.115.101.109:12384"

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy(request: Request, full_path: str):
    # Use a 30-second timeout to avoid premature termination
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{TARGET_URL}/{full_path}"
        headers = dict(request.headers)
        # Remove headers that might cause issues
        headers.pop("host", None)
        headers.pop("content-length", None)

        try:
            if request.method in ("POST", "PUT", "PATCH"):
                body = await request.body()
                resp = await client.request(request.method, url, headers=headers, content=body)
            else:
                resp = await client.request(request.method, url, headers=headers, params=request.query_params)
        except httpx.TimeoutException:
            # Return a user-friendly 504 error when Flask takes too long
            return Response(
                content="The verification server is temporarily slow. Please try again in a moment.",
                status_code=504,
                headers={"Content-Type": "text/plain"}
            )
        except Exception as e:
            # Catch any other proxy errors
            return Response(
                content=f"Proxy error: {str(e)}",
                status_code=502,
                headers={"Content-Type": "text/plain"}
            )

    # Forward the response exactly as received
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=dict(resp.headers)
    )
