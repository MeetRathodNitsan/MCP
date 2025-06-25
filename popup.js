document.addEventListener("DOMContentLoaded", () => {
  const askBtn = document.getElementById("askBtn");
  const promptInput = document.getElementById("prompt");
  const chatBox = document.getElementById("chat-container");

  // Create a hidden anchor element for safe, single-download use
  const downloadLink = document.createElement("a");
  downloadLink.style.display = "none";
  document.body.appendChild(downloadLink);

  promptInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askBtn.click();
    }
  });

  const history = JSON.parse(localStorage.getItem("mcp_history") || "[]");
  history.forEach(({ role, content }) => appendBubble(role, content));

  askBtn.addEventListener("click", async () => {
    const prompt = promptInput.value.trim();
    if (!prompt) return;

    appendBubble("user", prompt);
    saveToHistory("user", prompt);
    promptInput.value = "";

    let tool = detectTool(prompt);

    if (tool === "unknown") {
      try {
        const detectRes = await fetch("http://localhost:8010/detect_tool", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt })
        });
        const result = await detectRes.json();
        tool = result.tool;
      } catch (err) {
        appendBubble("ai", `❌ Tool detection failed: ${err.message}`);
        return;
      }
    }

    try {
      if (tool === "download_pdf") {
        const res = await fetch("http://localhost:8010/download_pdf", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: prompt })
        });
        const data = await res.json();
        if (data.status === "success") {
          appendBubble("ai", `📄 PDF downloaded: ${data.file}`);
          saveToHistory("ai", `📄 PDF downloaded: ${data.file}`);
        } else {
          appendBubble("ai", "❌ Failed to download PDF.");
        }
      } else if (tool === "generate_code_file") {
        const language = guessLanguage(prompt);
        const task = prompt;
        const res = await fetch("http://localhost:8010/generate_code_file", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ language, task })
        });
        const data = await res.json();
        const code = data.response || "⚠️ No code generated.";
        appendBubble("ai", code);
        saveToHistory("ai", code);

        // Safely trigger single download
        const blob = new Blob([code], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        downloadLink.href = url;
        downloadLink.download = `generated_code.${language.toLowerCase()}`;
        downloadLink.click();
        URL.revokeObjectURL(url);
      } else {
        const res = await fetch("http://localhost:8010/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt })
        });
        const data = await res.json();
        const reply = data.response || "⚠️ No response.";
        appendBubble("ai", reply);
        saveToHistory("ai", reply);
      }
    } catch (err) {
      const errorMsg = `❌ ${err.message}`;
      appendBubble("ai", errorMsg);
      saveToHistory("ai", errorMsg);
    }
  });

  function detectTool(text) {
    const lower = text.toLowerCase();
    if (lower.includes("pdf") || lower.includes("download")) return "download_pdf";
    if (
      lower.includes("code") ||
      ["python", "html", "javascript", "java", "c++", "react"].some((w) =>
        lower.includes(w)
      )
    )
      return "generate_code_file";
    return "unknown";
  }

  function guessLanguage(text) {
    const lower = text.toLowerCase();
    if (lower.includes("python")) return "python";
    if (lower.includes("html")) return "html";
    if (lower.includes("javascript")) return "javascript";
    if (lower.includes("java")) return "java";
    if (lower.includes("c++")) return "cpp";
    if (lower.includes("react")) return "jsx";
    return "txt";
  }

  function appendBubble(role, text) {
    const bubble = document.createElement("div");
    bubble.classList.add("bubble", role === "user" ? "user-msg" : "ai-msg");
    bubble.innerText = text;
    chatBox.appendChild(bubble);
    chatBox.scrollTop = chatBox.scrollHeight;

    setTimeout(() => {
      bubble.style.transition = "all 0.3s ease";
      bubble.style.opacity = "1";
      bubble.style.transform = "translateY(0)";
    }, 10);
  }

  function saveToHistory(role, content) {
    history.push({ role, content });
    localStorage.setItem("mcp_history", JSON.stringify(history));
  }
});
