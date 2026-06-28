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
const sidebar    = document.getElementById('sidebar');

let history = JSON.parse(sessionStorage.getItem('shopagent_history') || '[]');
let chatHistory = []; // full conversation context

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

// ── sidebar toggle (mobile) ───────────────────────────────
menuToggle.addEventListener('click', () => sidebar.classList.toggle('open'));
document.addEventListener('click', e => {
  if (!sidebar.contains(e.target) && !menuToggle.contains(e.target))
    sidebar.classList.remove('open');
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

// ── clear history ─────────────────────────────────────────
clearBtn.addEventListener('click', () => {
  history = [];
  chatHistory = [];
  sessionStorage.removeItem('shopagent_history');
  renderHistory();
  messages.innerHTML = '';
  welcome.style.display = '';
});

// ── form submit ───────────────────────────────────────────
form.addEventListener('submit', async e => {
  e.preventDefault();
  const q = input.value.trim();
  if (!q) return;

  hideWelcome();
  appendUserMsg(q);
  const typingEl = appendTyping();
  setLoading(true);

  input.value = '';
  input.style.height = 'auto';
  charCount.textContent = '0 / 500';
  
  chatHistory.push({ role: 'user', text: q });

  try {
    const resp = await fetch('api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
          question: q,
          history: chatHistory.slice(0, -1)
      }),
    });

    typingEl.remove();

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: resp.statusText }));
      appendAgentMsg(null, err.detail || 'Something went wrong.', [], 0);
      chatHistory.pop(); // remove user question on error
      return;
    }

    const data = await resp.json();
    appendAgentMsg(q, data.answer, data.trace || [], data.duration_ms);
    
    // Only add the very first question of the conversation to the sidebar history
    if (chatHistory.length === 1) {
      addToHistory(q);
    }
    
    chatHistory.push({ role: 'assistant', text: data.answer });
  } catch (err) {
    typingEl.remove();
    appendAgentMsg(null, 'Network error — please try again.', [], 0, true);
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
  const block = el('div', 'msg-block');
  const meta  = el('div', 'msg-meta');
  meta.innerHTML = `<span class="msg-role user">You</span>`;
  const card = el('div', 'msg-card user-card');
  card.textContent = text;
  block.append(meta, card);
  messages.append(block);
  scrollDown();
}

function appendAgentMsg(q, text, trace, ms, isError = false) {
  const block = el('div', 'msg-block');

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
function addToHistory(q) {
  const label = q.length > 38 ? q.slice(0, 38) + '…' : q;
  history.unshift(label);
  if (history.length > 20) history.pop();
  sessionStorage.setItem('shopagent_history', JSON.stringify(history));
  renderHistory();
}

function renderHistory() {
  historyList.innerHTML = '';
  if (!history.length) {
    const li = document.createElement('li');
    li.className = 'history-empty';
    li.textContent = 'No conversations yet';
    historyList.append(li);
    return;
  }
  history.forEach(q => {
    const li = document.createElement('li');
    li.textContent = q;
    li.title = q;
    li.addEventListener('click', () => {
      input.value = q;
      input.dispatchEvent(new Event('input'));
      input.focus();
    });
    historyList.append(li);
  });
}

renderHistory();
