/* ═══════════════════════════════════════════════════════════
   TripPilot AI — Planner Page Logic
   ═══════════════════════════════════════════════════════════ */

'use strict';

let currentStep = 1;
let currentPlan = null;
let currentTripId = null;
let selectedInterests = [];

// ── Init ───────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Set today as default date
  const startDate = document.getElementById('startDate');
  if (startDate) {
    const today = new Date().toISOString().split('T')[0];
    startDate.min = today;
    startDate.value = today;
  }
  // Pre-fill destination from URL param
  const params = new URLSearchParams(window.location.search);
  const destParam = params.get('dest');
  if (destParam) {
    const destInput = document.getElementById('destination');
    if (destInput) destInput.value = destParam;
  }
});

// ── Step navigation ────────────────────────────────────────────
function nextStep(from) {
  if (!validateStep(from)) return;
  goToStep(from + 1);
}

function prevStep(from) {
  goToStep(from - 1);
}

function goToStep(step) {
  document.getElementById(`step${currentStep}`)?.classList.remove('active');
  currentStep = step;
  const next = document.getElementById(`step${step}`);
  if (next) {
    next.classList.add('active');
    next.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  updateStepIndicator(step);
}

function updateStepIndicator(step) {
  document.querySelectorAll('.si-step').forEach((el, i) => {
    const s = i + 1;
    el.classList.remove('active', 'completed');
    if (s === step) el.classList.add('active');
    if (s < step)  el.classList.add('completed');
  });
  document.querySelectorAll('.si-line').forEach((el, i) => {
    el.classList.toggle('completed', i + 1 < step);
  });
}

function validateStep(step) {
  if (step === 1) {
    const name = document.getElementById('travelerName')?.value.trim();
    if (!name) { showToast('Please enter your name', 'error'); return false; }
  }
  if (step === 2) {
    const dest = document.getElementById('destination')?.value.trim();
    const date = document.getElementById('startDate')?.value;
    if (!dest) { showToast('Please enter a destination', 'error'); return false; }
    if (!date) { showToast('Please select a start date', 'error'); return false; }
  }
  if (step === 3) {
    const budget = parseFloat(document.getElementById('budget')?.value || '0');
    if (!budget || budget <= 0) { showToast('Please enter a valid budget', 'error'); return false; }
  }
  return true;
}

// ── Form helpers ───────────────────────────────────────────────
function selectChip(el, field) {
  el.closest('.chip-group').querySelectorAll('.chip').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
  const hidden = document.getElementById(field);
  if (hidden) hidden.value = el.dataset.value;
}

function adjustNum(field, delta) {
  const hidden  = document.getElementById(field);
  const display = document.getElementById(field + 'Display');
  if (!hidden || !display) return;
  const limits = { travelers: [1, 20], days: [1, 30] };
  const [min, max] = limits[field] || [1, 99];
  const newVal = Math.min(max, Math.max(min, parseInt(hidden.value) + delta));
  hidden.value = newVal;
  display.textContent = newVal;
}

function setBudgetPreset(value) {
  const input = document.getElementById('budget');
  if (input) input.value = value;
}

function toggleInterest(el) {
  const val = el.dataset.value;
  if (selectedInterests.includes(val)) {
    selectedInterests = selectedInterests.filter(i => i !== val);
    el.classList.remove('selected');
  } else {
    selectedInterests.push(val);
    el.classList.add('selected');
  }
}

// ── Destination autocomplete ───────────────────────────────────
function suggestDest(query) {
  const box = document.getElementById('destAutocomplete');
  if (!box) return;
  if (!query.trim()) { box.innerHTML = ''; _clearMatchPreview(); return; }
  // DEST_LIST and DEST_EMOJIS are defined in main.js
  const matches = DEST_LIST.filter(d => d.toLowerCase().includes(query.toLowerCase()));
  if (!matches.length) { box.innerHTML = ''; return; }
  box.innerHTML = matches.map(d => `
    <div class="dest-ac-item" onclick="pickDest('${d}')">
      <span>${DEST_EMOJIS[d.toLowerCase()] || '📍'}</span>
      <span>${d}</span>
    </div>`).join('');
}

function pickDest(dest) {
  const input = document.getElementById('destination');
  if (input) input.value = dest;
  const box = document.getElementById('destAutocomplete');
  if (box) box.innerHTML = '';
  // Show live match preview for selected destination
  _fetchMatchPreview(dest);
}

// ── Live match preview (shown in step 2 after dest selected) ──
let _matchPreviewTimeout = null;

function _fetchMatchPreview(dest) {
  clearTimeout(_matchPreviewTimeout);
  _matchPreviewTimeout = setTimeout(async () => {
    const container = document.getElementById('destMatchPreview');
    if (!container) return;
    if (!dest?.trim()) { container.innerHTML = ''; return; }

    const budget      = parseFloat(document.getElementById('budget')?.value) || 1000;
    const days        = parseInt(document.getElementById('days')?.value) || 5;
    const travelType  = document.getElementById('travelType')?.value || 'solo';
    const travelers   = parseInt(document.getElementById('travelers')?.value) || 1;
    const startDate   = document.getElementById('startDate')?.value || new Date().toISOString().split('T')[0];
    const budgetLevel = budget / Math.max(days,1) / Math.max(travelers,1) < 80 ? 'low'
                       : budget / Math.max(days,1) / Math.max(travelers,1) < 250 ? 'medium' : 'high';

    container.innerHTML = `<div style="display:flex;align-items:center;gap:8px;color:var(--text-muted);font-size:12px;padding:8px 0">
      <span class="spinner" style="display:inline-block;width:14px;height:14px;border:2px solid rgba(255,255,255,.1);border-top-color:var(--primary);border-radius:50%;animation:spin .6s linear infinite"></span>
      Calculating match score...
    </div>`;

    try {
      const res  = await fetch('/api/recommendations', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
          interests    : selectedInterests,
          budget_level : budgetLevel,
          travel_type  : travelType,
          travelers    : travelers,
          start_date   : startDate,
        }),
      });
      const data = await res.json();
      const recs = data.recommendations || [];
      const hit  = recs.find(r => r.name?.toLowerCase() === dest.toLowerCase());

      if (!hit) {
        container.innerHTML = `<div style="font-size:12px;color:var(--text-muted);padding:6px 0">
          No match data for this destination yet.</div>`;
        return;
      }

      const match = hit.match_pct || 0;
      const color = match >= 70 ? '#10b981' : match >= 45 ? '#f59e0b' : '#ef4444';
      const label = match >= 70 ? 'Great match' : match >= 45 ? 'Decent match' : 'Weak match';
      const sb    = hit.score_breakdown || {};

      const dims = [
        { label: 'Interests',   key: 'interests',   max: 40, color: '#6366f1' },
        { label: 'Budget',      key: 'budget',      max: 20, color: '#10b981' },
        { label: 'Travel type', key: 'travel_type', max: 20, color: '#06b6d4' },
        { label: 'Season',      key: 'season',      max: 10, color: '#f59e0b' },
        { label: 'Group size',  key: 'group_size',  max: 10, color: '#8b5cf6' },
      ];

      const bars = Object.keys(sb).length ? dims.map(dim => {
        const val = sb[dim.key] || 0;
        const pct = Math.round(val / dim.max * 100);
        return `<div style="display:flex;align-items:center;gap:6px">
          <span style="font-size:9px;color:var(--text-muted);min-width:62px;text-transform:uppercase;letter-spacing:.05em">${dim.label}</span>
          <div style="flex:1;height:3px;background:rgba(255,255,255,.06);border-radius:2px;overflow:hidden">
            <div style="width:${pct}%;height:100%;background:${dim.color};border-radius:2px"></div>
          </div>
          <span style="font-size:9px;color:var(--text-muted);min-width:22px;text-align:right">${val}/${dim.max}</span>
        </div>`;
      }).join('') : '';

      const why = (hit.why || []).slice(0,2)
        .map(r => `<div style="font-size:11px;color:var(--text-muted);line-height:1.5">› ${esc(r)}</div>`)
        .join('');

      container.innerHTML = `
        <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r-lg);
                    padding:14px 16px;margin-top:10px;position:relative;overflow:hidden">
          <div style="position:absolute;top:0;left:0;right:0;height:2px;background:${color}"></div>
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
            <div>
              <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;
                           color:var(--text-muted);margin-bottom:2px">AI Match Score</div>
              <div style="font-size:13px;color:var(--text-secondary)">${label} for your profile</div>
            </div>
            <div style="font-size:32px;font-weight:900;color:${color};font-variant-numeric:tabular-nums">
              ${match}%
            </div>
          </div>
          <div style="display:flex;flex-direction:column;gap:4px;margin-bottom:10px">${bars}</div>
          <div style="display:flex;flex-direction:column;gap:2px">${why}</div>
        </div>`;
    } catch (_) {
      container.innerHTML = '';
    }
  }, 400);  // debounce 400ms
}

function _clearMatchPreview() {
  const c = document.getElementById('destMatchPreview');
  if (c) c.innerHTML = '';
}

// ── Lazy-load a script (returns a Promise, no-ops if already loaded) ──
function _lazyLoadScript(src) {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) { resolve(); return; }
    const s    = document.createElement('script');
    s.src      = src;
    s.onload   = resolve;
    s.onerror  = () => { console.warn('Could not load', src); resolve(); }; // non-fatal
    document.head.appendChild(s);
  });
}

// ── Generate trip ──────────────────────────────────────────────
async function generateTrip() {
  if (!validateStep(3)) return;

  const payload = {
    traveler_name  : document.getElementById('travelerName')?.value.trim()    || '',
    traveler_age   : parseInt(document.getElementById('travelerAge')?.value)   || null,
    start_location : document.getElementById('startLocation')?.value.trim()   || '',
    destination    : document.getElementById('destination')?.value.trim()     || '',
    start_date     : document.getElementById('startDate')?.value              || '',
    days           : parseInt(document.getElementById('days')?.value)         || 5,
    budget         : parseFloat(document.getElementById('budget')?.value)     || 1000,
    travel_type    : document.getElementById('travelType')?.value             || 'solo',
    travelers      : parseInt(document.getElementById('travelers')?.value)    || 1,
    accommodation  : document.getElementById('accommodation')?.value          || 'hotel',
    transport      : document.getElementById('transport')?.value              || 'public',
    interests      : selectedInterests,
  };

  // Show loading state
  const btnText   = document.getElementById('generateBtnText');
  const btnLoader = document.getElementById('generateBtnLoader');
  if (btnText)   btnText.style.display = 'none';
  if (btnLoader) btnLoader.style.display = 'flex';

  try {
    const res  = await fetch('/api/trips/plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (data.status === 'success') {
      currentPlan   = data.plan;
      currentTripId = data.trip_id;
      renderResults(data.plan, payload);
      // Lazy-load ai_assistant.js only when a plan is ready (not on initial page load)
      const aiSrc = document.querySelector('meta[name="ai-assistant-src"]')?.content;
      if (aiSrc) {
        await _lazyLoadScript(aiSrc);
      }
      if (typeof initAssistant === 'function') {
        initAssistant(payload, data.plan);
      }
    } else {
      showToast(data.message || 'Planning failed. Please try again.', 'error');
    }
  } catch (err) {
    showToast('Connection error. Is the server running?', 'error');
  } finally {
    if (btnText)   btnText.style.display = '';
    if (btnLoader) btnLoader.style.display = 'none';
  }
}

// ── Render results ─────────────────────────────────────────────
function renderResults(plan, payload) {
  const container = document.getElementById('plannerContainer');
  const results   = document.getElementById('resultsContainer');
  if (container) container.style.display = 'none';
  if (results)   results.style.display  = 'block';

  // Update steps indicator to show step 5
  updateStepIndicator(5);
  document.querySelectorAll('.si-step').forEach(el => {
    if (parseInt(el.dataset.step) <= 4) el.classList.add('completed');
  });

  // Header
  document.getElementById('resTripTitle').textContent =
    `${payload.traveler_name}'s ${plan.destination.name} Trip`;
  document.getElementById('resTripSubtitle').textContent =
    `${plan.trip_summary.days} days · ${plan.trip_summary.travel_type} · ${fmt(plan.budget.total_budget)} budget`;

  renderItinerary(plan);
  renderBudget(plan);
  renderHotels(plan);
  renderWeather(plan);
  renderRoutes(plan);
  renderExpenses(plan);

  results.scrollIntoView({ behavior: 'smooth', block: 'start' });
  showToast('Your trip plan is ready! 🎉', 'success');
}

// ── Tab switching ──────────────────────────────────────────────
function showTab(name) {
  document.querySelectorAll('.rtab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.rtab-content').forEach(c => c.classList.remove('active'));
  document.querySelector(`.rtab[onclick="showTab('${name}')"]`)?.classList.add('active');
  document.getElementById(`tab-${name}`)?.classList.add('active');
}

// ── Itinerary ─────────────────────────────────────────────────
function renderItinerary(plan) {
  const container = document.getElementById('itineraryCards');
  if (!container) return;
  const itinerary = plan.itinerary || [];

  if (!itinerary.length) {
    container.innerHTML = '<p style="color:var(--text-muted)">No itinerary generated.</p>';
    return;
  }

  container.innerHTML = itinerary.map(day => {
    const items = (day.timeline || []).map(t => {
      const dotClass = ['food','nature','shopping','museum','historic','religious','adventure']
        .includes(t.type) ? t.type : '';
      return `
        <div class="timeline-item">
          <div class="timeline-time">${t.time}</div>
          <div class="timeline-dot ${dotClass}"></div>
          <div class="timeline-content">
            <div class="timeline-activity">${esc(t.activity)}</div>
            ${t.desc ? `<div class="timeline-desc">${esc(t.desc)}</div>` : ''}
            <div class="timeline-meta">
              ${t.duration ? `<span>⏱ ${t.duration}</span>` : ''}
              ${t.type    ? `<span>📍 ${t.type}</span>` : ''}
            </div>
          </div>
          <div class="timeline-cost">${t.cost ? fmt(t.cost) : 'Free'}</div>
        </div>`;
    }).join('');

    const w = day.weather || {};
    const adjNote = day.adjustment_note
      ? `<div class="adjustment-note">${esc(day.adjustment_note)}</div>` : '';

    return `
      <div class="day-card" id="day-${day.day}">
        <div class="day-header" onclick="toggleDay(${day.day})">
          <div class="day-header-left">
            <div class="day-num-badge">D${day.day}</div>
            <div>
              <div class="day-title">${esc(day.theme)}</div>
              <div class="day-date">${esc(day.date)}</div>
            </div>
          </div>
          <div class="day-header-right">
            <div class="day-weather-pill">
              ${w.icon || '☀️'} ${w.temp_c || 0}°C · ${w.rain_probability || 0}% rain
            </div>
            <div class="day-spend">${fmt(day.daily_spending)}</div>
            <div class="day-chevron">▼</div>
          </div>
        </div>
        <div class="day-body">
          ${adjNote}
          <div class="timeline">${items}</div>
        </div>
      </div>`;
  }).join('');

  // Open day 1 by default
  const first = document.getElementById('day-1');
  if (first) { first.classList.add('open'); }
}

function toggleDay(dayNum) {
  const card = document.getElementById(`day-${dayNum}`);
  if (card) card.classList.toggle('open');
}

// ── Budget ────────────────────────────────────────────────────
function renderBudget(plan) {
  const container = document.getElementById('budgetDashboard');
  if (!container || !plan.budget) return;

  const b         = plan.budget;
  const bd        = b.breakdown || {};
  const pct       = b.utilization_pct || 0;
  const remaining = b.remaining;
  const travelers = plan.trip_summary?.travelers || 1;
  const days      = plan.trip_summary?.days || 1;
  const perPerson = travelers > 1 ? Math.round((b.total_budget || 0) / travelers) : null;
  const perDay    = Math.round((b.total_budget || 0) / days);
  const itinerary = plan.itinerary || [];

  // ── Status colours ────────────────────────────────────────
  const remainClass = remaining >= 0 ? 'positive' : 'negative';
  const barColor    = pct >= 100 ? 'linear-gradient(90deg,var(--warning),var(--danger))'
                    : pct >= 85  ? 'linear-gradient(90deg,var(--warning),#f97316)'
                    : 'linear-gradient(90deg,var(--primary),var(--accent))';
  const pctColor    = pct >= 100 ? 'var(--danger)' : pct >= 85 ? 'var(--warning)' : 'var(--text-primary)';

  const catColors = {
    accommodation: '#6366f1', transportation: '#06b6d4', food: '#10b981',
    attractions: '#f59e0b', miscellaneous: '#8b5cf6', emergency_fund: '#ef4444',
  };
  const catIcons = {
    accommodation: '🏨', transportation: '🚌', food: '🍽️',
    attractions: '🎡', miscellaneous: '📦', emergency_fund: '🛡️',
  };

  // ── KPI cards ─────────────────────────────────────────────
  const kpiCards = `
    <div class="budget-summary">
      <div class="budget-kpi">
        <div class="budget-kpi-label">Total Budget</div>
        <div class="budget-kpi-value">${fmt(b.total_budget)}</div>
        ${perPerson ? `<div style="font-size:11px;color:var(--text-muted);margin-top:4px">${fmt(perPerson)} per person</div>` : ''}
      </div>
      <div class="budget-kpi">
        <div class="budget-kpi-label">Estimated Cost</div>
        <div class="budget-kpi-value ${pct > 90 ? 'warning' : ''}">${fmt(b.estimated_total)}</div>
        <div style="font-size:11px;color:var(--text-muted);margin-top:4px">${fmt(perDay)}/day avg</div>
      </div>
      <div class="budget-kpi">
        <div class="budget-kpi-label">Remaining</div>
        <div class="budget-kpi-value ${remainClass}">${fmt(remaining)}</div>
        <div style="font-size:11px;color:${remaining >= 0 ? 'var(--success)' : 'var(--danger)'};margin-top:4px">
          ${remaining >= 0 ? '✅ Under budget' : '⚠️ Over budget'}
        </div>
      </div>
      <div class="budget-kpi">
        <div class="budget-kpi-label">Budget Used</div>
        <div class="budget-kpi-value" style="color:${pctColor}">${pct}%</div>
        <div style="font-size:11px;color:var(--text-muted);margin-top:4px">
          ${pct < 70 ? 'Comfortable' : pct < 90 ? 'On track' : pct < 100 ? 'Near limit' : 'Exceeded'}
        </div>
      </div>
    </div>`;

  // ── Utilization bar ───────────────────────────────────────
  const utilizationBar = `
    <div class="budget-utilization">
      <div class="utilization-header">
        <span class="utilization-title">Budget Utilization</span>
        <span class="utilization-pct" style="color:${pctColor}">${pct}%</span>
      </div>
      <div class="progress-bar" style="height:12px">
        <div class="progress-fill" style="width:${Math.min(pct,100)}%;background:${barColor}"></div>
      </div>
      <!-- Budget scale markers -->
      <div style="display:flex;justify-content:space-between;margin-top:6px">
        ${[0,25,50,75,100].map(m => `
          <div style="text-align:center">
            <div style="width:1px;height:4px;background:var(--border);margin:0 auto 2px"></div>
            <div style="font-size:9px;color:var(--text-muted)">${m}%</div>
          </div>`).join('')}
      </div>
    </div>`;

  // ── Category breakdown with SVG donut chart ───────────────
  const totalEstimated = b.estimated_total || 1;
  const bdEntries = Object.entries(bd).filter(([,v]) => v > 0);

  // Build SVG donut
  const radius  = 54;
  const cx      = 70;
  const cy      = 70;
  const circumf = 2 * Math.PI * radius;
  let offset    = 0;
  const segments = bdEntries.map(([key, val]) => {
    const frac  = val / totalEstimated;
    const dash  = frac * circumf;
    const seg   = { key, val, frac, dash, offset, color: catColors[key] || '#64748b' };
    offset     += dash;
    return seg;
  });

  const donutSlices = segments.map(s => `
    <circle cx="${cx}" cy="${cy}" r="${radius}"
            fill="none" stroke="${s.color}" stroke-width="16"
            stroke-dasharray="${s.dash.toFixed(2)} ${(circumf - s.dash).toFixed(2)}"
            stroke-dashoffset="${(-s.offset + circumf/4).toFixed(2)}"
            style="transition:stroke-dasharray 800ms ease">
      <title>${s.key}: ${fmt(s.val)} (${(s.frac*100).toFixed(0)}%)</title>
    </circle>`).join('');

  const donutSvg = `
    <svg width="140" height="140" viewBox="0 0 140 140" role="img" aria-label="Budget breakdown donut chart">
      <circle cx="${cx}" cy="${cy}" r="${radius}" fill="none"
              stroke="rgba(255,255,255,0.06)" stroke-width="16"/>
      ${donutSlices}
      <text x="${cx}" y="${cy - 6}" text-anchor="middle"
            fill="var(--text-primary)" font-size="13" font-weight="800"
            font-family="Inter,sans-serif">${pct}%</text>
      <text x="${cx}" y="${cy + 10}" text-anchor="middle"
            fill="var(--text-muted)" font-size="9"
            font-family="Inter,sans-serif">USED</text>
    </svg>`;

  const legendRows = bdEntries.map(([key, val]) => {
    const pctBar = Math.min((val / totalEstimated) * 100, 100);
    const color  = catColors[key] || '#64748b';
    return `
      <div class="breakdown-item">
        <div style="width:10px;height:10px;border-radius:2px;background:${color};flex-shrink:0"></div>
        <div class="breakdown-label">${catIcons[key] || '💰'} ${key.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}</div>
        <div class="breakdown-bar-wrap">
          <div class="breakdown-bar" style="width:${pctBar}%;background:${color}"></div>
        </div>
        <div class="breakdown-amount">${fmt(val)}</div>
      </div>`;
  }).join('');

  const breakdownSection = `
    <div class="budget-breakdown">
      <div class="breakdown-title">Cost Breakdown</div>
      <div style="display:flex;align-items:center;gap:24px;flex-wrap:wrap">
        <div style="flex-shrink:0">${donutSvg}</div>
        <div style="flex:1;min-width:200px">${legendRows}</div>
      </div>
    </div>`;

  // ── Daily spending chart (SVG bar chart) ──────────────────
  let dailyChartHtml = '';
  if (itinerary.length > 0) {
    const dailySpends = itinerary.map(d => ({ day: d.day, label: `D${d.day}`, amount: d.daily_spending || 0 }));
    const maxSpend    = Math.max(...dailySpends.map(d => d.amount), 1);
    const chartW      = 100;
    const chartH      = 80;
    const barW        = Math.max(4, Math.floor((chartW - dailySpends.length * 2) / dailySpends.length));
    const avgSpend    = dailySpends.reduce((s,d) => s+d.amount, 0) / dailySpends.length;

    const bars = dailySpends.map((d, i) => {
      const barH  = Math.max(2, (d.amount / maxSpend) * (chartH - 14));
      const x     = i * (barW + 2) + 1;
      const y     = chartH - barH - 12;
      const color = d.amount > avgSpend * 1.2 ? '#f59e0b' : '#6366f1';
      return `<rect x="${x}" y="${y}" width="${barW}" height="${barH}"
                    rx="2" fill="${color}" opacity="0.85">
                <title>Day ${d.day}: ${fmt(d.amount)}</title>
              </rect>
              <text x="${x + barW/2}" y="${chartH - 2}" text-anchor="middle"
                    fill="var(--text-muted)" font-size="6">D${d.day}</text>`;
    }).join('');

    // Average line
    const avgY = chartH - (avgSpend / maxSpend) * (chartH - 14) - 12;
    const avgLine = `
      <line x1="0" y1="${avgY}" x2="${chartW}" y2="${avgY}"
            stroke="var(--accent)" stroke-width="0.8" stroke-dasharray="3,2" opacity="0.7"/>
      <text x="${chartW - 1}" y="${avgY - 2}" text-anchor="end"
            fill="var(--accent)" font-size="6">avg</text>`;

    dailyChartHtml = `
      <div class="budget-breakdown" style="margin-top:0">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
          <div class="breakdown-title" style="margin:0">Daily Spending</div>
          <div style="font-size:11px;color:var(--text-muted)">
            avg ${fmt(Math.round(avgSpend))}/day · 🟡 above avg
          </div>
        </div>
        <svg width="100%" viewBox="0 0 ${chartW} ${chartH}" preserveAspectRatio="none"
             style="height:80px" role="img" aria-label="Daily spending bar chart">
          ${bars}
          ${avgLine}
        </svg>
      </div>`;
  }

  // ── AI Insights ───────────────────────────────────────────
  const insightsHtml = (plan.ai_insights || []).length ? `
    <div class="ai-insights-box">
      <div class="ai-insights-title">✨ AI Budget Insights</div>
      ${plan.ai_insights.map(i => `<div class="ai-insight-item">${esc(i)}</div>`).join('')}
    </div>` : '';

  container.innerHTML = kpiCards + utilizationBar + breakdownSection + dailyChartHtml + insightsHtml;
}

// ── Hotels ────────────────────────────────────────────────────
function renderHotels(plan) {
  const container = document.getElementById('hotelsGrid');
  if (!container) return;
  const hotels = plan.hotels || [];

  if (!hotels.length) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🏨</div>
        <h3>No hotels found</h3>
        <p>Try adjusting your accommodation preference or destination.</p>
      </div>`;
    return;
  }

  const typeEmojis  = { hotel: '🏨', hostel: '🛏️', apartment: '🏠', resort: '🌴' };
  const typeLabels  = { hotel: 'Hotel', hostel: 'Hostel', apartment: 'Apartment', resort: 'Resort' };

  container.innerHTML = hotels.map((h, idx) => {
    // ── Stars display ────────────────────────────────────────
    const starCount   = Math.min(h.stars || 3, 5);
    const starsHtml   = '★'.repeat(starCount) + '☆'.repeat(Math.max(0, 5 - starCount));

    // ── Rating display with review count ────────────────────
    const reviews     = h.reviews ? `(${(h.reviews).toLocaleString()} reviews)` : '';
    const ratingColor = h.rating >= 4.7 ? '#10b981' : h.rating >= 4.3 ? '#f59e0b' : '#94a3b8';

    // ── Distance — fix: use distance_from_centre or distance_label ───
    const distNum     = h.distance_from_centre ?? h.distance_km ?? null;
    const distLabel   = h.distance_label
                     || (distNum !== null ? `${distNum} km from centre` : 'City centre area');
    const distColor   = distNum !== null && distNum <= 1 ? '#10b981'
                      : distNum <= 3 ? '#f59e0b' : '#94a3b8';

    // ── Price display ────────────────────────────────────────
    const pricePerNight = h.price_per_night || h.price_mid || 0;
    const priceLow      = h.price_low  || 0;
    const priceHigh     = h.price_high || 0;
    const priceRange    = priceLow && priceHigh
      ? `<span style="font-size:10px;color:var(--text-muted);display:block;margin-top:1px">
           Range: ${fmt(priceLow)}–${fmt(priceHigh)}/night
         </span>`
      : '';

    // ── Amenities ────────────────────────────────────────────
    const amenities = (h.amenities || []).slice(0, 5)
      .map(a => `<span class="hotel-amenity">${esc(a)}</span>`).join('');

    // ── Neighbourhood ────────────────────────────────────────
    const neighbourhood = h.neighbourhood
      ? `<div style="font-size:11px;color:var(--text-muted);margin-bottom:6px">
           📍 ${esc(h.neighbourhood)}
         </div>`
      : '';

    // ── Availability signal ──────────────────────────────────
    const rooms          = h.available_rooms ?? 0;
    const roomsColor     = rooms <= 3 ? '#ef4444' : rooms <= 6 ? '#f59e0b' : '#10b981';
    const roomsLabel     = rooms <= 3 ? `Only ${rooms} left!` : `${rooms} rooms available`;

    // ── Action buttons ───────────────────────────────────────
    const mapUrl     = h.map_url     || `https://www.google.com/maps/search/${encodeURIComponent(h.name || '')}`;
    const bookingUrl = h.booking_url || 'https://www.booking.com';

    // ── "Best value" badge for idx 0 ────────────────────────
    const bestBadge = idx === 0
      ? `<div style="position:absolute;top:10px;left:10px;
                     padding:3px 10px;background:rgba(16,185,129,0.9);
                     border-radius:var(--r-full);font-size:10px;font-weight:700;
                     color:#fff;z-index:2;letter-spacing:.04em">
           ✓ Best match
         </div>` : '';

    return `
      <div class="hotel-card">
        <!-- Image / placeholder area -->
        <div class="hotel-img" style="position:relative">
          ${typeEmojis[h.type] || '🏨'}
          ${bestBadge}
          <div class="hotel-stars" style="z-index:1">${starsHtml}</div>
        </div>

        <div class="hotel-body">
          <!-- Name + type -->
          <div style="display:flex;align-items:flex-start;justify-content:space-between;
                      gap:8px;margin-bottom:2px">
            <div class="hotel-name" style="flex:1">${esc(h.name)}</div>
            <span style="font-size:10px;font-weight:700;text-transform:uppercase;
                         letter-spacing:.08em;color:var(--text-muted);
                         white-space:nowrap;padding-top:2px">
              ${typeLabels[h.type] || h.type || 'Hotel'}
            </span>
          </div>

          <!-- Neighbourhood -->
          ${neighbourhood}

          <!-- Rating + reviews -->
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px">
            <span style="font-size:13px;font-weight:800;color:${ratingColor}">
              ⭐ ${h.rating ?? '—'}
            </span>
            <span style="font-size:11px;color:var(--text-muted)">${reviews}</span>
          </div>

          <!-- Distance from centre -->
          <div style="display:flex;align-items:center;gap:5px;margin-bottom:10px">
            <span style="font-size:11px;font-weight:600;color:${distColor}">
              🗺 ${esc(distLabel)}
            </span>
          </div>

          <!-- Amenities -->
          <div class="hotel-amenities" style="margin-bottom:12px">${amenities}</div>

          <!-- Footer: price + rooms + actions -->
          <div class="hotel-footer" style="flex-direction:column;gap:8px">
            <!-- Price row -->
            <div style="display:flex;align-items:flex-end;justify-content:space-between">
              <div>
                <div class="hotel-price">
                  ${fmt(pricePerNight)}<span>/night</span>
                </div>
                ${priceRange}
              </div>
              <div style="font-size:11px;font-weight:700;color:${roomsColor};text-align:right">
                ${esc(roomsLabel)}
              </div>
            </div>
            <!-- Action buttons -->
            <div style="display:flex;gap:8px">
              <a href="${esc(mapUrl)}" target="_blank" rel="noopener"
                 style="flex:1;text-align:center;padding:7px 10px;
                        background:rgba(255,255,255,0.04);border:1px solid var(--border);
                        border-radius:var(--r-md);font-size:11px;font-weight:600;
                        color:var(--text-secondary);text-decoration:none;
                        transition:all var(--t-fast);"
                 onmouseover="this.style.color='var(--text-primary)'"
                 onmouseout="this.style.color='var(--text-secondary)'">
                🗺 View Map
              </a>
              <a href="${esc(bookingUrl)}" target="_blank" rel="noopener"
                 style="flex:1;text-align:center;padding:7px 10px;
                        background:var(--primary);border:1px solid var(--primary);
                        border-radius:var(--r-md);font-size:11px;font-weight:700;
                        color:#fff;text-decoration:none;
                        transition:background var(--t-fast);"
                 onmouseover="this.style.background='var(--primary-dark)'"
                 onmouseout="this.style.background='var(--primary)'">
                Book Now →
              </a>
            </div>
          </div>
        </div>
      </div>`;
  }).join('');
}

// ── Weather ────────────────────────────────────────────────────
function renderWeather(plan) {
  const container = document.getElementById('weatherGrid');
  if (!container) return;
  const weather = plan.weather_overview || [];

  if (!weather.length) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🌤</div>
        <h3>No weather data available</h3>
        <p>Weather forecast will appear here after generating your trip plan.</p>
      </div>`;
    return;
  }

  // ── Weather summary stats ──────────────────────────────────
  const rainyDays  = weather.filter(w => (w.rain_probability || 0) > 60).length;
  const hotDays    = weather.filter(w => (w.temp_c || 0) >= 34).length;
  const avgTemp    = Math.round(weather.reduce((s, w) => s + (w.temp_c || 0), 0) / weather.length);
  const maxRain    = Math.max(...weather.map(w => w.rain_probability || 0));
  const hasLive    = weather.some(w => w.source === 'live');
  const sourceLabel = hasLive ? '🟢 Live weather data' : '📊 Climate model data';
  const sourceColor = hasLive ? '#10b981' : '#f59e0b';

  // Build overall recommendation
  const overallRec = _buildWeatherSummary(weather, rainyDays, hotDays, avgTemp);

  // ── Weather summary banner ─────────────────────────────────
  const summaryHtml = `
    <div style="grid-column:1/-1;background:var(--bg-card);border:1px solid var(--border);
                border-radius:var(--r-xl);padding:20px 24px;margin-bottom:4px">
      <div style="display:flex;align-items:flex-start;justify-content:space-between;
                  flex-wrap:wrap;gap:16px;margin-bottom:16px">
        <div>
          <div style="font-size:11px;font-weight:700;text-transform:uppercase;
                      letter-spacing:.1em;color:var(--text-muted);margin-bottom:4px">
            Weather Overview
          </div>
          <div style="font-size:15px;color:var(--text-primary);font-weight:600;
                      line-height:1.5;max-width:480px">
            ${esc(overallRec)}
          </div>
        </div>
        <span style="font-size:11px;font-weight:600;color:${sourceColor};
                     background:${sourceColor}18;border:1px solid ${sourceColor}40;
                     border-radius:var(--r-full);padding:4px 12px;white-space:nowrap;
                     align-self:flex-start">
          ${sourceLabel}
        </span>
      </div>
      <!-- Quick stats -->
      <div style="display:flex;gap:24px;flex-wrap:wrap">
        <div style="text-align:center">
          <div style="font-size:22px;font-weight:800;color:var(--text-primary)">${avgTemp}°C</div>
          <div style="font-size:10px;color:var(--text-muted);text-transform:uppercase;
                      letter-spacing:.08em">Avg Temp</div>
        </div>
        <div style="text-align:center">
          <div style="font-size:22px;font-weight:800;color:${rainyDays > 2 ? '#ef4444' : rainyDays > 0 ? '#f59e0b' : '#10b981'}">
            ${rainyDays}
          </div>
          <div style="font-size:10px;color:var(--text-muted);text-transform:uppercase;
                      letter-spacing:.08em">Rainy Days</div>
        </div>
        <div style="text-align:center">
          <div style="font-size:22px;font-weight:800;color:${maxRain > 70 ? '#ef4444' : '#f59e0b'}">
            ${maxRain}%
          </div>
          <div style="font-size:10px;color:var(--text-muted);text-transform:uppercase;
                      letter-spacing:.08em">Max Rain %</div>
        </div>
        ${hotDays > 0 ? `
        <div style="text-align:center">
          <div style="font-size:22px;font-weight:800;color:#ef4444">${hotDays}</div>
          <div style="font-size:10px;color:var(--text-muted);text-transform:uppercase;
                      letter-spacing:.08em">Hot Days</div>
        </div>` : ''}
      </div>
    </div>`;

  // ── Individual day cards ───────────────────────────────────
  const dayCards = weather.map((w, i) => {
    const isRainy   = (w.rain_probability || 0) > 60;
    const isStorm   = w.condition === 'thunderstorm';
    const isHot     = (w.temp_c || 0) >= 34;
    const isSnow    = w.condition === 'snow';
    const isWind    = w.condition === 'windy';

    // Card accent colour based on condition
    const cardBorder = isStorm ? 'rgba(239,68,68,0.3)'
                     : isRainy ? 'rgba(59,130,246,0.25)'
                     : isHot   ? 'rgba(245,158,11,0.25)'
                     : isSnow  ? 'rgba(148,163,184,0.3)'
                     : 'var(--border)';
    const cardBg = isStorm ? 'rgba(239,68,68,0.04)'
                 : isRainy ? 'rgba(59,130,246,0.04)'
                 : isHot   ? 'rgba(245,158,11,0.04)'
                 : isSnow  ? 'rgba(148,163,184,0.04)'
                 : 'var(--bg-card)';

    // Temperature colour
    const tempColor = w.temp_c >= 34 ? '#ef4444'
                    : w.temp_c >= 28 ? '#f59e0b'
                    : w.temp_c >= 15 ? '#10b981'
                    : w.temp_c >= 5  ? '#3b82f6'
                    : '#818cf8';

    // Rain bar
    const rainPct   = w.rain_probability || 0;
    const rainColor = rainPct >= 70 ? '#ef4444' : rainPct >= 40 ? '#f59e0b' : '#3b82f6';

    // Feels like delta
    const feelsDelta = w.feels_like_c != null && w.temp_c != null
      ? (w.feels_like_c < w.temp_c ? `Feels ${w.temp_c - w.feels_like_c}° cooler` : '')
      : '';

    // Source indicator
    const liveIndicator = w.source === 'live'
      ? `<span style="font-size:9px;color:#10b981;font-weight:600">● Live</span>`
      : `<span style="font-size:9px;color:var(--text-muted)">○ Model</span>`;

    // Day alert badge
    const alertBadge = isStorm ? `<div style="position:absolute;top:8px;right:8px;
      padding:2px 8px;background:rgba(239,68,68,0.9);border-radius:var(--r-full);
      font-size:9px;font-weight:700;color:#fff;z-index:1">⚠ Storm</div>`
    : isHot ? `<div style="position:absolute;top:8px;right:8px;
      padding:2px 8px;background:rgba(245,158,11,0.9);border-radius:var(--r-full);
      font-size:9px;font-weight:700;color:#fff;z-index:1">🌡 Extreme heat</div>`
    : '';

    return `
      <div class="weather-card" style="background:${cardBg};border-color:${cardBorder};
                                       position:relative;overflow:hidden">
        ${alertBadge}
        <!-- Date + source -->
        <div style="display:flex;align-items:center;justify-content:space-between;
                    margin-bottom:8px">
          <div class="weather-date">${esc(w.date || '')}</div>
          ${liveIndicator}
        </div>

        <!-- Icon -->
        <div class="weather-icon-big">${w.icon || '☀️'}</div>

        <!-- Condition label -->
        <div class="weather-label" style="margin-bottom:6px">${esc(w.label || '')}</div>
        ${w.description && w.description !== w.label
          ? `<div style="font-size:10px;color:var(--text-muted);margin-bottom:6px">
               ${esc(w.description)}
             </div>` : ''}

        <!-- Temperature -->
        <div style="font-size:28px;font-weight:800;color:${tempColor};
                    font-variant-numeric:tabular-nums;line-height:1;margin-bottom:3px">
          ${w.temp_c}°C
        </div>
        <div style="font-size:10px;color:var(--text-muted);margin-bottom:8px">
          ${w.temp_f}°F
          ${feelsDelta ? ` · ${feelsDelta}` : ''}
        </div>

        <!-- Rain probability bar -->
        <div style="margin-bottom:8px">
          <div style="display:flex;justify-content:space-between;margin-bottom:3px">
            <span style="font-size:10px;color:var(--text-muted)">💧 Rain</span>
            <span style="font-size:10px;font-weight:700;color:${rainColor}">${rainPct}%</span>
          </div>
          <div style="height:4px;background:rgba(255,255,255,.06);border-radius:2px;overflow:hidden">
            <div style="width:${rainPct}%;height:100%;background:${rainColor};border-radius:2px;
                         transition:width 600ms ease"></div>
          </div>
        </div>

        <!-- Extra details -->
        <div style="display:flex;flex-direction:column;gap:3px">
          ${w.humidity != null ? `
            <div style="font-size:10px;color:var(--text-muted);display:flex;gap:4px">
              <span>💦</span><span>${w.humidity}% humidity</span>
            </div>` : ''}
          ${w.wind_kmh != null ? `
            <div style="font-size:10px;color:var(--text-muted);display:flex;gap:4px">
              <span>💨</span><span>${w.wind_kmh} km/h wind</span>
            </div>` : ''}
        </div>

        <!-- Clothing recommendation -->
        <div style="margin-top:8px;padding-top:8px;border-top:1px solid var(--border-light);
                    font-size:10px;color:var(--text-muted);line-height:1.4">
          👔 ${esc(w.clothing || '')}
        </div>
      </div>`;
  }).join('');

  container.innerHTML = summaryHtml + `
    <div style="grid-column:1/-1">
      <div style="font-size:12px;font-weight:700;text-transform:uppercase;
                  letter-spacing:.1em;color:var(--text-muted);margin-bottom:14px">
        Day-by-Day Forecast
      </div>
    </div>
    ${dayCards}`;
}

// ── Weather summary text builder ───────────────────────────────
function _buildWeatherSummary(weather, rainyDays, hotDays, avgTemp) {
  const days = weather.length;

  if (!days) return 'No weather data available.';

  const parts = [];

  if (rainyDays === 0 && hotDays === 0) {
    parts.push(`Excellent conditions for all ${days} days — mostly dry and comfortable.`);
  } else if (rainyDays > days * 0.5) {
    parts.push(`Expect rain on ${rainyDays} of ${days} days. Pack waterproof gear and plan indoor alternatives.`);
  } else if (rainyDays > 0) {
    const rainyNames = weather
      .filter(w => (w.rain_probability || 0) > 60)
      .map(w => (w.date || '').split(',')[0])
      .slice(0, 3)
      .join(', ');
    parts.push(`Mostly good weather with ${rainyDays} rainy day${rainyDays > 1 ? 's' : ''} (${rainyNames}).`);
  }

  if (hotDays > 0) {
    parts.push(`Heat warning: ${hotDays} day${hotDays > 1 ? 's' : ''} above 34°C — avoid outdoor activities between 11am–4pm.`);
  }

  if (avgTemp >= 28 && hotDays === 0) {
    parts.push(`Warm throughout at an average of ${avgTemp}°C — light clothing and sunscreen recommended.`);
  } else if (avgTemp <= 8) {
    parts.push(`Cold conditions averaging ${avgTemp}°C — pack warm layers and a waterproof jacket.`);
  }

  const storms = weather.filter(w => w.condition === 'thunderstorm').length;
  if (storms > 0) {
    parts.push(`⚠️ Thunderstorms forecast on ${storms} day${storms > 1 ? 's' : ''} — check your itinerary for outdoor activity adjustments.`);
  }

  return parts.join(' ') || `Average temperature ${avgTemp}°C over ${days} days.`;
}

// ── Expenses ───────────────────────────────────────────────────
function renderExpenses(plan) {
  const container = document.getElementById('expensePanel');
  if (!container) return;
  const expenses = plan.expenses || [];
  const budget   = plan.budget?.total_budget || 0;

  container.innerHTML = `
    <!-- Add form -->
    <div class="expense-add-form">
      <h3>Add Expense</h3>
      <div class="expense-form-row">
        <div>
          <label style="font-size:12px;color:var(--text-muted);margin-bottom:4px;display:block">Category</label>
          <select id="expCat">
            <option value="food">🍽️ Food</option>
            <option value="transport">🚌 Transport</option>
            <option value="accommodation">🏨 Hotel</option>
            <option value="attraction">🎡 Attraction</option>
            <option value="shopping">🛍️ Shopping</option>
            <option value="other">📦 Other</option>
          </select>
        </div>
        <div>
          <label style="font-size:12px;color:var(--text-muted);margin-bottom:4px;display:block">Description</label>
          <input type="text" id="expDesc" placeholder="e.g. Lunch at café"/>
        </div>
        <div>
          <label style="font-size:12px;color:var(--text-muted);margin-bottom:4px;display:block">Amount ($)</label>
          <input type="number" id="expAmount" placeholder="0.00" min="0" step="0.01"/>
        </div>
        <div>
          <label style="font-size:12px;color:var(--text-muted);margin-bottom:4px;display:block">Date</label>
          <input type="date" id="expDate"/>
        </div>
        <button class="btn-primary" onclick="addExpense()" style="align-self:flex-end">+ Add</button>
      </div>
    </div>

    <div class="expense-list" id="expenseList"></div>
    <div class="expense-summary" id="expenseSummary"></div>`;

  // Set default date to today
  const expDateEl = document.getElementById('expDate');
  if (expDateEl) expDateEl.value = new Date().toISOString().split('T')[0];

  renderExpenseList(expenses, budget);
}

function renderExpenseList(expenses, budget) {
  const list    = document.getElementById('expenseList');
  const summary = document.getElementById('expenseSummary');
  if (!list) return;

  const catColors = {
    food: '#10b981', transport: '#6366f1', accommodation: '#06b6d4',
    attraction: '#f59e0b', shopping: '#8b5cf6', other: '#64748b',
  };
  const catEmojis = {
    food: '🍽️', transport: '🚌', accommodation: '🏨',
    attraction: '🎡', shopping: '🛍️', other: '📦',
  };
  const catOptions = Object.entries(catEmojis)
    .map(([v, e]) => `<option value="${v}">${e} ${v}</option>`)
    .join('');

  if (!expenses.length) {
    list.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">📊</div>
        <h3>No expenses yet</h3>
        <p>Use the form above to start tracking your spending.</p>
      </div>`;
  } else {
    list.innerHTML = expenses.map(e => {
      const c = catColors[e.category] || '#64748b';
      return `
        <div class="expense-item" id="exp-row-${e.id}">

          <!-- View mode (default) -->
          <div id="exp-view-${e.id}" style="display:contents">
            <div class="expense-cat-badge"
                 style="background:${c}22;color:${c};border:1px solid ${c}44">
              ${catEmojis[e.category] || '📦'} ${e.category}
            </div>
            <div class="expense-desc">${esc(e.description)}</div>
            <div class="expense-date">${e.date || ''}</div>
            <div class="expense-amount">${fmt(e.amount)}</div>
            <div style="display:flex;gap:4px;flex-shrink:0">
              <button class="expense-del"
                      onclick="startEditExpense('${e.id}')"
                      title="Edit" style="color:var(--accent)">✎</button>
              <button class="expense-del"
                      onclick="confirmDeleteExpense('${e.id}', '${esc(e.description)}')"
                      title="Delete">✕</button>
            </div>
          </div>

          <!-- Edit mode (hidden until ✎ clicked) -->
          <div id="exp-edit-${e.id}" style="display:none;width:100%;
               flex-direction:column;gap:8px">
            <div style="display:grid;grid-template-columns:1fr 2fr 1fr auto;gap:8px;align-items:end">
              <select id="edit-cat-${e.id}"
                      style="background:var(--bg-3);border:1px solid var(--border);
                             border-radius:var(--r-md);padding:8px 10px;
                             color:var(--text-primary);font-size:13px;outline:none">
                ${catOptions.replace(`value="${e.category}"`, `value="${e.category}" selected`)}
              </select>
              <input id="edit-desc-${e.id}" type="text" value="${esc(e.description)}"
                     style="background:var(--bg-3);border:1px solid var(--border);
                            border-radius:var(--r-md);padding:8px 10px;
                            color:var(--text-primary);font-size:13px;outline:none"/>
              <input id="edit-amount-${e.id}" type="number" value="${e.amount}"
                     min="0" step="0.01"
                     style="background:var(--bg-3);border:1px solid var(--border);
                            border-radius:var(--r-md);padding:8px 10px;
                            color:var(--text-primary);font-size:13px;outline:none"/>
              <div style="display:flex;gap:4px">
                <button onclick="saveEditExpense('${e.id}')"
                        style="padding:7px 12px;background:var(--primary);border:none;
                               border-radius:var(--r-md);color:#fff;font-size:12px;
                               font-weight:700;cursor:pointer">Save</button>
                <button onclick="cancelEditExpense('${e.id}')"
                        style="padding:7px 12px;background:rgba(255,255,255,.06);
                               border:1px solid var(--border);border-radius:var(--r-md);
                               color:var(--text-secondary);font-size:12px;cursor:pointer">
                  Cancel
                </button>
              </div>
            </div>
          </div>

        </div>`;
    }).join('');
  }

  // ── Summary totals ─────────────────────────────────────────
  const total     = expenses.reduce((s, e) => s + (e.amount || 0), 0);
  const remaining = budget - total;
  const pct       = budget > 0 ? Math.min(total / budget * 100, 100) : 0;

  // Category breakdown
  const byCat = {};
  expenses.forEach(e => {
    byCat[e.category] = (byCat[e.category] || 0) + e.amount;
  });
  const catRows = Object.entries(byCat).sort((a,b) => b[1]-a[1]).map(([cat, amt]) => {
    const c = catColors[cat] || '#64748b';
    const barPct = total > 0 ? Math.round(amt / total * 100) : 0;
    return `
      <div style="display:flex;align-items:center;gap:10px;padding:6px 0;
                  border-bottom:1px solid var(--border-light)">
        <span style="font-size:11px;color:var(--text-secondary);min-width:90px;
                     text-transform:capitalize">${catEmojis[cat]||'📦'} ${cat}</span>
        <div style="flex:1;height:5px;background:rgba(255,255,255,.06);
                    border-radius:3px;overflow:hidden">
          <div style="width:${barPct}%;height:100%;background:${c};border-radius:3px"></div>
        </div>
        <span style="font-size:12px;font-weight:700;color:var(--text-primary);
                     min-width:56px;text-align:right">${fmt(amt)}</span>
      </div>`;
  }).join('');

  if (summary) {
    summary.innerHTML = `
      <div class="expense-summary" style="margin-top:16px">
        <!-- Budget bar -->
        <div style="margin-bottom:16px">
          <div style="display:flex;justify-content:space-between;margin-bottom:6px">
            <span style="font-size:12px;color:var(--text-muted)">Budget used</span>
            <span style="font-size:12px;font-weight:700;
                         color:${pct >= 90 ? 'var(--danger)' : 'var(--text-primary)'}">
              ${pct.toFixed(0)}%
            </span>
          </div>
          <div style="height:6px;background:rgba(255,255,255,.06);
                      border-radius:3px;overflow:hidden">
            <div style="width:${pct}%;height:100%;border-radius:3px;
                         background:${pct >= 90 ? 'var(--danger)' : 'linear-gradient(90deg,var(--primary),var(--accent))'}"></div>
          </div>
        </div>

        <!-- Totals -->
        <div class="expense-summary-row">
          <span>Total Spent</span><strong>${fmt(total)}</strong>
        </div>
        <div class="expense-summary-row">
          <span>Total Budget</span><strong>${fmt(budget)}</strong>
        </div>
        <div class="expense-summary-row"
             style="color:${remaining >= 0 ? 'var(--success)' : 'var(--danger)'}">
          <span>Remaining</span><strong>${fmt(remaining)}</strong>
        </div>

        <!-- Category breakdown -->
        ${catRows ? `
        <div style="margin-top:16px">
          <div style="font-size:11px;font-weight:700;text-transform:uppercase;
                      letter-spacing:.08em;color:var(--text-muted);margin-bottom:8px">
            By Category
          </div>
          ${catRows}
        </div>` : ''}
      </div>`;
  }
}

// ── Edit helpers ───────────────────────────────────────────────
function startEditExpense(id) {
  document.getElementById(`exp-view-${id}`).style.display = 'none';
  const editEl = document.getElementById(`exp-edit-${id}`);
  editEl.style.display = 'flex';
  // Focus description
  document.getElementById(`edit-desc-${id}`)?.focus();
}

function cancelEditExpense(id) {
  document.getElementById(`exp-edit-${id}`).style.display = 'none';
  document.getElementById(`exp-view-${id}`).style.display = 'contents';
}

async function saveEditExpense(id) {
  if (!currentTripId) return;
  const cat    = document.getElementById(`edit-cat-${id}`)?.value    || 'other';
  const desc   = document.getElementById(`edit-desc-${id}`)?.value.trim() || '';
  const amount = parseFloat(document.getElementById(`edit-amount-${id}`)?.value || '0');

  if (!desc)   { showToast('Description cannot be empty', 'error'); return; }
  if (!amount) { showToast('Enter a valid amount', 'error'); return; }

  try {
    const res  = await fetch(`/api/trips/${currentTripId}/expenses/${id}`, {
      method:  'PUT',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ category: cat, description: desc, amount }),
    });
    const data = await res.json();
    if (data.status === 'success') {
      // Update local state
      const idx = currentPlan.expenses.findIndex(e => e.id === id);
      if (idx !== -1) currentPlan.expenses[idx] = data.expense;
      renderExpenseList(currentPlan.expenses, currentPlan.budget?.total_budget || 0);
      showToast('Expense updated', 'success');
    } else {
      showToast(data.message || 'Update failed', 'error');
    }
  } catch (_) {
    showToast('Failed to update expense', 'error');
  }
}

// ── Delete with confirmation ───────────────────────────────────
function confirmDeleteExpense(id, desc) {
  // Inline confirm inside the row — avoids browser dialog
  const row = document.getElementById(`exp-row-${id}`);
  if (!row) return;
  const view = document.getElementById(`exp-view-${id}`);
  view.style.display = 'none';

  // Insert confirm bar
  const bar = document.createElement('div');
  bar.id = `exp-confirm-${id}`;
  bar.style.cssText = 'display:flex;align-items:center;gap:10px;width:100%;padding:2px 0';
  bar.innerHTML = `
    <span style="font-size:12px;color:var(--warning);flex:1">
      Delete "<strong>${esc(desc)}</strong>"?
    </span>
    <button onclick="deleteExpense('${id}')"
            style="padding:6px 14px;background:var(--danger);border:none;
                   border-radius:var(--r-md);color:#fff;font-size:12px;
                   font-weight:700;cursor:pointer">
      Delete
    </button>
    <button onclick="cancelDeleteExpense('${id}')"
            style="padding:6px 12px;background:rgba(255,255,255,.06);
                   border:1px solid var(--border);border-radius:var(--r-md);
                   color:var(--text-secondary);font-size:12px;cursor:pointer">
      Cancel
    </button>`;
  row.appendChild(bar);
}

function cancelDeleteExpense(id) {
  document.getElementById(`exp-confirm-${id}`)?.remove();
  const view = document.getElementById(`exp-view-${id}`);
  if (view) view.style.display = 'contents';
}

async function addExpense() {
  if (!currentTripId) {
    showToast('Generate your trip plan first, then save it to track expenses.', 'info');
    return;
  }
  const cat    = document.getElementById('expCat')?.value          || 'other';
  const desc   = document.getElementById('expDesc')?.value.trim()  || '';
  const amount = parseFloat(document.getElementById('expAmount')?.value || '0');
  const date   = document.getElementById('expDate')?.value
              || new Date().toISOString().split('T')[0];

  if (!desc)   { showToast('Enter a description', 'error'); return; }
  if (!amount) { showToast('Enter a valid amount', 'error'); return; }

  try {
    const res  = await fetch(`/api/trips/${currentTripId}/expenses`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ category: cat, description: desc, amount, date }),
    });
    const data = await res.json();
    if (data.status === 'success') {
      if (!currentPlan.expenses) currentPlan.expenses = [];
      currentPlan.expenses.push(data.expense);
      renderExpenseList(currentPlan.expenses, currentPlan.budget?.total_budget || 0);
      document.getElementById('expDesc').value   = '';
      document.getElementById('expAmount').value = '';
      showToast('Expense added', 'success');
    } else {
      showToast(data.message || 'Failed to add expense', 'error');
    }
  } catch (_) {
    showToast('Failed to add expense', 'error');
  }
}

async function deleteExpense(expId) {
  if (!currentTripId) return;
  try {
    const res = await fetch(`/api/trips/${currentTripId}/expenses/${expId}`,
                            { method: 'DELETE' });
    const data = await res.json();
    if (data.status === 'success') {
      currentPlan.expenses = (currentPlan.expenses || []).filter(e => e.id !== expId);
      renderExpenseList(currentPlan.expenses, currentPlan.budget?.total_budget || 0);
      showToast('Expense deleted', 'info');
    }
  } catch (_) {
    showToast('Failed to delete expense', 'error');
  }
}

// ── Save to dashboard ──────────────────────────────────────────
async function saveToDashboard() {
  if (!App.user) {
    showToast('Log in to save trips to your dashboard', 'info');
    openModal('loginModal');
    return;
  }
  showToast('Trip saved to dashboard!', 'success');
  setTimeout(() => window.location.href = '/dashboard', 1200);
}

// ── Reset planner ──────────────────────────────────────────────
function resetPlanner() {
  currentPlan   = null;
  currentTripId = null;
  selectedInterests = [];
  document.querySelectorAll('.interest-card').forEach(c => c.classList.remove('selected'));
  document.getElementById('resultsContainer').style.display = 'none';
  document.getElementById('plannerContainer').style.display = '';
  goToStep(1);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Routes ─────────────────────────────────────────────────────
function renderRoutes(plan) {
  const container = document.getElementById('routesContainer');
  if (!container) return;

  const routes = plan.routes;
  if (!routes || !routes.fastest) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🗺️</div>
        <h3>No route data available</h3>
        <p>Routes are generated based on your destination and transport preference.</p>
      </div>`;
    return;
  }

  const dest     = routes.destination || plan.destination?.name || '';
  const routeList = [
    { key: 'fastest',  data: routes.fastest  },
    { key: 'cheapest', data: routes.cheapest },
    { key: 'scenic',   data: routes.scenic   },
  ].filter(r => r.data);

  // ── Header ────────────────────────────────────────────────────
  const headerHtml = `
    <div style="background:var(--bg-card);border:1px solid var(--border);
                border-radius:var(--r-xl);padding:20px 24px;margin-bottom:20px">
      <div style="font-size:11px;font-weight:700;text-transform:uppercase;
                  letter-spacing:.1em;color:var(--text-muted);margin-bottom:6px">
        🗺️ Route Planner — ${esc(dest)}
      </div>
      <div style="font-size:14px;color:var(--text-secondary);line-height:1.6">
        Three route options have been calculated for your trip. Each opens
        directly in Google Maps with your waypoints pre-loaded.
      </div>
    </div>`;

  // ── Route cards ───────────────────────────────────────────────
  const routeColors = {
    fastest:  { border: 'rgba(6,182,212,0.35)',  bg: 'rgba(6,182,212,0.04)',  accent: '#06b6d4' },
    cheapest: { border: 'rgba(16,185,129,0.35)', bg: 'rgba(16,185,129,0.04)', accent: '#10b981' },
    scenic:   { border: 'rgba(139,92,246,0.35)', bg: 'rgba(139,92,246,0.04)', accent: '#8b5cf6' },
  };

  const cardsHtml = routeList.map(({ key, data }) => {
    const col = routeColors[key] || routeColors.scenic;
    const travelMin = data.total_travel_min || 0;
    const travelLabel = travelMin >= 60
      ? `${Math.floor(travelMin / 60)}h ${travelMin % 60}m`
      : `${travelMin}m`;

    // Waypoint list
    const waypointRows = (data.waypoints || []).map((wp, i) => `
      <div style="display:flex;align-items:flex-start;gap:10px;padding:8px 0;
                  border-bottom:1px solid var(--border-light)">
        <div style="width:22px;height:22px;border-radius:50%;background:${col.accent};
                    display:flex;align-items:center;justify-content:center;
                    font-size:10px;font-weight:800;color:#fff;flex-shrink:0;margin-top:1px">
          ${wp.order}
        </div>
        <div style="flex:1">
          <div style="font-size:13px;font-weight:600;color:var(--text-primary)">
            ${esc(wp.name)}
          </div>
          <div style="font-size:11px;color:var(--text-muted);margin-top:1px">
            ⏱ ${esc(wp.duration)}
            ${wp.cost > 0 ? ` · ${fmt(wp.cost)} entry` : ' · Free entry'}
          </div>
          ${wp.desc ? `<div style="font-size:11px;color:var(--text-muted);
                                   margin-top:2px;line-height:1.4">${esc(wp.desc)}</div>` : ''}
        </div>
      </div>`).join('');

    return `
      <div style="background:${col.bg};border:1px solid ${col.border};
                  border-radius:var(--r-xl);padding:20px 24px;margin-bottom:16px;
                  position:relative;overflow:hidden">
        <!-- Top accent line -->
        <div style="position:absolute;top:0;left:0;right:0;height:2px;
                    background:${col.accent}"></div>

        <!-- Header row -->
        <div style="display:flex;align-items:flex-start;justify-content:space-between;
                    gap:16px;flex-wrap:wrap;margin-bottom:14px">
          <div>
            <div style="font-size:18px;font-weight:800;color:var(--text-primary);
                        margin-bottom:3px">
              ${data.icon} ${esc(data.label)}
            </div>
            <div style="font-size:13px;color:var(--text-secondary)">
              ${esc(data.description)}
            </div>
          </div>
          <!-- Stats badges -->
          <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-start">
            <span style="padding:4px 10px;background:${col.accent}18;
                         border:1px solid ${col.accent}40;border-radius:var(--r-full);
                         font-size:11px;font-weight:700;color:${col.accent};
                         white-space:nowrap">
              🚌 ${esc(data.transport)}
            </span>
            ${travelMin > 0 ? `
            <span style="padding:4px 10px;background:rgba(255,255,255,.04);
                         border:1px solid var(--border);border-radius:var(--r-full);
                         font-size:11px;font-weight:600;color:var(--text-secondary);
                         white-space:nowrap">
              ⏱ ${travelLabel} transit
            </span>` : ''}
            <span style="padding:4px 10px;background:rgba(255,255,255,.04);
                         border:1px solid var(--border);border-radius:var(--r-full);
                         font-size:11px;font-weight:600;color:var(--text-secondary);
                         white-space:nowrap">
              💰 ${esc(data.cost_note)}
            </span>
          </div>
        </div>

        <!-- Tip -->
        <div style="background:rgba(255,255,255,.03);border-left:3px solid ${col.accent};
                    border-radius:0 var(--r-sm) var(--r-sm) 0;
                    padding:8px 12px;margin-bottom:14px;
                    font-size:12px;color:var(--text-secondary);line-height:1.5">
          💡 ${esc(data.tip)}
        </div>

        <!-- Waypoints -->
        ${waypointRows ? `
        <div style="margin-bottom:14px">
          <div style="font-size:10px;font-weight:700;text-transform:uppercase;
                      letter-spacing:.08em;color:var(--text-muted);margin-bottom:8px">
            Waypoints
          </div>
          ${waypointRows}
        </div>` : ''}

        <!-- Open in Maps CTA -->
        <a href="${esc(data.maps_url || '#')}" target="_blank" rel="noopener"
           style="display:flex;align-items:center;justify-content:center;gap:8px;
                  padding:11px 20px;background:${col.accent};color:#fff;
                  border-radius:var(--r-md);font-size:13px;font-weight:700;
                  text-decoration:none;transition:opacity var(--t-fast);width:100%;
                  box-sizing:border-box"
           onmouseover="this.style.opacity='.85'"
           onmouseout="this.style.opacity='1'">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" stroke-width="2.5">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
          Open in Google Maps →
        </a>
      </div>`;
  }).join('');

  container.innerHTML = headerHtml + cardsHtml;
}
