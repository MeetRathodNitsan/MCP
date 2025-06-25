# 🧠 Quorb — Your Personal AI Assistant 🚀

A smart browser extension that acts like your **local AI assistant** — able to:
- ✨ Chat with an LLM
- 📄 Download relevant PDF files from the web
- 💻 Generate executable code snippets in various languages

## 🔍 Features

✅ **Natural Language Prompting**  
Just type like a normal human — no need for special syntax or commands.  
> “Download a PDF about chess” → ✅ Done  
> “Python code to sort numbers” → ✅ Code file generated  
> “What is AI?” → ✅ Instant response

✅ **Automatic Intent Detection**  
Quorb intelligently detects whether you're:
- Asking a question
- Wanting to download a file
- Requesting code

✅ **Clean Chat UI**  
Minimalist extension UI built with HTML, CSS, and JavaScript. All responses appear as friendly chat bubbles.

---

## ⚙️ How It Works

1. 🧠 `popup.js` detects the user's intent via keywords or LLM
2. 📡 Sends request to `mcp_bridge.py` backend
3. 🗃️ Depending on the intent:
   - Calls local LLM (via Ollama) for chat
   - Searches DuckDuckGo and downloads PDFs
   - Uses AI to generate code and triggers download
4. 📡 FastAPI based proxy server for automatically invoking mcp bridge.


## 🧪 Tech Stack

| Component       | Tech                              |
|----------------|-----------------------------------|
| Extension UI    | HTML + CSS + JS                   |
| Backend Server  | Python + HTTPServer               |
| Tool Detection  | Keyword Matching + granite LLM   |
| Code Gen        | Custom `/generate_code_file` route|
| PDF Search      | DuckDuckGo Search API             |
| Auto Launcher   | Python subprocess manager         |

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/MeetRathodNitsan/Quorb---Your-Personal-AI-Assistant.git
cd Quorb---Your-Personal-AI-Assistant
```
## © All Right Reserved by the owner of this git repository.
