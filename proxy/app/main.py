from fastapi import FastAPI, Request, WebSocket, Response, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import httpx
import asyncio
import logging
import websockets
from http.cookies import SimpleCookie
from datetime import datetime
import os

# VARIABLES
WEB_INTEGRATION_ID = os.getenv("WEB_INTEGRATION_ID")
QLIK_TENANT_ID = os.getenv("QLIK_TENANT_ID")
PROXY_URL = os.getenv("PROXY_URL")

LOCALHOST_AVAIABLE = os.getenv("LOCALHOST_AVAIABLE", "False").lower() == 'true'
if LOCALHOST_AVAIABLE:
    MASHUP_PORT = os.getenv("MASHUP_PORT")
    MASHUP_DOMAIN = os.getenv("MASHUP_DOMAIN")

# List of cookies that qlik uses
QLIK_COOKIES = ["AWSALBCORS", "eas.sid", "eas.sid.sig", "_csrfToken", "_csrfToken.sig"]

# Lista de extensões de arquivos estáticos
STATIC_EXTENSIONS = (".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2", ".ttf", ".eot")

# Criando a aplicação FastAPI
app = FastAPI()

# Definição de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Request to get the CSRF Token based on cookie
async def get_csrf_token(cookies):
    url = f"https://{PROXY_URL}/api/v1/csrf-token"
    headers = {
        "qlik-web-integration-id": WEB_INTEGRATION_ID
    }
    
    async with httpx.AsyncClient(cookies=cookies) as client:
        response = await client.get(url, headers=headers, follow_redirects=True)
        
    if response.status_code < 300:
        return response.headers.get("qlik-csrf-token")
    
    return None

# Proxy for websocket API Capability
@app.websocket("/app/{app_id}")
async def websocket_endpoint(websocket: WebSocket, app_id: str):
    await websocket.accept()
    
    cookie_header = websocket.headers.get("cookie")
    if not cookie_header:
        await websocket.close()
        return
    
    cookie_dict = SimpleCookie(cookie_header)

    cookies_needed = {key: cookie_dict[key].value for key in QLIK_COOKIES if key in cookie_dict}
    cookie_string = "; ".join([f"{key}={value}" for key, value in cookies_needed.items()])

    # Replacing application urls for qlik cloud
    url_qlik = str(websocket.url)
    url_qlik = url_qlik.replace(PROXY_URL, QLIK_TENANT_ID)
    
    if LOCALHOST_AVAIABLE:
        url_qlik = (
            url_qlik.replace(PROXY_URL, QLIK_TENANT_ID)
            .replace('localhost/app/', f'{QLIK_TENANT_ID}/app/')
            .replace(f'localhost%3A{MASHUP_PORT}', MASHUP_DOMAIN)
            .replace('http%3A', 'https%3A')
            .replace('ws://', 'wss://')
        )

    if 'qlik-csrf-token' not in url_qlik:
        csrf_token = await get_csrf_token(cookies_needed)
        if not csrf_token:
            logging.error("❌ Não foi possível obter o CSRF Token")
            await websocket.close()
            return
        url_qlik = f"{url_qlik}&qlik-csrf-token={csrf_token}"

    try:
        async with websockets.connect(url_qlik, extra_headers=[("Cookie", cookie_string)]) as qlik_ws:
            async def receive_from_client():
                try:
                    while True:
                        data = await websocket.receive_text()
                        await qlik_ws.send(data)
                except WebSocketDisconnect:
                    logging.warning("⚠️ Frontend desconectou.")
                    pass

            async def receive_from_qlik():
                try:
                    while True:
                        data = await qlik_ws.recv()
                        await websocket.send_text(data)
                except WebSocketDisconnect:
                    logging.warning("⚠️ Qlik Cloud WebSocket desconectou.")
                    pass

            await asyncio.gather(receive_from_client(), receive_from_qlik())

    except Exception as e:
        logging.error(f"🔥 Erro na conexão WebSocket: {str(e)}")
        await websocket.close()

# Redirect static files to Qlik Cloud
@app.get("/{path:path}")
async def serve_static_files(path: str, request: Request):
    if path.endswith(STATIC_EXTENSIONS):
        return RedirectResponse(url=f"https://{QLIK_TENANT_ID}/{path}")
    return await proxy(request, path)

# Proxy for all requests
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, path: str):
    url = f"https://{QLIK_TENANT_ID}/{path}"
    params = request.query_params
    new_url = f"{url}?{params}" if params else url

    headers = dict(request.headers)
    headers.pop("host", None)

    """
    This block identify the origin of the request and set the domain for the cookies validating whether it is localhost or not.
    If do you need to set the cookies for specific domain, you can set the domain in the variable "origem" and delete this block.
    """
    origem = headers.get("origin", None)
    if origem and "localhost" in origem:
        origem = "localhost"
    elif origem:
        origem = ".".join(origem.split(".")[1:]) #remove subdomain to create cookies for full domain.
        origem = f".{origem}"
        
    method = request.method

    cookies_needed = {k: v for k, v in request.cookies.items() if k in QLIK_COOKIES}
    
    # Remove a origem antes de enviar para o Qlik
    headers.pop("origin", None)
    headers.pop("Origin", None)

    async with httpx.AsyncClient(cookies=cookies_needed) as client:
        res = await client.request(method, new_url, headers=headers, cookies=cookies_needed, follow_redirects=True)

    cookies = res.cookies
    new_headers = dict(res.headers)

    headers_to_remove = ["content-encoding", "transfer-encoding", "content-length", "set-cookie"]
    for header in headers_to_remove:
        new_headers.pop(header.lower(), None)

    response = Response(content=res.content, status_code=res.status_code, headers=new_headers)

    # Pass cookies to the frontend
    for key, value in cookies.items():
        response.set_cookie(
            key,
            value=value,
            domain=origem,
            httponly=True,
            max_age=3600,
            samesite="None",
            secure=True
        )

    return response