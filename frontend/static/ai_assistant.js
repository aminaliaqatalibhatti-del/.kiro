/* ═══════════════════════════════════════════════════════════
   TripPilot AI — AI Assistant  (chat + inline advisor)
   Depends on: main.js (esc, fmt, showToast, App)
   ═══════════════════════════════════════════════════════════ */

'use strict';

// ── Module state ───────────────────────────────────────────────
const Assistant = {
  open:        false,
  context:     null,      // current trip context fed by planner
  advisory:    null,      // full advisory report from backend
  msgHistory:  [],
  typing:      false,
};

const QUICK_CHIPS = [
  { label: '💰 Save money',        q: 'How can I reduce costs on this trip?' },
  { label: '🔄 Alternatives',       q: 'What are the best alternatives to my destination?' },
  { label: '🌧 Weather impact',     q: 'How does the weather affect my itinerary?' },
  { label: '📅 Best timing',        q: 'Is my travel timing good?' },
  { label: '🏨 Hotel advice',       q: 'Which hotel type suits my budget best?' },
  { label: '🍽 Food tips',          q: 'What are the best local food options?' },
  { label: '✈️ Pro tips',           q: 'What are the top tips for my destination?' },
];

// ── Bootstrap (called after plan is generated) ────────────────
function initAssistant(tripContext, plan) {
  Assistant.context = { ...tripContext, plan };
  _buildUI();
  _loadAdvisory(tripContext, plan);
}

// ── Build floating UI ─────────────────────────────────────────
function _buildUI() {
  // Remove existing instance
  document.getElementById('aiFab')?.remove();
  document.getElementById('aiPanel')?.remove();

  // FAB
  const fab = document.createElement('button');
  fab.id = 'aiFab';
  fab.className = 'ai-fab';
  fab.setAttribute('aria-label', 'Open AI Travel Assistant');
  fab.innerHTML = `🤖<span class="ai-fab-badge" id="aiBadge" style="display:none">!</span>`;
  fab.addEventListener('click', toggleAssistant);
  document.body.appendChild(fab);

  // Panel
  const panel = document.createElement('div');
  panel.id = 'aiPanel';
  panel.className = 'ai-panel';
  panel.innerHTML = `
    <div class="ai-panel-header">
      <div class="ai-panel-avatar">🤖</div>
      <div class="ai-panel-title">
        <div class="ai-panel-name">TripPilot Advisor</div>
        <div class="ai-panel-status">
          <span class="ai-status-dot"></span>
          <span>Active — analysing your trip</span>
        </div>
      </div>
      <button class="ai-panel-close" onclick="toggleAssistant()" aria-label="Close">✕</button>
    </div>

    <div class="ai-quick-chips" id="aiQuickChips">
      ${QUICK_CHIPS.map(c => `
        <button class="ai-quick-chip" onclick="sendQuickQuestion(${JSON.stringify(c.q)})">${c.label}</button>
      `).join('')}
    </div>

    <div class="ai-messages" id="aiMessages">
      <div class="ai-msg assistant">
        <div class="ai-msg-avatar">🤖</div>
        <div class="ai-msg-bubble">
          Hi! I'm analysing your trip plan right now. I'll have personalised insights ready in a moment — or ask me anything about your trip.
        </div>
      </div>
    </div>

    <div class="ai-input-area">
      <textarea
        class="ai-input"
        id="aiInput"
        placeholder="Ask me anything about your trip…"
        rows="1"
        onkeydown="handleChatKey(event)"
        oninput="autoResizeInput(this)"
      ></textarea>
      <button class="ai-send-btn" id="aiSendBtn" onclick="sendChatMessage()" aria-label="Send">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg>
      </button>
    </div>`;

  document.body.appendChild(panel);
}

// ── Toggle panel ───────────────────────────────────────────────
function toggleAssistant() {
  const panel = document.getElementById('aiPanel');
  const fab   = document.getElementById('aiFab');
  if (!panel) return;

  Assistant.open = !Assistant.open;
  panel.classList.toggle('open', Assistant.open);
  fab?.classList.toggle('open', Assistant.open);

  // Clear notification badge
  const badge = document.getElementById('aiBadge');
  if (badge) badge.style.display = 'none';

  if (Assistant.open) {
    setTimeout(() => document.getElementById('aiInput')?.focus(), 300);
  }
}

// ── Load advisory from backend ─────────────────────────────────
async function _loadAdvisory(tripContext, plan) {
  try {
    const payload = {
      destination:   tripContext.destination,
      days:          tripContext.days,
      budget:        tripContext.budget,
      travel_type:   tripContext.travel_type,
      travelers:     tripContext.travelers,
      interests:     tripContext.interests,
      accommodation: tripContext.accommodation,
      transport:     tripContext.transport,
      start_date:    tripContext.start_date,
      plan:          plan,
    };

    const res  = await fetch('/api/ai/advisory', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (data.status === 'success') {
      Assistant.advisory = data.advisory;
      _renderAdvisoryInline(data.advisory);
      _sendAdvisoryMessage(data.advisory.ai_summary);
      _showBadge();
    }
  } catch (err) {
    console.warn('Advisory load failed:', err);
  }
}

function _showBadge() {
  if (!Assistant.open) {
    const badge = document.getElementById('aiBadge');
    if (badge) badge.style.display = 'flex';
  }
}

// ── Render inline advisory cards in planner results ───────────
function _renderAdvisoryInline(advisory) {
  // 1. Summary panel at top of results
  const titleArea = document.getElementById('resTripTitle')?.closest('.results-header');
  if (titleArea && !document.getElementById('advisoryPanel')) {
    const panel = document.createElement('div');
    panel.id = 'advisoryPanel';
    panel.className = 'advisory-panel';
    panel.innerHTML = _buildAdvisoryPanelHTML(advisory);
    titleArea.insertAdjacentElement('afterend', panel);
  }

  // 2. Weather alerts above itinerary
  const itinContainer = document.getElementById('itineraryCards');
  if (itinContainer && advisory.weather_adjustments?.length) {
    const weatherAlerts = document.createElement('div');
    weatherAlerts.className = 'weather-alerts';
    weatherAlerts.innerHTML = advisory.weather_adjustments
      .filter(a => a.severity === 'high')
      .map(a => _buildWeatherAlertHTML(a)).join('');
    if (weatherAlerts.innerHTML) {
      itinContainer.insertAdjacentElement('beforebegin', weatherAlerts);
    }
  }

  // 3. Budget optimization tab injection
  const budgetTab = document.getElementById('tab-budget');
  if (budgetTab && advisory.budget_optimization?.length) {
    const opt = advisory.budget_optimization.filter(t => t.type !== 'summary');
    if (opt.length) {
      const optSection = document.createElement('div');
      optSection.innerHTML = `
        <div class="ai-insights-box" style="margin-top:20px">
          <div class="ai-insights-title">✨ AI Savings Opportunities</div>
          <div class="budget-opt-list">
            ${opt.map(t => `
              <div class="budget-opt-item">
                <div class="budget-opt-icon">${t.icon}</div>
                <div class="budget-opt-text">
                  <div class="budget-opt-cat">${t.category}</div>
                  <div class="budget-opt-msg">${esc(t.message)}</div>
                </div>
                ${t.saving > 0 ? `<div class="budget-opt-saving">Save $${t.saving}</div>` : ''}
              </div>`).join('')}
          </div>
        </div>`;
      budgetTab.appendChild(optSection);
    }
  }

  // 4. Alternatives in a new "AI Advisor" tab (inject dynamically)
  _injectAdvisorTab(advisory);
}

function _buildAdvisoryPanelHTML(advisory) {
  const verdict = advisory.destination_verdict || {};
  const flags   = (verdict.flags || []).map(f => `
    <div class="advisory-flag ${f.type}">
      <span class="advisory-flag-icon">${f.icon}</span>
      <span>${esc(f.message)}</span>
    </div>`).join('');

  return `
    <div class="advisory-header">
      <div class="advisory-avatar">🤖</div>
      <div class="advisory-meta">
        <div class="advisory-from">✨ TripPilot AI Advisor</div>
        <div class="advisory-summary">${esc(advisory.ai_summary || '')}</div>
      </div>
    </div>
    ${flags ? `<div class="advisory-flags">${flags}</div>` : ''}`;
}

function _buildWeatherAlertHTML(alert) {
  const alts = (alert.indoor_alternatives || [])
    .map(a => `<span class="weather-alt-chip">${esc(a)}</span>`).join('');
  return `
    <div class="weather-alert-card ${alert.severity}">
      <div class="weather-alert-icon">${alert.icon || '⛈'}</div>
      <div class="weather-alert-body">
        <div class="weather-alert-title">Day ${alert.day} — ${esc(alert.condition)}</div>
        <div class="weather-alert-msg">${esc(alert.message)}</div>
        ${alts ? `<div class="weather-alert-alts"><span style="font-size:11px;color:var(--text-muted);margin-right:4px">Indoor options:</span>${alts}</div>` : ''}
      </div>
    </div>`;
}

function _injectAdvisorTab(advisory) {
  const tabsBar = document.querySelector('.results-tabs');
  if (!tabsBar || document.getElementById('rtab-advisor')) return;

  // Add tab button
  const btn = document.createElement('button');
  btn.id = 'rtab-advisor';
  btn.className = 'rtab';
  btn.textContent = '🤖 AI Advisor';
  btn.onclick = () => showTab('advisor');
  tabsBar.appendChild(btn);

  // Add tab content
  const content = document.createElement('div');
  content.id = 'tab-advisor';
  content.className = 'rtab-content';
  content.innerHTML = _buildAdvisorTabHTML(advisory);
  tabsBar.closest('.results-container')?.appendChild(content);
}

function _buildAdvisorTabHTML(advisory) {
  const alts   = advisory.alternative_suggestions || [];
  const timing = advisory.timing_advice || {};
  const tips   = advisory.pro_tips || [];
  const hacks  = advisory.budget_hacks || [];
  const ttype  = advisory.travel_type_tips || [];

  const altCards = alts.map(a => {
    const budgetClass = a.budget_diff_pct < -5 ? 'alt-budget-cheaper'
                      : a.budget_diff_pct > 5  ? 'alt-budget-pricier'
                      : 'alt-budget-same';
    const budgetLabel = a.budget_diff_pct < -5
      ? `💰 ${Math.abs(a.budget_diff_pct)}% cheaper`
      : a.budget_diff_pct > 5
      ? `💸 ${a.budget_diff_pct}% pricier`
      : '≈ Similar cost';

    return `
      <div class="alt-card" onclick="planAlternative('${a.destination}')">
        <div class="alt-card-dest">${esc(a.destination)}</div>
        <div class="alt-card-country">${esc(a.country)}</div>
        <div class="alt-card-reason">${esc(a.reason)}</div>
        <div class="alt-card-budget ${budgetClass}">${budgetLabel}</div>
        <div class="alt-card-plan-btn">Plan this trip →</div>
      </div>`;
  }).join('');

  const tipItems = tips.map(t => `
    <div class="ai-insight-item">💡 ${esc(t)}</div>`).join('');

  const hackItems = hacks.map(h => `
    <div class="ai-insight-item">🪙 ${esc(h)}</div>`).join('');

  const ttypeItems = ttype.map(t => `
    <div class="ai-insight-item">👤 ${esc(t)}</div>`).join('');

  return `
    <!-- Destination verdict -->
    <div class="advisory-panel" style="margin-bottom:20px">
      <div class="advisory-header">
        <div class="advisory-avatar">🤖</div>
        <div class="advisory-meta">
          <div class="advisory-from">AI Analysis</div>
          <div class="advisory-summary">${esc(advisory.ai_summary || '')}</div>
        </div>
      </div>
    </div>

    <!-- Timing advice -->
    ${timing.message ? `
    <div class="ai-insights-box" style="margin-bottom:20px">
      <div class="ai-insights-title">📅 Timing Intelligence</div>
      <div class="ai-insight-item">${esc(timing.message)}</div>
      ${timing.weather_note ? `<div class="ai-insight-item">🌡️ ${esc(timing.weather_note)}</div>` : ''}
    </div>` : ''}

    <!-- Alternative destinations -->
    ${alts.length ? `
    <div class="alternatives-section">
      <div class="alt-section-title">
        🔄 Alternative Destinations
        <span style="font-size:12px;color:var(--text-muted);font-weight:400">Tap to plan</span>
      </div>
      <div class="alt-cards">${altCards}</div>
    </div>` : ''}

    <!-- Pro tips -->
    ${tipItems ? `
    <div class="ai-insights-box" style="margin-bottom:20px">
      <div class="ai-insights-title">✨ Pro Tips for Your Destination</div>
      ${tipItems}
    </div>` : ''}

    <!-- Budget hacks -->
    ${hackItems ? `
    <div class="ai-insights-box" style="margin-bottom:20px">
      <div class="ai-insights-title">💰 Local Budget Hacks</div>
      ${hackItems}
    </div>` : ''}

    <!-- Travel type advice -->
    ${ttypeItems ? `
    <div class="ai-insights-box" style="margin-bottom:20px">
      <div class="ai-insights-title">🧳 Personalised for Your Travel Style</div>
      ${ttypeItems}
    </div>` : ''}

    <!-- Compare CTA -->
    <div style="text-align:center; padding:16px 0">
      <p style="font-size:13px;color:var(--text-muted);margin-bottom:12px">
        Want to compare two destinations side-by-side?
      </p>
      <button class="btn-outline" onclick="openCompareModal()">⚖️ Compare Destinations</button>
    </div>`;
}

// ── Plan alternative from card click ──────────────────────────
function planAlternative(destName) {
  window.location.href = `/planner?dest=${encodeURIComponent(destName)}`;
}

// ── Chat message handling ──────────────────────────────────────
function handleChatKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendChatMessage();
  }
}

function autoResizeInput(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 80) + 'px';
}

async function sendChatMessage() {
  const input = document.getElementById('aiInput');
  if (!input) return;
  const question = input.value.trim();
  if (!question || Assistant.typing) return;

  input.value = '';
  input.style.height = 'auto';
  _appendMessage('user', question);
  _showTyping();

  try {
    const payload = {
      question,
      context: {
        destination:   Assistant.context?.destination   || '',
        days:          Assistant.context?.days          || 5,
        budget:        Assistant.context?.budget        || 1000,
        travel_type:   Assistant.context?.travel_type   || 'solo',
        travelers:     Assistant.context?.travelers     || 1,
        interests:     Assistant.context?.interests     || [],
        accommodation: Assistant.context?.accommodation || 'hotel',
        transport:     Assistant.context?.transport     || 'public',
        start_date:    Assistant.context?.start_date    || '',
        plan:          Assistant.context?.plan          || {},
      },
    };

    const res  = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    _removeTyping();

    if (data.status === 'success') {
      _appendMessage('assistant', data.answer);
    } else {
      _appendMessage('assistant', 'Sorry, I ran into an issue. Please try again.');
    }
  } catch (_) {
    _removeTyping();
    _appendMessage('assistant', 'Connection issue. Make sure the server is running.');
  }
}

function sendQuickQuestion(q) {
  const input = document.getElementById('aiInput');
  if (input) input.value = q;
  sendChatMessage();
}

// ── Message rendering ──────────────────────────────────────────
function _appendMessage(role, text) {
  const container = document.getElementById('aiMessages');
  if (!container) return;

  const msg = document.createElement('div');
  msg.className = `ai-msg ${role}`;

  const avatar = role === 'assistant' ? '🤖' : (App.user?.name?.[0] || 'U');
  // Convert markdown **bold** to <strong>
  const formatted = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');

  msg.innerHTML = `
    <div class="ai-msg-avatar">${avatar}</div>
    <div class="ai-msg-bubble">${formatted}</div>`;

  container.appendChild(msg);
  container.scrollTop = container.scrollHeight;

  Assistant.msgHistory.push({ role, text });
}

function _sendAdvisoryMessage(summary) {
  if (!summary) return;
  // Update the initial placeholder message
  const msgs = document.getElementById('aiMessages');
  if (msgs) {
    const first = msgs.querySelector('.ai-msg.assistant .ai-msg-bubble');
    if (first) {
      const formatted = summary
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
      first.innerHTML = formatted;
      // Update status
      const status = document.querySelector('.ai-panel-status span:last-child');
      if (status) status.textContent = 'Ready — ask me anything';
    }
  }
}

function _showTyping() {
  Assistant.typing = true;
  const container  = document.getElementById('aiMessages');
  if (!container) return;
  const typing = document.createElement('div');
  typing.className = 'ai-msg assistant';
  typing.id = 'aiTypingIndicator';
  typing.innerHTML = `
    <div class="ai-msg-avatar">🤖</div>
    <div class="ai-typing">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>`;
  container.appendChild(typing);
  container.scrollTop = container.scrollHeight;

  const sendBtn = document.getElementById('aiSendBtn');
  if (sendBtn) sendBtn.disabled = true;
}

function _removeTyping() {
  Assistant.typing = false;
  document.getElementById('aiTypingIndicator')?.remove();
  const sendBtn = document.getElementById('aiSendBtn');
  if (sendBtn) sendBtn.disabled = false;
}

// ── Destination compare modal ─────────────────────────────────
function openCompareModal() {
  const dest = Assistant.context?.destination || '';
  // DEST_LIST is defined in main.js
  const options = DEST_LIST.map(d =>
    `<option value="${d.toLowerCase()}" ${d.toLowerCase() === dest ? 'selected' : ''}>${d}</option>`
  ).join('');

  // Reuse modal infrastructure from main.js
  const existing = document.getElementById('compareModal');
  if (existing) existing.remove();

  const modal = document.createElement('div');
  modal.id = 'compareModal';
  modal.className = 'modal-overlay';
  modal.style.display = 'flex';
  modal.innerHTML = `
    <div class="modal modal-wide">
      <button class="modal-close" onclick="closeModal('compareModal')">✕</button>
      <h2>⚖️ Compare Destinations</h2>
      <p class="modal-sub">Side-by-side AI analysis for your trip profile.</p>
      <div style="display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap">
        <div style="flex:1;min-width:140px">
          <label style="font-size:12px;color:var(--text-muted);margin-bottom:4px;display:block">Destination A</label>
          <select id="cmpDestA" style="width:100%;background:var(--bg-3);border:1px solid var(--border);border-radius:var(--r-md);padding:10px;color:var(--text-primary);font-size:14px;outline:none">
            ${options}
          </select>
        </div>
        <div style="flex:1;min-width:140px">
          <label style="font-size:12px;color:var(--text-muted);margin-bottom:4px;display:block">Destination B</label>
          <select id="cmpDestB" style="width:100%;background:var(--bg-3);border:1px solid var(--border);border-radius:var(--r-md);padding:10px;color:var(--text-primary);font-size:14px;outline:none">
            ${options.replace(`value="${dest}"`, `value="${DEST_LIST.find(d => d.toLowerCase() !== dest)?.toLowerCase() || 'tokyo'}"`)}
          </select>
        </div>
        <div style="display:flex;align-items:flex-end">
          <button class="btn-primary" onclick="runComparison()">Compare →</button>
        </div>
      </div>
      <div id="compareResult" style="min-height:100px"></div>
    </div>`;

  modal.addEventListener('click', e => { if (e.target === modal) closeModal('compareModal'); });
  document.body.appendChild(modal);
}

async function runComparison() {
  const destA = document.getElementById('cmpDestA')?.value;
  const destB = document.getElementById('cmpDestB')?.value;
  const result = document.getElementById('compareResult');
  if (!destA || !destB || !result) return;
  if (destA === destB) {
    result.innerHTML = '<p style="color:var(--warning);text-align:center;padding:16px">Please select two different destinations.</p>';
    return;
  }

  result.innerHTML = `
    <div style="text-align:center;padding:32px;color:var(--text-muted)">
      <span class="spinner" style="display:inline-block;width:24px;height:24px;border:3px solid rgba(255,255,255,.1);border-top-color:var(--primary);border-radius:50%;animation:spin .7s linear infinite;margin-bottom:8px"></span>
      <p>Analysing both destinations…</p>
    </div>`;

  try {
    const ctx = Assistant.context || {};
    const res = await fetch('/api/ai/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        destination_a: destA,
        destination_b: destB,
        days:         ctx.days || 5,
        budget:       ctx.budget || 1000,
        travel_type:  ctx.travel_type || 'solo',
        travelers:    ctx.travelers || 1,
        interests:    ctx.interests || [],
      }),
    });
    const data = await res.json();
    if (data.status === 'success') {
      result.innerHTML = _renderComparisonResult(data.comparison);
    } else {
      result.innerHTML = `<p style="color:var(--danger)">${data.message}</p>`;
    }
  } catch (_) {
    result.innerHTML = '<p style="color:var(--danger)">Comparison failed. Check the server.</p>';
  }
}

function _renderComparisonResult(cmp) {
  const a = cmp.destination_a;
  const b = cmp.destination_b;
  const rec = cmp.recommendation || '';

  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const bestMonths = (arr) => (arr || []).map(m => months[m - 1]).join(', ') || '—';

  const aWinner = (a.estimated_trip_cost || 0) <= (b.estimated_trip_cost || 0);

  return `
    <div class="compare-modal-content">
      <div class="compare-grid">
        <div class="compare-dest-col ${aWinner ? 'winner' : ''}">
          <div class="compare-dest-name">${esc(a.name)} ${aWinner ? '✅' : ''}</div>
          <div class="compare-dest-score">Verdict: ${a.verdict?.verdict || '—'} (${a.verdict?.score || 0}/100)</div>
          <div class="compare-row"><span class="compare-row-label">Est. trip cost</span><span class="compare-row-val">${fmt(a.estimated_trip_cost)}</span></div>
          <div class="compare-row"><span class="compare-row-label">Difficulty</span><span class="compare-row-val">${a.difficulty}</span></div>
          <div class="compare-row"><span class="compare-row-label">Safety</span><span class="compare-row-val">${a.safety}</span></div>
          <div class="compare-row"><span class="compare-row-label">Best months</span><span class="compare-row-val">${bestMonths(a.best_months)}</span></div>
          <div class="compare-row"><span class="compare-row-label">Tags</span><span class="compare-row-val">${(a.tags || []).slice(0,3).join(', ')}</span></div>
          ${(a.pro_tips || []).map(t => `<div class="ai-insight-item" style="font-size:12px;margin-top:6px">💡 ${esc(t)}</div>`).join('')}
        </div>
        <div class="compare-dest-col ${!aWinner ? 'winner' : ''}">
          <div class="compare-dest-name">${esc(b.name)} ${!aWinner ? '✅' : ''}</div>
          <div class="compare-dest-score">Verdict: ${b.verdict?.verdict || '—'} (${b.verdict?.score || 0}/100)</div>
          <div class="compare-row"><span class="compare-row-label">Est. trip cost</span><span class="compare-row-val">${fmt(b.estimated_trip_cost)}</span></div>
          <div class="compare-row"><span class="compare-row-label">Difficulty</span><span class="compare-row-val">${b.difficulty}</span></div>
          <div class="compare-row"><span class="compare-row-label">Safety</span><span class="compare-row-val">${b.safety}</span></div>
          <div class="compare-row"><span class="compare-row-label">Best months</span><span class="compare-row-val">${bestMonths(b.best_months)}</span></div>
          <div class="compare-row"><span class="compare-row-label">Tags</span><span class="compare-row-val">${(b.tags || []).slice(0,3).join(', ')}</span></div>
          ${(b.pro_tips || []).map(t => `<div class="ai-insight-item" style="font-size:12px;margin-top:6px">💡 ${esc(t)}</div>`).join('')}
        </div>
      </div>
      <div class="compare-rec">
        <strong>AI Recommendation:</strong>
        ${rec.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}
      </div>
    </div>`;
}
