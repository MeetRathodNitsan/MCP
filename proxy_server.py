import asyncio
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx, subprocess, socket, time, threading, os, sys

app = FastAPI()


LOCAL_BACKEND = "http://localhost:5001"
BRIDGE_SCRIPT = os.path.join(os.path.dirname(__file__), "mcp_bridge.py")
TIMEOUT = httpx.Timeout(connect=10.0, read=180.0, write=60.0, pool=60.0)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Port check ===
def is_port_open(port: int) -> bool:
    try:
        with socket.create_connection(("localhost", port), timeout=1):
            return True
    except:
        return False

# === Launch bridge if not running ===
def start_bridge():
    if not is_port_open(5001):
        bridge_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "mcp_bridge.py"))
        print(f"🚀 Launching MCP bridge from: {bridge_path}")
        try:
            creationflags = 0
            if os.name == "nt":  # Windows
                creationflags = subprocess.CREATE_NO_WINDOW

            proc = subprocess.Popen(
                [sys.executable, bridge_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creationflags
            )
            print("✅ Bridge process started (non-blocking).")
        except Exception as e:
            print("❌ Bridge failed to start:", e)


# === Middleware to ensure bridge is live ===
@app.middleware("http")
async def ensure_bridge(request: Request, call_next):
    if not is_port_open(5001):
        print("🟡 Starting MCP Bridge...")
        thread = threading.Thread(target=start_bridge)
        thread.start()

        for _ in range(30):  # wait up to 15 seconds
            if is_port_open(5001):
                print("✅ MCP Bridge is ready.")
                break
            time.sleep(0.5)
        else:
            return JSONResponse({"error": "Bridge startup timeout"}, status_code=500)

    return await call_next(request)

# === API Endpoints ===

@app.get("/ping")
async def ping():
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{LOCAL_BACKEND}/ping")
            return JSONResponse(content=r.json(), status_code=r.status_code)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/generate")
async def generate(request: Request):
    data = await request.json()
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(f"{LOCAL_BACKEND}/generate", json=data)
            return JSONResponse(content=r.json(), status_code=r.status_code)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/download_pdf")
async def download_pdf(request: Request):
    data = await request.json()
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(f"{LOCAL_BACKEND}/download_pdf", json=data)
            return JSONResponse(content=r.json(), status_code=r.status_code)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/generate_code_file")
async def generate_code_file(request: Request):
    data = await request.json()
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(f"{LOCAL_BACKEND}/generate_code_file", json=data)
            return JSONResponse(content=r.json(), status_code=r.status_code)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/detect_tool")
async def detect_tool(request: Request):
    data = await request.json()
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(f"{LOCAL_BACKEND}/detect_tool", json=data)
            return JSONResponse(content=r.json(), status_code=r.status_code)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
