export function showSolvedBox(challengeId) {
    // Update sidebar as before
    if (challengeId) {
        const li = document.getElementById(`challenge-${challengeId}`);
        if (li) {
            li.classList.add("completed");
        }
    }

    // Create overlay elements
    let overlay = document.getElementById("solved-overlay");
    if (!overlay) {
        overlay = document.createElement("div");
        overlay.id = "solved-overlay";

        // Blue centered container
        overlay.innerHTML = `
            <div class="solved-content">
                <h2>Challenge solved!</h2>
                <img src="/static/images/goat-congrats.gif" alt="Celebration Goat" class="solved-goat"/>
                <button class="solved-ok-btn">OK</button>
            </div>
        `;
        document.body.appendChild(overlay);

        // Close button handler
        overlay.querySelector(".solved-ok-btn").onclick = () => {
            overlay.style.display = "none";
        };
    }

    // Show the overlay
    overlay.style.display = "flex";
}

function showWaitingModal() {
    // Create overlay elements
    let overlay = document.getElementById("waiting-overlay");
    if (!overlay) {
        overlay = document.createElement("div");
        overlay.id = "waiting-overlay";

        // Blue centered container
        overlay.innerHTML = `
            <div class="solved-content">
                <h2>Please wait... our goats are chewing through the data grass</h2>
                <img src="/static/images/goat-base.gif" alt="The Goat is waiting" class="waiting-goat"/>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    // Show the overlay
    overlay.style.display = "flex";
}

function hideWaitingModal() {
    let overlay = document.getElementById("waiting-overlay");
    if (overlay) {
      overlay.style.display = "none";
    }
}

export function initModelSelector() {
  let isProcessing = false;
  const select = document.getElementById("model-select");
  select.addEventListener("change", async function(e) {
    const selectedModel = e.target.value.trim(); // Get the selected value
    if (isProcessing) return; // Block if processing
    isProcessing = true;
    select.disabled = true;

    try {
      showWaitingModal()
      const res = await fetch("/api/set_model", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model_name: selectedModel }),
      });

      if (res.status === 429) {
        await res.json();
        isProcessing = true;
        select.disabled = true;
        return;
      }
    } catch {
        isProcessing = true;
        select.disabled = true;
    } finally {
      hideWaitingModal();
      select.disabled = false;
      isProcessing = false;
    }
  })
}

/* chatbot - common to most challenges */
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
          showSolvedBox(endpoint.split("/api/")[1]);
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

/* helper */
export async function fetchJson(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);
  return res.json();
}

/* A04 challenge */
export function renderReviews(goat, dataForGoat) {
  const list = document.getElementById("reviews-list");
  list.innerHTML = "";

  const items = Array.isArray(dataForGoat) ? dataForGoat : [];
  items.forEach(item => {
    const text = (typeof item === "object" && item !== null) ? item.text : String(item);

    const li = document.createElement("li");
    li.className = "review-item";

    const span = document.createElement("span");
    span.textContent = text;
    li.appendChild(span);

    // prepend to show newest reviews on top
    list.prepend(li);
  });
}

export async function loadReviewsFor(goat) {
  try {
    const data = await fetchJson("/a04_data_and_model_poisoning/get_reviews");
    const reviews = data[goat] || [];
    document.getElementById("reviews-title").textContent = goat + " Reviews";
    renderReviews(goat, reviews);
  } catch (err) {
    console.error("Error loading reviews", err);
    document.getElementById("reviews-title").textContent = "Error loading reviews";
    document.getElementById("reviews-list").innerHTML = "";
  }
}

export async function addReview(goat, reviewText) {
  if (!goat) throw new Error("Goat not selected");
  if (!reviewText.trim()) return;

  const res = await fetch("/a04_data_and_model_poisoning/add_review", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ review: reviewText, goat })
  });

  if (!res.ok) throw new Error("Add review failed");
  return loadReviewsFor(goat);
}

export async function resetReviews(selectedGoat) {
  try {
    const res = await fetch("/a04_data_and_model_poisoning/reset_reviews", { method: "POST" });
    const data = await res.json();
    if (!res.ok) throw new Error("Reset failed");
    const reviews = data.reviews[selectedGoat] || [];
    renderReviews(selectedGoat, reviews);
  } catch (err) {
    console.error("Reset failed", err);
    window.location.reload();
  }
}

/** === Recommendation Helper === **/
export async function getRecommendation(selectedGoat, selectedTags) {
  const recBtn = document.getElementById("get-recommendation-btn");
  const recBox = document.getElementById("recommendation-box");
  let isProcessing = false;

  if (isProcessing) return; // prevent double clicks

  if (!selectedGoat) {
    alert("Please select a goat first!");
    return;
  }

  // Lock UI
  isProcessing = true;
  recBtn.disabled = true;
  recBtn.textContent = "Processing...";
  recBtn.style.backgroundColor = "#888"; // disabled look

  // Show typing dots while waiting
  recBox.innerHTML = `<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>`;
  //recBox.innerHTML = `<img src="{{ url_for('static', filename='images/goat-chew.gif') }}" alt="Billy chewing..." class="chew-gif" />`;

  try {
    const res = await fetch("/api/a04-data-and-model-poisoning", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ selectedGoat, attributes: Array.from(selectedTags) })
    });

    if (res.ok) {
      const data = await res.json();
      recBox.textContent = `We recommend you purchase the: ${data.response}`;

      // check solved flag
      if (data.solved) {
        if (typeof showSolvedBox === "function") {
          showSolvedBox("a04-data-and-model-poisoning");
        }
      }

    } else {
      recBox.textContent = "Error: Failed to get recommendation";
    }
  } catch (err) {
    console.error("Recommendation failed", err);
    recBox.textContent = "Error: Failed to reach the goat 🐐";
  } finally {
    // Unlock UI
    isProcessing = false;
    recBtn.disabled = false;
    recBtn.textContent = "GET RECOMMENDATION";
    recBtn.style.backgroundColor = "#1f42f2"; // restore normal
  }
}

/* A08 challenge */
/* helper to post a bot message from outside initChat */
export function appendBotMessage(text, botName = "Billy the Goat") {
  const messagesDiv = document.getElementById("messages");
  if (!messagesDiv) return;

  const msg = document.createElement("div");
  msg.classList.add("message", "bot-message");

  const label = document.createElement("span");
  label.classList.add("sender-label");
  label.textContent = botName;
  msg.appendChild(label);

  const content = document.createElement("div");
  content.innerHTML = text.replace(/\n/g, "<br>");
  msg.appendChild(content);

  messagesDiv.appendChild(msg);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

export async function importVectors(fileInput) {
  const file = fileInput.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/a08_vector_embedding_weaknesses/import_vectors", {
      method: "POST",
      body: formData,
    });
        const text = await res.json();
    appendBotMessage(text.status);
  } catch (err) {
    console.error("Import failed", err);
    appendBotMessage("Error importing vectors");
  }

  fileInput.value = "";
}

export async function exportVectors() {
  try {
    const res = await fetch("/a08_vector_embedding_weaknesses/export_vectors");
    if (!res.ok) throw new Error("Export failed");

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "vectors.json";
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error("Export failed", err);
    appendBotMessage("Error exporting vectors");
  }
}

export async function resetVectors() {
  try {
    const res = await fetch("/a08_vector_embedding_weaknesses/reset_vectors");
    const text = await res.json();
    appendBotMessage(text.status);
  } catch (err) {
    console.error("Reset failed", err);
    appendBotMessage("Error resetting vectors");
  }
}

/* A09 challenge */
// Enable/disable process button
export function setProcessButtonState(processBtn, enabled) {
    processBtn.disabled = !enabled;
    processBtn.style.backgroundColor = enabled ? "#1f42f2" : "#888";
}

// Upload image
export async function uploadImage(fileInput, imagePreview, processBtn, outputBox) {
    if (!fileInput.files.length) return;

    const uploadedFile = fileInput.files[0];
    const reader = new FileReader();
    reader.onload = () => imagePreview.src = reader.result;
    reader.readAsDataURL(uploadedFile);

    setProcessButtonState(processBtn, false);
    outputBox.textContent = "Uploading image...";

    const formData = new FormData();
    formData.append("file", uploadedFile);

    try {
        const res = await fetch("/a09_misinformation/upload_image", {
            method: "POST",
            body: formData,
        });
        if (!res.ok) {
            outputBox.textContent = "Upload failed";
            return;
        }
        outputBox.textContent = "Image uploaded successfully!";
        setProcessButtonState(processBtn, true);
    } catch (err) {
        outputBox.textContent = "Error uploading image";
    }
}

// Process image
export async function processImage(processBtn, outputBox) {
    setProcessButtonState(processBtn, false);
    outputBox.textContent = "Processing image...";

    try {
        const res = await fetch("/api/a09_misinformation", { method: "POST" });
        if (!res.ok) {
            outputBox.textContent = "Processing failed";
            return;
        }

        const data = await res.json();
        outputBox.textContent = data.response || "No response";

        if (data.solved && typeof showSolvedBox === "function") {
            showSolvedBox("a09-misinformation");
        }
    } catch (err) {
        console.error("Processing error", err);
        outputBox.textContent = "Error processing image";
    } finally {
        setProcessButtonState(processBtn, true);
    }
}

// Download image
export function downloadImage(url) {
    const link = document.createElement("a");
    link.href = url;
    link.download = "goat.png";
    document.body.appendChild(link);
    link.click();
    link.remove();
}
