from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import subprocess
import socket
import time
import threading

app = FastAPI()
LOCAL_BACKEND = "http://localhost:5001"

# === Auto-launch MCP Bridge on Demand ===
def is_port_open(port):
    try:
        with socket.create_connection(("localhost", port), timeout=1):
            return True
    except:
        return False

def start_bridge():
    if not is_port_open(5001):
        print("🚀 Starting mcp_bridge.py...")
        subprocess.Popen(["python", "mcp_bridge.py"])
        time.sleep(2)  # Allow bridge to boot

@app.middleware("http")
async def bridge_auto_launcher(request: Request, call_next):
    if not is_port_open(5001):
        thread = threading.Thread(target=start_bridge)
        thread.start()
        time.sleep(1.5)  # ensure it starts before handling
    response = await call_next(request)
    return response

@app.get("/ping")
async def ping():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{LOCAL_BACKEND}/ping")
            return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/generate")
async def generate(request: Request):
    data = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{LOCAL_BACKEND}/generate", json=data)
        return JSONResponse(content=response.json(), status_code=response.status_code)

@app.post("/download_pdf")
async def download_pdf(request: Request):
    data = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{LOCAL_BACKEND}/download_pdf", json=data)
        return JSONResponse(content=response.json(), status_code=response.status_code)

@app.post("/generate_code_file")
async def generate_code_file(request: Request):
    data = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{LOCAL_BACKEND}/generate_code_file", json=data)
        return JSONResponse(content=response.json(), status_code=response.status_code)

@app.post("/detect_tool")
async def detect_tool(request: Request):
    data = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{LOCAL_BACKEND}/detect_tool", json=data)
        return JSONResponse(content=response.json(), status_code=response.status_code)

