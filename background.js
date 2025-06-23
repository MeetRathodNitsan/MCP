chrome.runtime.onMessage.addListener(async (request, sender, sendResponse) => {
  if (request.action === "generate") {
    try {
      const response = await fetch("http://localhost:11434/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "llama3.2:1b",
          prompt: request.prompt,
          stream: false
        })
      });

      const text = await response.text(); // Capture raw response text
      console.log("🔄 Raw Ollama Response:", text);

      const data = JSON.parse(text); // Manually parse so we see errors
      sendResponse({ result: data.response || "No response from model" });
    } catch (error) {
      console.error("❌ Error communicating with Ollama:", error);
      sendResponse({ error: error.message || "Unknown background error" });
    }
    return true;
  }
});
