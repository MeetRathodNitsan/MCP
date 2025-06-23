document.addEventListener("DOMContentLoaded", () => {
  const askBtn = document.getElementById("askBtn");
  const promptInput = document.getElementById("prompt");
  const chatBox = document.getElementById("chat-container");

  const toolSelect = document.getElementById("tool");
  const langInput = document.getElementById("lang");
  const taskInput = document.getElementById("task");

  // Load previous history from localStorage
  const history = JSON.parse(localStorage.getItem("mcp_history") || "[]");
  history.forEach(({ role, content }) => {
    appendBubble(role, content);
  });

  // Tool selector logic
  toolSelect.addEventListener("change", () => {
    const isCodeTool = toolSelect.value === "generate_code_file";
    langInput.style.display = isCodeTool ? "block" : "none";
    taskInput.style.display = isCodeTool ? "block" : "none";
    promptInput.style.display = isCodeTool ? "none" : "block";
  });

  // Handle Ask Button
  askBtn.addEventListener("click", async () => {
    const selectedTool = toolSelect.value;

    if (selectedTool === "ask_llm") {
      const prompt = promptInput.value.trim();
      if (!prompt) return;

      appendBubble("user", prompt);
      saveToHistory("user", prompt);
      promptInput.value = "";

      try {
        const res = await fetch("http://localhost:5001/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt })
        });

        const data = await res.json();
        const reply = data.response || "⚠️ No response.";
        appendBubble("ai", reply);
        saveToHistory("ai", reply);
      } catch (err) {
        const errorMsg = `❌ ${err.message}`;
        appendBubble("ai", errorMsg);
        saveToHistory("ai", errorMsg);
      }
    }

    else if (selectedTool === "generate_code_file") {
      const language = langInput.value.trim();
      const task = taskInput.value.trim();
      if (!language || !task) return;

      const requestText = `Generate ${language} code to: ${task}`;
      appendBubble("user", requestText);
      saveToHistory("user", requestText);

      try {
        const res = await fetch("http://localhost:5001/generate_code_file", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ language, task })
        });

        const data = await res.json();
        const reply = data.response || "⚠️ No response.";
        appendBubble("ai", reply);
        saveToHistory("ai", reply);
      } catch (err) {
        const errorMsg = `❌ ${err.message}`;
        appendBubble("ai", errorMsg);
        saveToHistory("ai", errorMsg);
      }
    }
  });

  // Append chat bubble
  function appendBubble(role, text) {
    const bubble = document.createElement("div");
    bubble.classList.add("bubble", role === "user" ? "user-msg" : "ai-msg");

    // Animate bubble
    bubble.style.opacity = "0";
    bubble.style.transform = "translateY(10px)";
    bubble.innerText = text;
    chatBox.appendChild(bubble);
    chatBox.scrollTop = chatBox.scrollHeight;

    setTimeout(() => {
      bubble.style.transition = "all 0.3s ease";
      bubble.style.opacity = "1";
      bubble.style.transform = "translateY(0)";
    }, 10);
  }

  // Store to localStorage
  function saveToHistory(role, content) {
    history.push({ role, content });
    localStorage.setItem("mcp_history", JSON.stringify(history));
  }
});
