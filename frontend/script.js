let BACKEND_URL = "http://localhost:5000";
let SESSION_ID = "default";

// Attempt to load configurations from frontend/.env if served via HTTP server
async function loadFrontendEnv() {
  try {
    const res = await fetch(".env");
    if (res.ok) {
      const text = await res.text();
      text.split("\n").forEach((line) => {
        const trimmed = line.trim();
        if (trimmed && !trimmed.startsWith("#") && trimmed.includes("=")) {
          const [key, ...vals] = trimmed.split("=");
          const val = vals.join("=").trim().replace(/^["']|["']$/g, "");
          if (key === "BACKEND_URL" && val) BACKEND_URL = val;
          if (key === "DEFAULT_SESSION_ID" && val) SESSION_ID = val;
        }
      });
    }
  } catch (e) {
    // If opened via file:// protocol or .env not directly readable, defaults are used
  }
}

const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const clearBtn = document.getElementById("clear-btn");
const statusDot = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");
const dbBadge = document.getElementById("db-badge");

// Auto-expand textarea
userInput.addEventListener("input", () => {
  userInput.style.height = "auto";
  userInput.style.height = Math.min(userInput.scrollHeight, 120) + "px";
});

// Append a message bubble
function appendMessage(text, sender = "bot", isError = false) {
  const msgDiv = document.createElement("div");
  msgDiv.className = `message ${sender}${isError ? " error" : ""}`;
  
  const contentDiv = document.createElement("div");
  contentDiv.className = "message-content";
  contentDiv.textContent = text;
  
  msgDiv.appendChild(contentDiv);
  chatMessages.appendChild(msgDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return msgDiv;
}

// Show/hide typing indicator
function showTypingIndicator() {
  const typingDiv = document.createElement("div");
  typingDiv.className = "message bot";
  typingDiv.id = "typing-indicator";
  typingDiv.innerHTML = `
    <div class="message-content">
      <span class="typing-dots">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </span>
    </div>
  `;
  chatMessages.appendChild(typingDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
  const indicator = document.getElementById("typing-indicator");
  if (indicator) indicator.remove();
}

// Check backend and database status
async function checkBackendStatus() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/health`, { method: "GET" });
    if (res.ok) {
      const data = await res.json();
      statusDot.className = "status-dot online";
      statusText.textContent = "Backend Online";

      if (data.supabase_connected) {
        dbBadge.className = "db-badge supabase";
        dbBadge.textContent = "Supabase DB";
      } else {
        dbBadge.className = "db-badge memory";
        dbBadge.textContent = "In-Memory DB";
      }
      return true;
    }
  } catch (err) {
    statusDot.className = "status-dot offline";
    statusText.textContent = "Backend Offline";
    dbBadge.className = "db-badge";
    dbBadge.textContent = "DB: unreachable";
    return false;
  }
}

// Load conversation history from backend (Supabase)
async function loadHistory() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/history?session_id=${encodeURIComponent(SESSION_ID)}`, { method: "GET" });
    if (res.ok) {
      const data = await res.json();
      chatMessages.innerHTML = "";

      if (data.messages && data.messages.length > 0) {
        data.messages.forEach((msg) => {
          const sender = msg.role === "user" ? "user" : "bot";
          appendMessage(msg.content, sender);
        });
      } else {
        appendMessage("Hello! I am your AI assistant powered by Gemini and Supabase. Ask me anything!", "bot");
      }
    }
  } catch (e) {
    chatMessages.innerHTML = "";
    appendMessage("Hello! I am your AI assistant powered by Gemini. Ask me anything!", "bot");
  }
}

// Handle message submission
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = userInput.value.trim();
  if (!text) return;

  appendMessage(text, "user");
  userInput.value = "";
  userInput.style.height = "auto";
  userInput.disabled = true;
  sendBtn.disabled = true;

  showTypingIndicator();

  try {
    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, session_id: SESSION_ID })
    });

    const data = await response.json();
    removeTypingIndicator();

    if (!response.ok) {
      appendMessage(data.error || "An error occurred while contacting backend.", "bot", true);
    } else {
      appendMessage(data.reply, "bot");
    }
  } catch (error) {
    removeTypingIndicator();
    appendMessage(
      "Could not reach backend server at http://localhost:5000. Make sure `python backend/server.py` is running.",
      "bot",
      true
    );
  } finally {
    userInput.disabled = false;
    sendBtn.disabled = false;
    userInput.focus();
  }
});

// Enter sends, Shift+Enter adds newline
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    chatForm.dispatchEvent(new Event("submit"));
  }
});

// Clear conversation
clearBtn.addEventListener("click", async () => {
  try {
    await fetch(`${BACKEND_URL}/api/reset`, { method: "POST" });
  } catch (e) {}

  chatMessages.innerHTML = "";
  appendMessage("Conversation cleared! Start a new topic.", "bot");
});

// Initial load
(async () => {
  await loadFrontendEnv();
  await checkBackendStatus();
  await loadHistory();
  setInterval(checkBackendStatus, 8000);
})();
