# Developed By Meet Rathod

import json
import re
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from duckduckgo_search import DDGS
import os
from mcp_server import generate_code_file

DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "downloads")

print("[INFO] mcp_bridge.py: Started running.")

class SimpleHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")  
        self.end_headers()


    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()    

    def do_GET(self):
        if self.path == "/ping":
            self._set_headers()
            self.wfile.write(json.dumps({"status": "alive"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode())
            
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(length).decode('utf-8')

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": f"Invalid JSON: {str(e)}"}).encode())
            return

        if self.path == "/generate":
            prompt = data.get("prompt", "")
            try:
                response = requests.post("http://localhost:11434/api/generate", json={
                    "model": "llama3.2:1b",
                    "prompt": prompt,
                    "stream": False
                })
                result = response.json()
                self._set_headers()
                self.wfile.write(json.dumps({"response": result.get("response", "")}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        elif self.path == "/download_pdf":
            query = data.get("query", "")
            try:
                with DDGS() as ddgs:
                    results = ddgs.text(query + " filetype:pdf", max_results=10)
                pdf_urls = [r['href'] for r in results if r['href'].lower().endswith('.pdf')]
                if not pdf_urls:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "No PDFs found."}).encode())
                    return

                for i, url in enumerate(pdf_urls, 1):
                    try:
                        response = requests.get(url, stream=True, timeout=20)
                        if "application/pdf" not in response.headers.get("Content-Type", "").lower():
                            continue
                        response.raise_for_status()
                        filename = re.sub(r'\W+', '_', query)[:50] + f"_{i}.pdf"
                        filepath = os.path.join(DOWNLOAD_DIR, filename)
                        with open(filepath, "wb") as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                        self._set_headers()
                        self.wfile.write(json.dumps({
                            "status": "success",
                            "file": filename,
                            "path": filepath,
                            "url": url
                        }).encode())
                        return
                    except Exception:
                        continue

                self._set_headers(500)
                self.wfile.write(json.dumps({"error": "All downloads failed."}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        elif self.path == "/detect_tool":
            prompt = data.get("prompt", "")
            try:
                detect_prompt = (
                    f"You are a smart assistant.\n"
                    f"User said: \"{prompt}\"\n"
                    f"Choose a tool to fulfill this request:\n"
                    f"- If they want help or information, use: generate\n"
                    f"- If they want to download a file, document or PDF, use: download_pdf\n"
                    f"- If they want to write or generate some code, use: generate_code_file\n"
                    f"Reply with only one of these: generate, download_pdf, generate_code_file"
                )
                response = requests.post("http://localhost:11434/api/generate", json={
                    "model": "llama3.2:1b",
                    "prompt": detect_prompt,
                    "stream": False
                })
                result = response.json()
                tool = result.get("response", "generate").strip().lower()
                self._set_headers()
                self.wfile.write(json.dumps({"tool": tool}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        elif self.path == "/generate_code_file":
            language = data.get("language", "")
            task = data.get("task", "")
            result = generate_code_file(language, task)
            self._set_headers()
            self.wfile.write(json.dumps({"response": result}).encode())

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Route not found"}).encode())

def run():
    print("[INFO] MCP Bridge: Starting server...")
    server = HTTPServer(('localhost', 5001), SimpleHandler)
    server.serve_forever()

if __name__ == "__main__":
    print("[INFO] MCP Bridge __main__ triggered.")
    run()

# Developed By Meet Rathod
