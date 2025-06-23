
import json
import re
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from duckduckgo_search import DDGS

from mcp_server import generate_code_file

class SimpleHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length).decode('utf-8'))

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
                        response.raise_for_status()
                        filename = re.sub(r'\W+', '_', query)[:50] + f"_{i}.pdf"
                        with open(filename, "wb") as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                        self._set_headers()
                        self.wfile.write(json.dumps({"status": "success", "file": filename, "url": url}).encode())
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
                    f"Given the user request: '{prompt}', respond ONLY with one tool name: 'generate', 'download_pdf', or 'summarize_pdf'."
                    f" Do not explain, just return the tool name."
                )
                response = requests.post("http://localhost:11434/api/generate", json={
                    "model": "llama ",
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
    print("🔌 MCP Dynamic Tool Router running at http://localhost:5001")
    server = HTTPServer(('localhost', 5001), SimpleHandler)
    server.serve_forever()

if __name__ == "__main__":
    run()
