from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI()

# Replace with your Wispbyte HTTP address (no trailing slash)
TARGET_URL = "http://93.115.101.109:12384"   # e.g., http://abc123.pylex.software:8000

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy(request: Request, full_path: str):
    async with httpx.AsyncClient() as client:
        url = f"{TARGET_URL}/{full_path}"
        headers = dict(request.headers)
        # Remove headers that might cause issues
        headers.pop("host", None)
        headers.pop("content-length", None)

        if request.method in ("POST", "PUT", "PATCH"):
            body = await request.body()
            resp = await client.request(request.method, url, headers=headers, content=body)
        else:
            resp = await client.request(request.method, url, headers=headers, params=request.query_params)

    return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))
