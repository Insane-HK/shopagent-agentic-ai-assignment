const form       = document.getElementById('chatForm');
const input      = document.getElementById('questionInput');
const askBtn     = document.getElementById('askBtn');
const askLabel   = askBtn.querySelector('.ask-label');
const askSpinner = document.getElementById('askSpinner');
const messages   = document.getElementById('messages');
const welcome    = document.getElementById('welcomeScreen');
const historyList= document.getElementById('historyList');
const clearBtn   = document.getElementById('clearBtn');
const charCount  = document.getElementById('charCount');
const menuToggle = document.getElementById('menuToggle');
const themeToggle= document.getElementById('themeToggle');
const sidebar    = document.getElementById('sidebar');
const newChatBtn = document.getElementById('newChatBtn');

let chats = [];
let activeChatId = null;

// Initialize
try {
  chats = JSON.parse(localStorage.getItem('shopagent_conversations') || '[]');
} catch (e) {
  chats = [];
}

if (chats.length === 0) {
  createNewChat();
} else {
  activeChatId = chats[0].id;
  loadActiveChat();
  renderSidebar();
}

// ── auto-resize textarea ──────────────────────────────────
input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = Math.min(input.scrollHeight, 120) + 'px';
  charCount.textContent = `${input.value.length} / 500`;
});

// ── enter to submit (shift+enter = newline) ───────────────
input.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (!askBtn.disabled) form.requestSubmit();
  }
});

// ── sidebar toggle (all screens) ────────────────────────
const isMobile = () => window.innerWidth <= 680;
menuToggle.addEventListener('click', () => {
  if (isMobile()) {
    sidebar.classList.toggle('open');
    sidebar.classList.remove('collapsed');
  } else {
    sidebar.classList.toggle('collapsed');
  }
});
document.addEventListener('click', e => {
  if (isMobile() && !sidebar.contains(e.target) && !menuToggle.contains(e.target))
    sidebar.classList.remove('open');
});

// ── dark mode toggle ──────────────────────────────────────
const savedTheme = localStorage.getItem('shopagent_theme');
if (savedTheme === 'dark') document.body.classList.add('dark-mode');

themeToggle.addEventListener('click', () => {
  document.body.classList.toggle('dark-mode');
  const isDark = document.body.classList.contains('dark-mode');
  localStorage.setItem('shopagent_theme', isDark ? 'dark' : 'light');
});

// ── suggestion chips ──────────────────────────────────────
document.querySelectorAll('.suggestion-chip').forEach(btn => {
  btn.addEventListener('click', () => {
    input.value = btn.dataset.q;
    input.dispatchEvent(new Event('input'));
    input.focus();
    form.requestSubmit();
  });
});

// ── new chat button ───────────────────────────────────────
newChatBtn.addEventListener('click', () => {
  createNewChat();
});

// ── clear history ─────────────────────────────────────────
clearBtn.addEventListener('click', () => {
  chats = [];
  localStorage.removeItem('shopagent_conversations');
  createNewChat();
});

// ── form submit ───────────────────────────────────────────
form.addEventListener('submit', async e => {
  e.preventDefault();
  const q = input.value.trim();
  if (!q) return;

  const chat = chats.find(c => c.id === activeChatId);
  if (!chat) return;

  hideWelcome();
  appendUserMsg(q);
  const typingEl = appendTyping();
  setLoading(true);

  input.value = '';
  input.style.height = 'auto';
  charCount.textContent = '0 / 500';
  
  // Save to active chat state
  chat.uiMessages.push({ type: 'user', text: q });
  chat.chatHistory.push({ role: 'user', text: q });
  
  // Set title if it was "New Chat"
  if (chat.title === 'New Chat' || chat.chatHistory.length === 1) {
    chat.title = q.length > 38 ? q.slice(0, 38) + '…' : q;
    renderSidebar();
  }
  saveChats();

  try {
    const resp = await fetch('api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
          question: q,
          history: chat.chatHistory.slice(0, -1)
      }),
    });

    typingEl.remove();

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: resp.statusText }));
      appendAgentMsg(q, err.detail || 'Something went wrong.', [], 0, true);
      
      // Remove from state on error
      chat.chatHistory.pop();
      chat.uiMessages.pop();
      saveChats();
      return;
    }

    const data = await resp.json();
    appendAgentMsg(q, data.answer, data.trace || [], data.duration_ms);
    
    // Save response to active chat state
    chat.chatHistory.push({ role: 'assistant', text: data.answer });
    chat.uiMessages.push({ 
      type: 'agent', 
      text: data.answer, 
      trace: data.trace || [], 
      ms: data.duration_ms 
    });
    saveChats();
  } catch (err) {
    typingEl.remove();
    appendAgentMsg(q, 'Network error — please try again.', [], 0, true);
    chat.chatHistory.pop();
    chat.uiMessages.pop();
    saveChats();
  } finally {
    setLoading(false);
    input.focus();
  }
});

// ── helpers ───────────────────────────────────────────────
function hideWelcome() {
  if (welcome) welcome.style.display = 'none';
}

function setLoading(on) {
  askBtn.disabled = on;
  askLabel.hidden = on;
  askSpinner.hidden = !on;
}

function appendUserMsg(text) {
  const block = el('div', 'msg-block user-block');
  const meta  = el('div', 'msg-meta');
  meta.innerHTML = `<span class="msg-role user">You</span>`;
  const card = el('div', 'msg-card user-card');
  card.textContent = text;
  block.append(meta, card);
  messages.append(block);
  scrollDown();
}

function appendAgentMsg(q, text, trace, ms, isError = false) {
  const block = el('div', 'msg-block agent-block');

  const meta = el('div', 'msg-meta');
  meta.innerHTML = `<span class="msg-role agent">ShopAgent</span>`;
  if (ms) {
    const dur = el('span', 'duration-tag');
    dur.textContent = `${ms}ms`;
    meta.append(dur);
  }

  const card = el('div', isError ? 'msg-card error-card' : 'msg-card');
  
  // escape html to prevent XSS
  const escaped = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  // parse markdown bold **text** -> <strong>text</strong>
  card.innerHTML = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  block.append(meta, card);

  // tool trace section
  if (trace && trace.length) {
    const toggleBtn = el('button', 'trace-toggle');
    toggleBtn.innerHTML = `<span class="arrow">▶</span> ${trace.length} tool call${trace.length > 1 ? 's' : ''}`;

    const panel = el('div', 'trace-panel');
    trace.forEach(t => {
      const item = el('div', 'trace-item');
      item.innerHTML =
        `<span class="trace-tool-name">${t.tool}</span>` +
        `<br><span class="trace-key">in: </span><span class="trace-val">${JSON.stringify(t.input)}</span>` +
        `<br><span class="trace-key">out: </span><span class="trace-val">${JSON.stringify(t.output).slice(0, 200)}</span>`;
      panel.append(item);
    });

    toggleBtn.addEventListener('click', () => {
      toggleBtn.classList.toggle('open');
      panel.classList.toggle('visible');
    });

    block.append(toggleBtn, panel);
  }

  messages.append(block);
  scrollDown();
}

function appendTyping() {
  const block = el('div', 'msg-block');
  const meta  = el('div', 'msg-meta');
  meta.innerHTML = `<span class="msg-role agent">ShopAgent</span>`;
  const card = el('div', 'msg-card typing-card');
  [0,1,2].forEach(() => card.append(el('div', 'typing-dot')));
  block.append(meta, card);
  messages.append(block);
  scrollDown();
  return block;
}

function scrollDown() {
  messages.scrollIntoView ? null : null;
  const conv = document.getElementById('conversation');
  conv.scrollTop = conv.scrollHeight;
}

function el(tag, cls) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  return e;
}

// ── history sidebar ───────────────────────────────────────
function createNewChat() {
  const newChat = {
    id: 'chat_' + Date.now(),
    title: 'New Chat',
    chatHistory: [],
    uiMessages: []
  };
  chats.unshift(newChat);
  activeChatId = newChat.id;
  saveChats();
  loadActiveChat();
  renderSidebar();
}

function saveChats() {
  localStorage.setItem('shopagent_conversations', JSON.stringify(chats));
}

function loadActiveChat() {
  messages.innerHTML = '';
  const chat = chats.find(c => c.id === activeChatId);
  if (!chat) return;

  if (chat.uiMessages.length === 0) {
    welcome.style.display = '';
  } else {
    hideWelcome();
    chat.uiMessages.forEach(msg => {
      if (msg.type === 'user') {
        appendUserMsg(msg.text);
      } else {
        appendAgentMsg(null, msg.text, msg.trace, msg.ms, msg.isError);
      }
    });
  }
  scrollDown();
}

function renderSidebar() {
  historyList.innerHTML = '';
  if (!chats.length) {
    const li = el('li', 'history-empty');
    li.textContent = 'No conversations yet';
    historyList.append(li);
    return;
  }
  
  chats.forEach(chat => {
    const li = el('li', chat.id === activeChatId ? 'history-item active' : 'history-item');
    li.textContent = chat.title || 'New Chat';
    li.title = chat.title || 'New Chat';
    li.addEventListener('click', () => {
      activeChatId = chat.id;
      loadActiveChat();
      renderSidebar();
    });
    historyList.append(li);
  });
}
