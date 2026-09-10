/* ═══════════════════════════════════════════════════════════
   TripPilot AI — Explore Page Logic

   Recommendation engine features:
   ✅ Personalized by interests (Jaccard match, 0–40 pts)
   ✅ Personalized by budget level (0–20 pts)
   ✅ Personalized by travel style (0–20 pts)
   ✅ Season/timing aware (0–10 pts)
   ✅ Group-size aware (0–10 pts)
   ✅ Score breakdown bars displayed per card
   ✅ Scores recalculate dynamically on filter change
   ✅ Why-reasons generated per destination
   ═══════════════════════════════════════════════════════════ */

'use strict';

let selectedFilterInterests = [];
// Prevents chip-change handlers from firing loadRecommendations() during the
// initial DOMContentLoaded render — avoids a double API call on page load.
let _initialLoad = true;

document.addEventListener('DOMContentLoaded', async () => {
  loadAllDests();
  await loadRecommendations();
  _initialLoad = false;  // chips may now trigger reloads freely
});

// ── Filter chip helpers ────────────────────────────────────────
function selectChipExplore(el, field) {
  el.closest('.chip-group').querySelectorAll('.chip').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
  const hidden = document.getElementById(field);
  if (hidden) hidden.value = el.dataset.value;
  // Only reload after the initial render is complete
  if (!_initialLoad) loadRecommendations();
}

function toggleInterestFilter(el) {
  const val = el.dataset.value;
  if (selectedFilterInterests.includes(val)) {
    selectedFilterInterests = selectedFilterInterests.filter(i => i !== val);
    el.classList.remove('selected');
  } else {
    selectedFilterInterests.push(val);
    el.classList.add('selected');
  }
  // Only reload after the initial render is complete
  if (!_initialLoad) loadRecommendations();
}

// ── Load all destinations ──────────────────────────────────────
async function loadAllDests() {
  const grid = document.getElementById('allDestGrid');
  if (!grid) return;
  try {
    const res  = await fetch('/api/destinations');
    const data = await res.json();
    grid.innerHTML = (data.destinations || []).map(renderDestCard).join('');
  } catch (_) {
    grid.innerHTML = '<p style="color:var(--text-muted)">Could not load destinations.</p>';
  }
}

// ── Load AI recommendations (called on init + every filter change) ────
let _recsDebounce = null;
async function loadRecommendations() {
  clearTimeout(_recsDebounce);
  _recsDebounce = setTimeout(_doLoadRecommendations, 350);
}

async function _doLoadRecommendations() {
  const grid = document.getElementById('exploreDestGrid');
  if (!grid) return;

  grid.innerHTML = `
    <div style="grid-column:1/-1;display:flex;align-items:center;gap:12px;
                color:var(--text-muted);padding:24px 0;">
      <span class="spinner" style="display:inline-block;width:18px;height:18px;
            border:2px solid rgba(255,255,255,0.1);border-top-color:var(--primary);
            border-radius:50%;animation:spin 0.7s linear infinite"></span>
      <span>Calculating your matches…</span>
    </div>`;

  const budgetLevel = document.getElementById('budgetLevel')?.value || 'medium';
  const travelType  = document.getElementById('travelTypeE')?.value  || 'solo';
  const today       = new Date().toISOString().split('T')[0];

  try {
    const res = await fetch('/api/recommendations', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        interests    : selectedFilterInterests,
        budget_level : budgetLevel,
        travel_type  : travelType,
        travelers    : 1,
        start_date   : today,
      }),
    });
    const data = await res.json();
    const recs = data.recommendations || [];

    if (!recs.length) {
      grid.innerHTML = `<p style="color:var(--text-muted);grid-column:1/-1;
        text-align:center;padding:40px 0">
        No strong matches for these filters. Try adjusting your preferences.</p>`;
      return;
    }
    grid.innerHTML = recs.map(renderRecommendationCard).join('');

  } catch (_) {
    grid.innerHTML = `<p style="color:var(--text-muted);grid-column:1/-1;
      text-align:center;padding:40px 0">Could not load recommendations.</p>`;
  }
}

// ── Shared emoji helper ────────────────────────────────────────
function getEmoji(d) {
  return DEST_EMOJIS[d.name?.toLowerCase()]
      || DEST_EMOJIS[(d.id || '').replace('_', ' ')]
      || '🌍';
}

// ── Get destination image (uses DEST_IMAGES from main.js) ──────
function getDestImg(d) {
  const key = (d.name || '').toLowerCase();
  if (typeof DEST_IMAGES !== 'undefined' && DEST_IMAGES[key]) return DEST_IMAGES[key];
  return `https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=400&q=80`;
}

// ── All-destinations card (no match score) ─────────────────────
function renderDestCard(d) {
  const imgUrl = getDestImg(d);
  const tags   = (d.tags || []).slice(0, 3).map(t => `<span class="dest-tag">${t}</span>`).join('');
  const budget = d.daily_budget?.low || 0;

  const diffColors = { easy: '#00e5a0', moderate: '#ffd93d', hard: '#ff6b6b' };
  const diffColor  = diffColors[d.difficulty] || '#e040fb';

  return `
    <div class="dest-card"
         onclick="window.location.href='/planner.html?dest=${encodeURIComponent(d.name)}'">
      <div class="dest-card-img">
        <img src="${imgUrl}" alt="${d.name}" loading="lazy" onerror="this.style.display='none'"/>
        <div class="dest-card-img-overlay"></div>
        <div class="dest-card-match"
             style="background:${diffColor}cc;text-transform:capitalize">
          ${d.difficulty || 'moderate'}
        </div>
      </div>
      <div class="dest-card-body">
        <div class="dest-card-country">${d.country || ''}</div>
        <div class="dest-card-name">${d.name}</div>
        <div class="dest-card-desc">${d.description || ''}</div>
        <div class="dest-card-footer">
          <div class="dest-card-tags">${tags}</div>
          <div class="dest-card-cost">From <strong>$${budget}</strong>/day</div>
        </div>
      </div>
    </div>`;
}

// ── Recommendation card — full match % + 5-dimension breakdown ─
function renderRecommendationCard(d) {
  const match = d.match_pct || 0;
  const tags  = (d.tags || []).slice(0, 3)
                  .map(t => `<span class="dest-tag">${t}</span>`).join('');

  // Match badge colour: green ≥70, amber 45–69, pink <45
  const matchColor = match >= 70 ? '#00e5a0' : match >= 45 ? '#ffd93d' : '#e040fb';

  // Safety icon
  const safetyIcons = { 'very safe': '🟢', safe: '🟡', moderate: '🟠', unsafe: '🔴' };
  const safetyIcon  = safetyIcons[d.safety] || '⚪';

  // Why-reasons — structured list
  const whyHtml = (d.why || []).slice(0, 2).map(r =>
    `<div style="font-size:11px;color:var(--text-muted);line-height:1.5;
                 display:flex;align-items:flex-start;gap:4px">
       <span style="opacity:.5;flex-shrink:0;margin-top:1px">›</span>
       <span>${esc(r)}</span>
     </div>`
  ).join('');

  // 5-dimension score breakdown bars
  const sb   = d.score_breakdown || {};
  const dims = [
    { label: 'Interests',   key: 'interests',   max: 40, color: '#6366f1' },
    { label: 'Budget',      key: 'budget',      max: 20, color: '#10b981' },
    { label: 'Travel type', key: 'travel_type', max: 20, color: '#06b6d4' },
    { label: 'Season',      key: 'season',      max: 10, color: '#f59e0b' },
    { label: 'Group size',  key: 'group_size',  max: 10, color: '#8b5cf6' },
  ];

  const breakdownHtml = Object.keys(sb).length ? `
    <div style="margin:10px 0 8px">
      <div style="font-size:9px;font-weight:700;text-transform:uppercase;
                  letter-spacing:.1em;color:var(--text-muted);margin-bottom:5px">
        Score breakdown
      </div>
      ${dims.map(dim => {
        const val = sb[dim.key] || 0;
        const pct = Math.round(val / dim.max * 100);
        return `
          <div style="display:flex;align-items:center;gap:5px;margin-bottom:3px">
            <span style="font-size:9px;color:var(--text-muted);min-width:62px;
                         text-transform:uppercase;letter-spacing:.04em;line-height:1">
              ${dim.label}
            </span>
            <div style="flex:1;height:4px;background:rgba(255,255,255,.06);
                        border-radius:2px;overflow:hidden">
              <div style="width:${pct}%;height:100%;background:${dim.color};
                           border-radius:2px;transition:width 700ms ease"></div>
            </div>
            <span style="font-size:9px;color:var(--text-muted);
                         min-width:26px;text-align:right;font-variant-numeric:tabular-nums">
              ${val}/${dim.max}
            </span>
          </div>`;
      }).join('')}
    </div>` : '';

  return `
    <div class="dest-card"
         onclick="window.location.href='/planner.html?dest=${encodeURIComponent(d.name)}'">

      <div class="dest-card-img">
        <img src="${getDestImg(d)}" alt="${d.name}" loading="lazy" onerror="this.style.display='none'"/>
        <div class="dest-card-img-overlay"></div>
        <div class="dest-card-match"
             style="background:${matchColor}cc;font-size:12px;font-weight:800;
                    letter-spacing:-.01em">
          ${match}% match
        </div>
      </div>

      <div class="dest-card-body">
        <!-- Header row: country + safety -->
        <div style="display:flex;align-items:center;justify-content:space-between;
                    margin-bottom:2px">
          <div class="dest-card-country">${d.country || ''}</div>
          <span style="font-size:10px;color:var(--text-muted)">
            ${safetyIcon} ${d.safety || ''}
          </span>
        </div>

        <div class="dest-card-name">${d.name}</div>
        <div class="dest-card-desc">${d.description || ''}</div>

        <!-- Why reasons -->
        <div style="display:flex;flex-direction:column;gap:3px;margin-bottom:8px">
          ${whyHtml}
        </div>

        <!-- 5-dimension breakdown -->
        ${breakdownHtml}

        <!-- Footer: tags + cost -->
        <div class="dest-card-footer" style="margin-top:6px">
          <div class="dest-card-tags">${tags}</div>
          <div class="dest-card-cost">~$${d.estimated_daily_cost || 0}/day</div>
        </div>
      </div>
    </div>`;
}
