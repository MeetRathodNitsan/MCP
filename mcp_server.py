import os
import re
import json
import requests
from PyPDF2 import PdfReader
from duckduckgo_search import DDGS

TOOLS = {
    "list_files": {"description": "List files in the current folder", "parameters": {}},
    "read_file": {"description": "Read a file", "parameters": {"path": "Path of the file"}},
    "write_file": {"description": "Write content to a file", "parameters": {"path": "Path to the file", "content": "Content to write"}},
    "modify_file": {"description": "Modify a file", "parameters": {"path": "Path to the file", "content": "Content to write"}},
    "ask_llm": {"description": "Ask a prompt to your local Ollama LLM", "parameters": {"prompt": "Your prompt text"}},
    "search_and_download_pdf": {"description": "Search and auto-download first PDF for query", "parameters": {"query": "Search keywords for PDF"}},
    "summarize_pdf": {"description": "Summarize content from a PDF", "parameters": {"path": "Path to the PDF"}},
    "detect_intent": {"description": "Determine the appropriate tool for a free-form task", "parameters": {"prompt": "User input"}},
    "generate_code_file":{"description": "Generate code and save it to a file", "parameters": {"language": "Programming language (e.g., Python, HTML, JavaScript)","task": "Describe what the code should do"}}
}

# === Tool Functions ===
def list_files():
    return os.listdir()

def read_file(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"\u274c Error: {e}"

def write_file(path, content):
    try:
        with open(path, "w") as f:
            f.write(content)
        return f"\u2705 File '{path}' written successfully."
    except Exception as e:
        return f"\u274c Error: {e}"

def modify_file(path, content):
    try:
        with open(path, "w+") as f:
            f.write(content)
        return f"\u2705 File '{path}' modified successfully."
    except Exception as e:
        return f"\u274c Error: {e}"

def ask_llm_chat():
    print("💬 Entering LLM chat mode (type 'exit' to quit)...\n")
    history = []

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Exiting chat.")
            break
        history.append(f"User: {user_input}")
        prompt = "\n".join(history) + "\nAI:"
        try:
            reply = call_llm(prompt)
            print("AI:", reply.strip())
            history.append(f"AI: {reply.strip()}")
        except Exception as e:
            print(f"|Ollama error: {e}")

def call_llm(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {"model": "granite3.3:latest", "prompt": prompt, "stream": False}
    res = requests.post(url, json=payload)
    return res.json().get("response", "No response from model.")

def search_and_download_pdf(query):
    with DDGS() as ddgs:
        results = ddgs.text(query + " filetype:pdf", max_results=10)
    pdf_urls = [r['href'] for r in results if r['href'].lower().endswith('.pdf')]
    for i, url in enumerate(pdf_urls, start=1):
        try:
            response = requests.get(url, stream=True, timeout=20)
            response.raise_for_status()
            filename = re.sub(r'\W+', '_', query)[:50] + f"_{i}.pdf"
            with open(filename, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return f"\u2705 PDF downloaded: {filename} (from {url})"
        except Exception as e:
            continue
    return "\u274c All found links failed to download."

def summarize_pdf(path):
    try:
        reader = PdfReader(path)
        text = "".join([page.extract_text() for page in reader.pages[:3]])
        return call_llm("Summarize this:\n" + text[:2000])
    except Exception as e:
        return f"\u274c PDF error: {e}"
    
def generate_code_file(language, task):
    prompt = f"Write a complete {language} program that does the following:\n{task}"
    try:
        res = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2:1b",
            "prompt": prompt,
            "stream": False
        })
        code = res.json().get("response", "")
        ext = {"python": "py", "html": "html", "javascript": "js", "java": "java", "c": "c"}.get(language.lower(), "txt")
        filename = f"generated_code.{ext}"
        with open(filename, "w") as f:
            f.write(code)
        return f"✅ Code saved as `{filename}`.\n\n💡 Output Preview:\n{code[:500]}..."
    except Exception as e:
        return f"❌ Error generating code: {e}"

    
def detect_intent(prompt):
    try:
        tool_list = list(TOOLS.keys())
        tool_list_str = ", ".join(tool_list)
        reformulated_prompt = (
            f"Given this request: '{prompt}', choose the best matching tool name from this list:\n"
            f"{tool_list_str}\n\n"
            "Reply with ONLY the exact tool name from the list. No explanation."
        )

        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "llama3.2:1b",
            "prompt": reformulated_prompt,
            "stream": False
        }
        res = requests.post(url, json=payload)
        reply = res.json().get("response", "").strip()

        # Validate the reply
        if reply in TOOLS:
            return reply
        else:
            return "❌ LLM responded with an invalid tool: " + reply

    except Exception as e:
        return f"❌ LLM error: {e}"



def run_mcp():
    print("\nMCP Agent with Web + LLM Toolchain")
    print("Type a request or use tool names. Type 'exit' to quit.")
    while True:
        cmd = input("\n Your command: ").strip()
        if cmd.lower() == "exit":
            print("\ud83d\udc4b Goodbye!")
            break

        tool = cmd if cmd in TOOLS else detect_intent(cmd)

        if tool not in TOOLS:
            print("\u274c Unknown tool or intent.")
            continue

        args = {}
        for param in TOOLS[tool]["parameters"]:
            args[param] = input(f"\u2728 Enter value for '{param}': ")

        if tool == "list_files":
            result = list_files()
        elif tool == "read_file":
            result = read_file(args["path"])
        elif tool == "write_file":
            result = write_file(args["path"], args["content"])
        elif tool == "modify_file":
            result = modify_file(args["path"], args["content"])
        elif tool == "ask_llm":
            ask_llm_chat()
            continue
        elif tool == "generate_code_file":
            result = generate_code_file(args["language"], args["task"])
        elif tool == "search_and_download_pdf":
            result = search_and_download_pdf(args["query"])
        elif tool == "summarize_pdf":
            result = summarize_pdf(args["path"])
        else:
            result = "\u274c Tool not implemented."

        print("\nResult:\n", result)

if __name__ == "__main__":
    run_mcp()
