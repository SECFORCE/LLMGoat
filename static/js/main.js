// static/js/main.js

function showSolvedBox() {
    const box = document.getElementById("solved-box");
    if (box) {
        box.style.display = "block";
    }
}

export function initChat({ endpoint, botName = "Bot", solvedCallback }) {
  const form = document.getElementById("challenge-form");
  const input = document.getElementById("input");
  const messagesDiv = document.getElementById("messages");

  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      form.requestSubmit();
    }
  });

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    const userInput = input.value.trim();
    if (!userInput) return;
    input.value = "";

    appendMessage("You", userInput, "user");

    appendTypingIndicator();
    const thinkingMessage = messagesDiv.lastChild;

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: userInput }),
      });

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
