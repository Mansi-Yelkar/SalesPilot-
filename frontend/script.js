/* =========================================================
   SalesPilot AI — script.js
   Handles chat, voice I/O, TTS, session management,
   lead/appointment actions, and CRM dashboard rendering.
   ========================================================= */

'use strict';

// ── Configuration ──────────────────────────────────────────
const API_BASE = '';            // Same origin — FastAPI serves both
const WELCOME  = 'Hello! Welcome to Fortivex AI. I\'m SalesPilot AI, your personal sales assistant. How can I help you today?';

// ── State ──────────────────────────────────────────────────
let sessionId     = null;
let sessionNumber = 0;
let turnCount     = 0;
let isListening   = false;
let isSpeaking    = false;
let recognition   = null;
let finalTranscript = '';
let voiceError = '';
let isSending = false;
let leadChartInst = null;
let sentChartInst = null;

// ── DOM references ─────────────────────────────────────────
const chatMessages   = document.getElementById('chat-messages');
const chatInput      = document.getElementById('chat-input');
const btnSend        = document.getElementById('btn-send');
const btnMic         = document.getElementById('btn-mic');
const micIcon        = document.getElementById('mic-icon');
const voiceStatusBar = document.getElementById('voice-status-bar');
const langSelect     = document.getElementById('lang-select');
const sessionDisplay = document.getElementById('session-id-display');
const turnCounter    = document.getElementById('turn-counter');
const leadBadge      = document.getElementById('lead-category-badge');
const sentimentDisp  = document.getElementById('sentiment-display');
const btnNewSession  = document.getElementById('btn-new-session');
const btnSaveLead    = document.getElementById('btn-save-lead');
const btnSummarise   = document.getElementById('btn-summarise');
const summaryCard    = document.getElementById('summary-card');
const summaryText    = document.getElementById('summary-text');
const btnBookAppt    = document.getElementById('btn-book-appt');
const apptStatus     = document.getElementById('appt-status');
const toast          = document.getElementById('toast');
const tabChat        = document.getElementById('tab-chat');
const tabCrm         = document.getElementById('tab-crm');
const panelChat      = document.getElementById('panel-chat');
const panelCrm       = document.getElementById('panel-crm');
const btnRefreshCrm  = document.getElementById('btn-refresh-crm');

// ═══════════════════════════════════════════════════════════
// INITIALISATION
// ═══════════════════════════════════════════════════════════
function init() {
  startNewSession(false);
  setupVoiceInput();
  bindEvents();
}

function startNewSession(resetServer = true) {
  if (resetServer && sessionId) {
    fetch(`${API_BASE}/reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    }).catch(() => {});
  }

  sessionId  = generateUUID();
  sessionNumber += 1;
  turnCount  = 0;
  chatMessages.innerHTML = '';
  summaryCard.classList.add('hidden');
  summaryText.textContent = '';
  leadBadge.textContent   = '—';
  leadBadge.dataset.category = '';
  sentimentDisp.textContent  = '—';
  apptStatus.textContent     = '';
  sessionDisplay.textContent = `Session ${sessionNumber}`;
  turnCounter.textContent    = '0';

  appendMessage('ai', WELCOME);
}

function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
  });
}

// ═══════════════════════════════════════════════════════════
// CHAT
// ═══════════════════════════════════════════════════════════
async function sendMessage(text) {
  if (isSending) return;
  text = text.trim();
  if (!text) return;

  isSending = true;
  btnSend.disabled = true;
  chatInput.value = '';
  appendMessage('user', text);
  const typingId = appendTypingIndicator();

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        message:    text,
        language:   langSelect.value,
      }),
    });
    const data = await res.json();
    removeTypingIndicator(typingId);

    if (!res.ok) {
      const message = data.detail || 'Chat request failed. Please try again.';
      appendMessage('ai', message);
      showToast(message, 'error');
      return;
    }

    turnCount = data.turn_count;
    turnCounter.textContent = turnCount;
    appendMessage('ai', data.reply);
    speakText(data.reply);

    // Auto-refresh lead status after every 5 turns
    if (turnCount >= 3 && turnCount % 5 === 3) {
      await autoRefreshLead();
    }
  } catch (err) {
    removeTypingIndicator(typingId);
    appendMessage('ai', `I couldn't send that message: ${err.message}. Please try again.`);
    showToast('Error: ' + err.message, 'error');
  } finally {
    isSending = false;
    btnSend.disabled = false;
    if (voiceStatusBar.textContent === 'Sending recognized speech…') voiceStatusBar.textContent = '';
  }
}

function appendMessage(role, text) {
  const isAI = role === 'ai';
  const msgEl = document.createElement('div');
  msgEl.className = `msg msg-${isAI ? 'ai' : 'user'}`;

  const avatarEl = document.createElement('div');
  avatarEl.className = 'msg-avatar';
  avatarEl.textContent = isAI ? 'SP' : 'You';

  const bubbleEl = document.createElement('div');
  bubbleEl.className = 'msg-bubble';
  bubbleEl.textContent = text;

  msgEl.appendChild(avatarEl);
  msgEl.appendChild(bubbleEl);
  chatMessages.appendChild(msgEl);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return msgEl;
}

function appendTypingIndicator() {
  const id = 'typing-' + Date.now();
  const msgEl = document.createElement('div');
  msgEl.className = 'msg msg-ai';
  msgEl.id = id;

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = 'SP';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';

  const indicator = document.createElement('div');
  indicator.className = 'typing-indicator';
  for (let i = 0; i < 3; i++) {
    const dot = document.createElement('div');
    dot.className = 'typing-dot';
    indicator.appendChild(dot);
  }
  bubble.appendChild(indicator);
  msgEl.appendChild(avatar);
  msgEl.appendChild(bubble);
  chatMessages.appendChild(msgEl);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// ═══════════════════════════════════════════════════════════
// VOICE I/O
// ═══════════════════════════════════════════════════════════
function setupVoiceInput() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    btnMic.title = 'Speech recognition not supported in this browser. Use text input.';
    btnMic.disabled = true;
    voiceStatusBar.textContent = 'Voice recognition is not available in this browser. Open this page in Chrome or Edge, or type your message.';
    return;
  }
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = 'en-US';

  recognition.onstart = () => {
    isListening = true;
    finalTranscript = '';
    voiceError = '';
    btnMic.classList.add('listening');
    voiceStatusBar.textContent = '🎙 Listening…';
  };

  recognition.onresult = (e) => {
    let interim = '';
    let final   = '';
    for (const result of e.results) {
      if (result.isFinal) final += result[0].transcript;
      else interim += result[0].transcript;
    }
    const text = final || interim;
    if (text) {
      finalTranscript = text.trim();
      chatInput.value = finalTranscript;
      voiceStatusBar.textContent = interim ? `🎙 ${interim}` : `✅ "${final}"`;
    }
  };

  recognition.onend = () => {
    isListening = false;
    btnMic.classList.remove('listening');
    const finalText = (finalTranscript || chatInput.value || '').trim();
    if (voiceError) {
      setTimeout(() => { voiceStatusBar.textContent = ''; }, 5000);
    } else if (finalText) {
      voiceStatusBar.textContent = 'Sending recognized speech…';
      setTimeout(() => { voiceStatusBar.textContent = ''; }, 2000);
      sendMessage(finalText);
    } else {
      voiceStatusBar.textContent = 'No speech was recognized. Try again or type your message.';
      setTimeout(() => { voiceStatusBar.textContent = ''; }, 4000);
    }
  };

  recognition.onerror = (e) => {
    isListening = false;
    voiceError = e.error || 'unknown';
    btnMic.classList.remove('listening');
    voiceStatusBar.textContent = e.error === 'no-speech'
      ? 'No speech detected. Try again.'
      : `Voice input failed (${e.error}). Check microphone permission or type your message.`;
    if (e.error !== 'no-speech') showToast('Voice input failed: ' + e.error, 'error');
    setTimeout(() => { voiceStatusBar.textContent = ''; }, 5000);
  };
}

function toggleListening() {
  if (!recognition) return;
  if (isListening) {
    recognition.stop();
  } else {
    chatInput.value = '';
    recognition.lang = langSelect.value === 'Hindi' ? 'hi-IN'
      : langSelect.value === 'Spanish' ? 'es-ES'
      : langSelect.value === 'French'  ? 'fr-FR'
      : langSelect.value === 'German'  ? 'de-DE'
      : langSelect.value === 'Marathi' ? 'mr-IN'
      : langSelect.value === 'Tamil'   ? 'ta-IN'
      : 'en-US';
    try {
      recognition.start();
    } catch (err) {
      showToast('Could not start voice input. Please try again or type your message.', 'error');
    }
  }
}

function speakText(text) {
  if (!window.speechSynthesis) return;
  speechSynthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = langSelect.value === 'Hindi'   ? 'hi-IN'
    : langSelect.value === 'Spanish' ? 'es-ES'
    : langSelect.value === 'French'  ? 'fr-FR'
    : langSelect.value === 'German'  ? 'de-DE'
    : langSelect.value === 'Marathi' ? 'mr-IN'
    : langSelect.value === 'Tamil'   ? 'ta-IN'
    : 'en-US';
  utter.rate  = 1.0;
  utter.pitch = 1.0;
  speechSynthesis.speak(utter);
}

// ═══════════════════════════════════════════════════════════
// LEAD & SUMMARY ACTIONS
// ═══════════════════════════════════════════════════════════
async function autoRefreshLead() {
  try {
    const res  = await fetch(`${API_BASE}/leads`);
    const leads = await res.json();
    const mine  = leads.find(l => l.session_id === sessionId);
    if (mine) updateLeadUI(mine);
  } catch {}
}

async function saveLead() {
  try {
    const res  = await fetch(`${API_BASE}/leads`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Save error');
    // data.lead_data has the extracted lead fields
    updateLeadUI(data.lead_data);
    showToast('Lead saved to CRM ✅', 'success');
  } catch (err) {
    showToast('Could not save lead: ' + err.message, 'error');
  }
}

function updateLeadUI(lead) {
  const cat  = lead.lead_category || '—';
  const sent = lead.sentiment     || '—';
  leadBadge.textContent = cat;
  leadBadge.dataset.category = cat;
  sentimentDisp.textContent  = sent;
}

async function generateSummary() {
  try {
    const res  = await fetch(`${API_BASE}/summary`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Summary error');
    summaryText.textContent = data.summary;
    summaryCard.classList.remove('hidden');
  } catch (err) {
    showToast('Summary error: ' + err.message, 'error');
  }
}

async function bookAppointment() {
  const name = document.getElementById('appt-name').value.trim();
  const date = document.getElementById('appt-date').value;
  const time = document.getElementById('appt-time').value;
  const req  = document.getElementById('appt-req').value.trim();

  apptStatus.style.color = 'var(--clr-muted)';
  apptStatus.textContent = 'Saving…';

  try {
    const res = await fetch(`${API_BASE}/appointments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id:     sessionId,
        customer_name:  name || null,
        preferred_date: date || null,
        preferred_time: time || null,
        requirement:    req  || null,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Booking error');
    apptStatus.style.color = 'var(--clr-positive)';
    apptStatus.textContent = '✅ ' + data.message;
    showToast('Appointment request saved!', 'success');
  } catch (err) {
    apptStatus.style.color = 'var(--clr-negative)';
    apptStatus.textContent = '❌ ' + err.message;
  }
}

// ═══════════════════════════════════════════════════════════
// CRM DASHBOARD
// ═══════════════════════════════════════════════════════════
async function loadDashboard() {
  await Promise.all([loadLeads(), loadAppointments(), loadInsights()]);
}

async function loadLeads() {
  const tbody = document.getElementById('leads-tbody');
  try {
    const res   = await fetch(`${API_BASE}/leads`);
    const leads = await res.json();
    if (!leads.length) {
      tbody.innerHTML = '<tr><td colspan="9" class="empty-row">No leads yet.</td></tr>';
      return;
    }
    tbody.innerHTML = leads.map((l, i) => `
      <tr>
        <td>${i + 1}</td>
        <td>${esc(l.customer_name  || '—')}</td>
        <td>${esc(l.business_type  || '—')}</td>
        <td>${esc(l.requirement    || '—')}</td>
        <td>${esc(l.budget         || '—')}</td>
        <td><span class="chip chip-${l.lead_category}">${esc(l.lead_category || '—')}</span></td>
        <td><span class="chip chip-${l.sentiment}">${esc(l.sentiment || '—')}</span></td>
        <td style="font-size:0.78rem;color:var(--clr-muted);max-width:200px;white-space:normal">${esc(l.summary || '—')}</td>
        <td style="white-space:nowrap;font-size:0.78rem;color:var(--clr-muted)">${formatDate(l.created_at)}</td>
      </tr>`).join('');
  } catch {
    tbody.innerHTML = '<tr><td colspan="9" class="empty-row">Failed to load leads.</td></tr>';
  }
}

async function loadAppointments() {
  const tbody = document.getElementById('appts-tbody');
  try {
    const res   = await fetch(`${API_BASE}/appointments`);
    const appts = await res.json();
    if (!appts.length) {
      tbody.innerHTML = '<tr><td colspan="7" class="empty-row">No appointments yet.</td></tr>';
      return;
    }
    tbody.innerHTML = appts.map((a, i) => `
      <tr>
        <td>${i + 1}</td>
        <td>${esc(a.customer_name   || '—')}</td>
        <td>${esc(a.preferred_date  || '—')}</td>
        <td>${esc(a.preferred_time  || '—')}</td>
        <td>${esc(a.requirement     || '—')}</td>
        <td><span class="chip chip-Warm">${esc(a.status)}</span></td>
        <td style="white-space:nowrap;font-size:0.78rem;color:var(--clr-muted)">${formatDate(a.created_at)}</td>
      </tr>`).join('');
  } catch {
    tbody.innerHTML = '<tr><td colspan="7" class="empty-row">Failed to load appointments.</td></tr>';
  }
}

async function loadInsights() {
  try {
    const res  = await fetch(`${API_BASE}/insights`);
    const data = await res.json();

    document.getElementById('kpi-total-leads').textContent = data.total_leads;
    document.getElementById('kpi-hot-leads').textContent   = data.lead_categories?.Hot || 0;
    document.getElementById('kpi-total-appts').textContent = data.total_appointments;
    const total = data.total_leads || 1;
    const positivePct = Math.round(((data.sentiments?.Positive || 0) / total) * 100);
    document.getElementById('kpi-positive-pct').textContent = positivePct + '%';

    renderLeadChart(data.lead_categories);
    renderSentimentChart(data.sentiments);
  } catch {}
}

function renderLeadChart(cats) {
  const canvas = document.getElementById('chart-lead-category');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (leadChartInst) leadChartInst.destroy();

  const hot = Number(cats?.Hot || 0);
  const warm = Number(cats?.Warm || 0);
  const cold = Number(cats?.Cold || 0);
  const hasData = (hot + warm + cold) > 0;

  leadChartInst = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: hasData ? ['Hot', 'Warm', 'Cold'] : ['No Leads Yet'],
      datasets: [{
        data: hasData ? [hot, warm, cold] : [1],
        backgroundColor: hasData
          ? ['hsla(10,90%,60%,0.85)', 'hsla(38,92%,55%,0.85)', 'hsla(205,80%,60%,0.85)']
          : ['hsla(230,15%,28%,0.5)'],
        borderColor: hasData
          ? ['hsl(10,90%,60%)', 'hsl(38,92%,55%)', 'hsl(205,80%,60%)']
          : ['hsl(230,15%,35%)'],
        borderWidth: 2,
        hoverOffset: hasData ? 6 : 0,
      }],
    },
    options: chartOptions('Lead Category', hasData),
  });
}

function renderSentimentChart(sents) {
  const canvas = document.getElementById('chart-sentiment');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (sentChartInst) sentChartInst.destroy();

  const pos = Number(sents?.Positive || 0);
  const neu = Number(sents?.Neutral || 0);
  const neg = Number(sents?.Negative || 0);
  const hasData = (pos + neu + neg) > 0;

  sentChartInst = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: hasData ? ['Positive', 'Neutral', 'Negative'] : ['No Sentiment Yet'],
      datasets: [{
        data: hasData ? [pos, neu, neg] : [1],
        backgroundColor: hasData
          ? ['hsla(142,60%,50%,0.85)', 'hsla(220,15%,60%,0.85)', 'hsla(355,75%,60%,0.85)']
          : ['hsla(230,15%,28%,0.5)'],
        borderColor: hasData
          ? ['hsl(142,60%,50%)', 'hsl(220,15%,60%)', 'hsl(355,75%,60%)']
          : ['hsl(230,15%,35%)'],
        borderWidth: 2,
        hoverOffset: hasData ? 6 : 0,
      }],
    },
    options: chartOptions('Sentiment', hasData),
  });
}

function chartOptions(title, hasData = true) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '70%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: 'hsl(220,15%,65%)',
          font:  { family: 'Inter', size: 12 },
          padding: 14,
          boxWidth: 12,
          boxHeight: 12,
          borderRadius: 4,
          useBorderRadius: true,
        },
      },
      tooltip: {
        enabled: hasData,
        backgroundColor: 'hsl(230,16%,16%)',
        titleColor:      'hsl(220,20%,92%)',
        bodyColor:       'hsl(220,15%,70%)',
        borderColor:     'hsl(230,20%,25%)',
        borderWidth: 1,
        callbacks: {
          label: ctx => ` ${ctx.label}: ${ctx.parsed}`,
        },
      },
    },
  };
}

// ═══════════════════════════════════════════════════════════
// TOAST
// ═══════════════════════════════════════════════════════════
let toastTimer = null;
function showToast(msg, type = '') {
  toast.textContent = msg;
  toast.className   = 'toast show' + (type ? ' toast-' + type : '');
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 3200);
}

// ═══════════════════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════════════════
function esc(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function formatDate(isoStr) {
  if (!isoStr) return '—';
  try {
    return new Date(isoStr + 'Z').toLocaleString('en-IN', {
      day:    '2-digit',
      month:  'short',
      year:   'numeric',
      hour:   '2-digit',
      minute: '2-digit',
    });
  } catch {
    return isoStr;
  }
}

// ═══════════════════════════════════════════════════════════
// EVENT BINDINGS
// ═══════════════════════════════════════════════════════════
function bindEvents() {
  btnSend.addEventListener('click', () => sendMessage(chatInput.value));
  chatInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(chatInput.value); }
  });
  btnMic.addEventListener('click', toggleListening);
  btnNewSession.addEventListener('click', () => {
    if (confirm('Start a new conversation? The current session will be reset.')) {
      startNewSession(true);
    }
  });
  btnSaveLead.addEventListener('click', saveLead);
  btnSummarise.addEventListener('click', generateSummary);
  btnBookAppt.addEventListener('click', bookAppointment);

  // Tabs
  tabChat.addEventListener('click', () => switchTab('chat'));
  tabCrm.addEventListener('click',  () => { switchTab('crm'); loadDashboard(); });
  btnRefreshCrm.addEventListener('click', loadDashboard);
}

function switchTab(tab) {
  if (tab === 'chat') {
    panelChat.classList.remove('hidden');
    panelCrm.classList.add('hidden');
    tabChat.classList.add('active');
    tabCrm.classList.remove('active');
    tabChat.setAttribute('aria-selected', 'true');
    tabCrm.setAttribute('aria-selected', 'false');
  } else {
    panelCrm.classList.remove('hidden');
    panelChat.classList.add('hidden');
    tabCrm.classList.add('active');
    tabChat.classList.remove('active');
    tabCrm.setAttribute('aria-selected', 'true');
    tabChat.setAttribute('aria-selected', 'false');
  }
}

// ── Boot ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', init);
