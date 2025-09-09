// static/js/main.js

export function showSolvedBox() {
    const box = document.getElementById("solved-box");
    if (box) {
        box.style.display = "block";
    }
}

export function initChat({ endpoint, botName = "Bot", solvedCallback }) {
  const form = document.getElementById("challenge-form");
  const input = document.getElementById("input");
  const messagesDiv = document.getElementById("messages");
  const submitBtn = document.getElementById("submit-btn");

  let isProcessing = false;
  const originalBtnText = submitBtn ? submitBtn.textContent : "Send";
  const originalBtnBg = submitBtn ? submitBtn.style.backgroundColor : "";
  const disabledBtnBg = "#aaa";

  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      if (isProcessing) {
        e.preventDefault();
        return;
      }
      e.preventDefault();
      form.requestSubmit();
    }
  });

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    if (isProcessing) return; // Block if processing
    const userInput = input.value.trim();
    if (!userInput) {
      // Do not lock UI or set isProcessing if input is empty
      return;
    }
    // Only now, after input is validated, lock UI and set isProcessing
    isProcessing = true;
    input.disabled = true;
    submitBtn.disabled = true;
    submitBtn.textContent = "Processing...";
    submitBtn.style.backgroundColor = disabledBtnBg;
    input.value = "";

    appendMessage("You", userInput, "user");
    appendTypingIndicator();

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: userInput }),
      });

      if (res.status === 429) {
        const data = await res.json();
        document.getElementById("typing-indicator")?.remove();
        appendMessage(botName, data.error || "The LLM is busy. Please wait and try again.", "bot");
        return;
      }

      const data = await res.json();
      document.getElementById("typing-indicator")?.remove();
      appendMessage(botName, data.response, "bot");

      if (data.solved) {
        if (typeof showSolvedBox === "function") {
          showSolvedBox();
        }
        solvedCallback?.();
      }
    } catch (err) {
      document.getElementById("typing-indicator")?.remove();
      appendMessage(botName, "Oops! Something went wrong.", "bot");
    } finally {
      submitBtn.textContent = originalBtnText;
      submitBtn.style.backgroundColor = originalBtnBg;
      submitBtn.disabled = false;
      input.disabled = false;
      isProcessing = false;
    }
  });

  function appendMessage(sender, text, role, skipLabel = false) {
    const msg = document.createElement("div");
    msg.classList.add("message", role === "user" ? "user-message" : "bot-message");

    if (!skipLabel) {
      const label = document.createElement("span");
      label.classList.add("sender-label");
      label.textContent = sender;
      msg.appendChild(label);
    }

    const content = document.createElement("div");
    content.innerHTML = text.replace(/\n/g, "<br>");
    msg.appendChild(content);

    messagesDiv.appendChild(msg);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  function appendTypingIndicator() {
    const typingContainer = document.createElement("div");
    typingContainer.classList.add("message", "bot-message");
    typingContainer.id = "typing-indicator";

    const label = document.createElement("span");
    label.classList.add("sender-label");
    label.textContent = botName;
    typingContainer.appendChild(label);

    const dots = document.createElement("div");
    dots.classList.add("typing-dots");
    dots.innerHTML = "<span></span><span></span><span></span>";
    typingContainer.appendChild(dots);

    messagesDiv.appendChild(typingContainer);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }
}
