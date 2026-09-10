/* ═══════════════════════════════════════════════════════════
   TripPilot AI — Dashboard Page Logic
   ═══════════════════════════════════════════════════════════ */

'use strict';

const SAVED_DESTS_KEY = 'trippilot_saved_dests';

document.addEventListener('DOMContentLoaded', () => {
  setGreeting();
  loadDashboard();
});

// ── Greeting ───────────────────────────────────────────────────
function setGreeting() {
  const h = new Date().getHours();
  const greet = h < 12 ? 'morning' : h < 18 ? 'afternoon' : 'evening';
  const el = document.getElementById('timeGreeting');
  if (el) el.textContent = greet;
}

// ── Load dashboard data ────────────────────────────────────────
async function loadDashboard() {
  // Auth check
  try {
    const res = await fetch('/api/auth/me');
    if (res.ok) {
      const data = await res.json();
      App.user = data.user;
      renderNavUser(data.user);
      setUserInfo(data.user);
    }
  } catch (_) {}

  // Fire all 4 data loaders in parallel — saves ~3× sequential wait time
  await Promise.all([
    loadTrips(),
    loadAnalytics(),
    loadSavedDests(),
    loadAiSuggestions(),
  ]);
}

function setUserInfo(user) {
  const nameEl  = document.getElementById('userName');
  const emailEl = document.getElementById('userEmail');
  const avEl    = document.getElementById('userAvatar');
  const wNameEl = document.getElementById('welcomeName');
  if (nameEl)  nameEl.textContent  = user.name  || 'Traveler';
  if (emailEl) emailEl.textContent = user.email || '';
  if (avEl)    avEl.textContent    = (user.name || 'U')[0].toUpperCase();
  if (wNameEl) wNameEl.textContent = user.name?.split(' ')[0] || 'Traveler';
}

// ── Sidebar tab navigation ─────────────────────────────────────
function showDashTab(name, linkEl) {
  document.querySelectorAll('.dash-tab').forEach(t => t.classList.remove('active'));
  document.getElementById(`tab-${name}`)?.classList.add('active');
  document.querySelectorAll('.snav-item').forEach(l => l.classList.remove('active'));
  if (linkEl) linkEl.classList.add('active');
  return false;
}

// ── Load trips ─────────────────────────────────────────────────
async function loadTrips() {
  try {
    const res  = await fetch('/api/trips');
    const data = await res.json();
    const trips = data.trips || [];
    renderRecentTrips(trips.slice(0, 3));
    renderAllTrips(trips);
    updateStatCards(trips);
  } catch (_) {
    renderRecentTrips([]);
    renderAllTrips([]);
  }
}

function updateStatCards(trips) {
  document.getElementById('statTrips').textContent = trips.length;
  document.getElementById('statDests').textContent = new Set(trips.map(t => t.destination)).size;
  document.getElementById('statDays').textContent  = trips.reduce((s, t) => s + (t.days || 0), 0);
  // Spent will be updated by analytics
}

function renderRecentTrips(trips) {
  const container = document.getElementById('recentTrips');
  if (!container) return;
  if (!trips.length) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">✈️</div>
        <h3>No trips yet</h3>
        <p>Start planning your first adventure.</p>
        <a href="/planner.html" class="btn-primary">Plan a Trip →</a>
      </div>`;
    return;
  }
  container.innerHTML = trips.map(t => renderTripRow(t, false)).join('');
}

function renderAllTrips(trips) {
  const container = document.getElementById('allTripsContainer');
  if (!container) return;
  if (!trips.length) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🗺️</div>
        <h3>No trips planned yet</h3>
        <p>Your saved trips will appear here.</p>
        <a href="/planner.html" class="btn-primary" style="display:inline-flex">Plan a Trip →</a>
      </div>`;
    return;
  }
  container.innerHTML = trips.map(t => renderTripRow(t, true)).join('');
}

function renderTripRow(t, full) {
  // DEST_EMOJIS is defined in main.js
  const emoji = DEST_EMOJIS[(t.destination||'').toLowerCase()] || '🌍';
  const deleteBtn = full
    ? `<button class="trip-btn trip-btn-delete" onclick="deleteTrip('${t.id}',event)">Delete</button>` : '';

  return `
    <div class="trip-row" onclick="viewTrip('${t.id}')">
      <div class="trip-dest-icon">${emoji}</div>
      <div class="trip-info">
        <div class="trip-dest">${esc(t.destination)}</div>
        <div class="trip-meta">${t.start_date || ''} · ${t.days} days</div>
      </div>
      <span class="trip-type-badge">${t.travel_type || 'trip'}</span>
      <div class="trip-budget">${fmt(t.budget)}</div>
      <div class="trip-actions">
        <button class="trip-btn trip-btn-view" onclick="viewTrip('${t.id}');event.stopPropagation()">View Plan</button>
        ${deleteBtn}
      </div>
    </div>`;
}

// ── View trip modal ────────────────────────────────────────────
async function viewTrip(tripId) {
  const modal   = document.getElementById('tripModal');
  const content = document.getElementById('tripModalContent');
  if (!modal || !content) return;

  content.innerHTML = `<div style="text-align:center;padding:40px;color:var(--text-muted)">
    <span class="spinner" style="display:inline-block;width:28px;height:28px;border:3px solid rgba(255,255,255,0.1);border-top-color:var(--primary);border-radius:50%;animation:spin 0.7s linear infinite;margin-bottom:12px"></span>
    <p>Loading trip...</p></div>`;
  openModal('tripModal');

  try {
    const res  = await fetch(`/api/trips/${tripId}`);
    const data = await res.json();
    if (data.status === 'success') {
      renderTripModal(data.trip);
    } else {
      content.innerHTML = `<p style="color:var(--danger)">Trip not found.</p>`;
    }
  } catch (_) {
    content.innerHTML = `<p style="color:var(--danger)">Failed to load trip.</p>`;
  }
}

function renderTripModal(trip) {
  const content = document.getElementById('tripModalContent');
  if (!content) return;
  const plan = trip.plan || {};
  const b    = plan.budget || {};
  const itinerary = plan.itinerary || [];

  const dayCards = itinerary.slice(0, 3).map(day => {
    const acts = (day.timeline || []).slice(0, 4)
      .map(t => `<li style="font-size:13px;color:var(--text-secondary);padding:2px 0">${t.time} — ${esc(t.activity)}</li>`)
      .join('');
    return `
      <div style="background:var(--bg-3);border:1px solid var(--border);border-radius:var(--r-lg);padding:16px;margin-bottom:12px">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
          <div style="background:var(--primary);color:#fff;width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px">D${day.day}</div>
          <div>
            <div style="font-weight:700;color:var(--text-primary)">${esc(day.theme)}</div>
            <div style="font-size:12px;color:var(--text-muted)">${esc(day.date)}</div>
          </div>
          <div style="margin-left:auto;font-size:14px;font-weight:700;color:var(--text-primary)">${fmt(day.daily_spending)}</div>
        </div>
        <ul style="list-style:none;padding:0;margin:0">${acts}</ul>
      </div>`;
  }).join('');

  const moreNote = itinerary.length > 3
    ? `<p style="text-align:center;font-size:13px;color:var(--text-muted);margin-top:8px">+${itinerary.length - 3} more days in full plan</p>` : '';

  content.innerHTML = `
    <div class="trip-modal-header">
      <div>
        <div class="trip-modal-title">${esc(trip.destination)} Trip</div>
        <div class="trip-modal-sub">${trip.start_date} · ${trip.days} days · ${trip.travel_type} · ${fmt(trip.budget)}</div>
      </div>
      <a href="/planner.html" class="btn-primary">Edit in Planner</a>
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:12px;margin-bottom:24px">
      <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r-lg);padding:14px">
        <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--text-muted);margin-bottom:6px">Budget</div>
        <div style="font-size:20px;font-weight:800;color:var(--text-primary)">${fmt(b.total_budget)}</div>
      </div>
      <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r-lg);padding:14px">
        <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--text-muted);margin-bottom:6px">Estimated</div>
        <div style="font-size:20px;font-weight:800;color:var(--text-primary)">${fmt(b.estimated_total)}</div>
      </div>
      <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r-lg);padding:14px">
        <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--text-muted);margin-bottom:6px">Days</div>
        <div style="font-size:20px;font-weight:800;color:var(--text-primary)">${trip.days}</div>
      </div>
      <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r-lg);padding:14px">
        <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--text-muted);margin-bottom:6px">Travelers</div>
        <div style="font-size:20px;font-weight:800;color:var(--text-primary)">${trip.travelers || 1}</div>
      </div>
    </div>
    <h3 style="font-size:16px;font-weight:700;color:var(--text-primary);margin-bottom:16px">Itinerary Preview</h3>
    ${dayCards}
    ${moreNote}`;
}

// ── Delete trip ────────────────────────────────────────────────
async function deleteTrip(tripId, e) {
  if (e) e.stopPropagation();
  if (!confirm('Delete this trip? This cannot be undone.')) return;
  try {
    await fetch(`/api/trips/${tripId}`, { method: 'DELETE' });
    showToast('Trip deleted', 'info');
    loadTrips();
  } catch (_) {
    showToast('Failed to delete trip', 'error');
  }
}

// ── Analytics ─────────────────────────────────────────────────
async function loadAnalytics() {
  const container = document.getElementById('analyticsContainer');
  if (!container) return;
  try {
    const res  = await fetch('/api/analytics/summary');
    const data = await res.json();
    const s    = data.summary || {};

    // Update stat card
    const statSpent = document.getElementById('statSpent');
    if (statSpent) statSpent.textContent = fmt(s.total_spent || 0);

    const catColors = ['#6366f1','#06b6d4','#10b981','#f59e0b','#8b5cf6','#ef4444'];
    const cats      = Object.entries(s.spending_by_category || {}).sort((a,b) => b[1]-a[1]);
    const maxVal    = cats.reduce((m, [,v]) => Math.max(m, v), 1);
    const total     = cats.reduce((s, [,v]) => s + v, 0);

    // ── Category bar rows ─────────────────────────────────
    const catRows = cats.map(([cat, val], i) => {
      const pct = Math.round(val / maxVal * 100);
      const color = catColors[i % catColors.length];
      return `
        <div class="category-bar-row">
          <div class="cat-label" style="display:flex;align-items:center;gap:6px">
            <span style="width:8px;height:8px;border-radius:2px;background:${color};display:inline-block;flex-shrink:0"></span>
            ${cat.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}
          </div>
          <div class="cat-bar-wrap">
            <div class="cat-bar" style="width:${pct}%;background:${color};transition:width 600ms ease"></div>
          </div>
          <div class="cat-amount">${fmt(val)}</div>
        </div>`;
    }).join('');

    // ── SVG donut for spending by category ────────────────
    const donutHtml = cats.length ? (() => {
      const radius  = 44;
      const cx = 54, cy = 54;
      const circumf = 2 * Math.PI * radius;
      let offset = 0;
      const slices = cats.map(([cat, val], i) => {
        const frac  = val / total;
        const dash  = frac * circumf;
        const color = catColors[i % catColors.length];
        const slice = `<circle cx="${cx}" cy="${cy}" r="${radius}" fill="none"
          stroke="${color}" stroke-width="14"
          stroke-dasharray="${dash.toFixed(2)} ${(circumf-dash).toFixed(2)}"
          stroke-dashoffset="${(-offset + circumf/4).toFixed(2)}">
          <title>${cat}: ${fmt(val)}</title>
        </circle>`;
        offset += dash;
        return slice;
      }).join('');
      return `<svg width="108" height="108" viewBox="0 0 108 108">
        <circle cx="${cx}" cy="${cy}" r="${radius}" fill="none"
                stroke="rgba(255,255,255,.06)" stroke-width="14"/>
        ${slices}
        <text x="${cx}" y="${cy+4}" text-anchor="middle"
              fill="var(--text-primary)" font-size="11" font-weight="800"
              font-family="Inter,sans-serif">${fmt(total)}</text>
      </svg>`;
    })() : '';

    container.innerHTML = `
      <div class="analytics-grid">

        <!-- Spending by category -->
        <div class="analytics-card" style="grid-column:span 2">
          <h3>Spending by Category</h3>
          ${cats.length ? `
            <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap">
              ${donutHtml ? `<div style="flex-shrink:0">${donutHtml}</div>` : ''}
              <div style="flex:1;min-width:200px">${catRows}</div>
            </div>` :
            '<p style="color:var(--text-muted);font-size:14px">No expense data yet. Add expenses to your trips to see spending analytics.</p>'}
        </div>

        <!-- Overview card -->
        <div class="analytics-card">
          <h3>Trip Overview</h3>
          <div style="display:flex;flex-direction:column;gap:14px;margin-top:10px">
            ${[
              ['Total Trips',    s.total_trips    || 0, '✈️'],
              ['Destinations',   s.destinations_visited || 0, '🌍'],
              ['Days Travelled', s.total_days     || 0, '📅'],
              ['Total Spent',    fmt(s.total_spent || 0), '💰'],
            ].map(([label, val, icon]) => `
              <div style="display:flex;align-items:center;justify-content:space-between">
                <span style="font-size:13px;color:var(--text-secondary);display:flex;align-items:center;gap:6px">
                  <span>${icon}</span>${label}
                </span>
                <strong style="font-size:14px;color:var(--text-primary)">${val}</strong>
              </div>`).join('')}
          </div>
        </div>

      </div>`;
  } catch (_) {
    container.innerHTML = '<p style="color:var(--text-muted)">Analytics unavailable.</p>';
  }
}

// ── Saved Destinations ─────────────────────────────────────────
function loadSavedDests() {
  const container = document.getElementById('savedDestContainer');
  if (!container) return;
  const saved = JSON.parse(localStorage.getItem(SAVED_DESTS_KEY) || '[]');
  if (!saved.length) {
    container.innerHTML = `
      <div class="empty-state" style="grid-column:1/-1">
        <div class="empty-state-icon">🔖</div>
        <h3>No saved destinations</h3>
        <p>Explore destinations and save your favourites.</p>
        <a href="/explore.html" class="btn-primary" style="display:inline-flex">Explore →</a>
      </div>`;
    return;
  }
  container.innerHTML = saved.map(d => {
    const imgUrl = (typeof DEST_IMAGES !== 'undefined' && DEST_IMAGES[(d.name||'').toLowerCase()])
      || 'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=400&q=80';
    return `
    <div class="dest-card" onclick="window.location.href='/planner.html?dest=${encodeURIComponent(d.name)}'">
      <div class="dest-card-img" style="height:140px">
        <img src="${imgUrl}" alt="${d.name}" loading="lazy" style="width:100%;height:100%;object-fit:cover" onerror="this.style.display='none'"/>
        <div class="dest-card-img-overlay"></div>
      </div>
      <div class="dest-card-body">
        <div class="dest-card-country">${d.country || ''}</div>
        <div class="dest-card-name">${d.name}</div>
      </div>
    </div>`;
  }).join('');
}

// ── AI Suggestions ─────────────────────────────────────────────
function loadAiSuggestions() {
  const container = document.getElementById('aiSuggestions');
  if (!container) return;
  const suggestions = [
    { icon: '🌸', text: 'Spring is the best time to visit Japan — cherry blossoms in full bloom.' },
    { icon: '☀️', text: 'Dubai offers great deals in summer for budget-conscious luxury travelers.' },
    { icon: '🍂', text: 'October in Paris offers mild weather with smaller crowds.' },
    { icon: '🌊', text: 'Book Maldives overwater bungalows 3–6 months in advance for best rates.' },
  ];
  container.innerHTML = suggestions.map(s => `
    <div class="ai-suggestion-card">
      <div class="ai-suggestion-icon">${s.icon}</div>
      ${s.text}
    </div>`).join('');
}
