/* ═══════════════════════════════════════════════════════════
   TripPilot AI — Shared JS (auth, nav, utils, toasts)
   ═══════════════════════════════════════════════════════════ */

'use strict';

// ── State ─────────────────────────────────────────────────────
const App = {
  user: null,
};

// ── DOM Ready ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initNavScroll();
  initHamburger();
  initModalBackdrops();
  checkAuth();
  if (document.getElementById('destGrid')) loadHomeDests();
  if (document.getElementById('heroSearch')) initHeroSearch();
  createToastContainer();
  _handleAuthRedirect();
});

// ── Navbar scroll effect ───────────────────────────────────────
function initNavScroll() {
  const nav = document.getElementById('navbar');
  if (!nav) return;
  const onScroll = () => {
    nav.classList.toggle('scrolled', window.scrollY > 40);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

// ── Hamburger menu ─────────────────────────────────────────────
function initHamburger() {
  const btn = document.getElementById('hamburger');
  const links = document.querySelector('.nav-links');
  const auth = document.querySelector('.nav-auth');
  if (!btn) return;
  btn.addEventListener('click', () => {
    const open = btn.classList.toggle('open');
    if (links) links.style.display = open ? 'flex' : '';
    if (auth) auth.style.display = open ? 'flex' : '';
    if (open && links) {
      links.style.flexDirection = 'column';
      links.style.position = 'absolute';
      links.style.top = '68px';
      links.style.left = '0';
      links.style.right = '0';
      links.style.background = 'rgba(10,10,15,0.97)';
      links.style.padding = '16px 24px';
      links.style.borderBottom = '1px solid rgba(255,255,255,0.08)';
      links.style.zIndex = '999';
    } else if (links) {
      links.removeAttribute('style');
    }
  });
}

// ── Modal backdrop close ───────────────────────────────────────
function initModalBackdrops() {
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', e => {
      if (e.target === overlay) closeModal(overlay.id);
    });
  });
}

// ── Modal helpers ──────────────────────────────────────────────
function openModal(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.add('active'); el.style.display = 'flex'; }
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.remove('active'); el.style.display = ''; }
}
function switchModal(fromId, toId) {
  closeModal(fromId);
  setTimeout(() => openModal(toId), 150);
}

// ── Auth ───────────────────────────────────────────────────────
async function checkAuth() {
  try {
    const res = await fetch('/api/auth/me');
    if (res.ok) {
      const data = await res.json();
      App.user = data.user;
      renderNavUser(data.user);
    }
  } catch (_) { /* not logged in */ }
}

function renderNavUser(user) {
  const navAuth = document.getElementById('navAuth');
  if (!navAuth) return;
  navAuth.innerHTML = `
    <a href="/dashboard.html" class="nav-user-btn" title="Go to dashboard">
      <div class="nav-avatar">${(user.name || 'U')[0].toUpperCase()}</div>
      <span>${user.name.split(' ')[0]}</span>
    </a>`;
}

async function handleLogin(e) {
  e.preventDefault();
  const emailEl = document.getElementById('loginEmail');
  const passEl  = document.getElementById('loginPassword');
  const errEl   = document.getElementById('loginError');
  if (!emailEl || !passEl) return;
  errEl.textContent = '';

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: emailEl.value.trim(), password: passEl.value }),
    });
    const data = await res.json();
    if (data.status === 'success') {
      App.user = data.user;
      renderNavUser(data.user);
      closeModal('loginModal');
      showToast('Welcome back, ' + data.user.name.split(' ')[0] + '!', 'success');
      if (window.location.pathname === '/dashboard.html') location.reload();
    } else {
      errEl.textContent = data.message || 'Login failed.';
    }
  } catch (_) {
    errEl.textContent = 'Server error. Please try again.';
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const nameEl = document.getElementById('regName');
  const emailEl = document.getElementById('regEmail');
  const passEl  = document.getElementById('regPassword');
  const errEl   = document.getElementById('registerError');
  if (!nameEl || !emailEl || !passEl) return;
  errEl.textContent = '';

  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: nameEl.value.trim(), email: emailEl.value.trim(), password: passEl.value }),
    });
    const data = await res.json();
    if (data.status === 'success') {
      App.user = data.user;
      renderNavUser(data.user);
      closeModal('registerModal');
      showToast('Welcome to TripPilot AI, ' + data.user.name.split(' ')[0] + '! 🎉', 'success');
      if (window.location.pathname === '/dashboard.html') location.reload();
    } else {
      errEl.textContent = data.message || 'Registration failed.';
    }
  } catch (_) {
    errEl.textContent = 'Server error. Please try again.';
  }
}

async function handleLogout() {
  await fetch('/api/auth/logout', { method: 'POST' });
  App.user = null;
  showToast('Logged out successfully.', 'info');
  setTimeout(() => window.location.href = '/', 800);
}

// ── Hero search ────────────────────────────────────────────────
const DEST_LIST = [
  'Paris','Tokyo','Dubai','Bali','New York','Istanbul','Rome','Maldives',
  'Hunza','Skardu','Fairy Meadows','Naran','Swat','Murree','Neelum Valley',
  'Lahore','Taxila','Multan','Peshawar','Bahawalpur',
  'Makkah','Madinah','Jerusalem',
  'Karachi','Gwadar','Antalya',
  'Abu Dhabi','Doha','Kuala Lumpur','Singapore','Bangkok','Seoul',
  'London','Barcelona','Amsterdam','Los Angeles','Toronto','Sydney',
  'Patagonia','Interlaken','Queenstown','Banff',
  'Monaco','Santorini','Swiss Alps','Bora Bora',
  'Kyoto','Prague','Cairo','Cape Town','Marrakech','Vienna','Lisbon',
  'Florence','Athens','Rio de Janeiro','Iceland','Phuket',
];
const DEST_EMOJIS = {
  paris:'🗼', tokyo:'⛩️', dubai:'🏙️', bali:'🌴', 'new york':'🗽',
  istanbul:'🕌', rome:'🏛️', maldives:'🏖️',
  hunza:'🏔️', skardu:'⛰️', 'fairy meadows':'🌿', naran:'🏕️',
  swat:'🌲', murree:'🌄', 'neelum valley':'🏞️',
  lahore:'🕌', taxila:'🏺', multan:'🕌', peshawar:'🏺', bahawalpur:'🏰',
  makkah:'🕋', madinah:'🕌', jerusalem:'✡️',
  karachi:'🌊', gwadar:'⚓', antalya:'☀️',
  'abu dhabi':'🕌', doha:'🌆', 'kuala lumpur':'🏙️', singapore:'🦁',
  bangkok:'🛕', seoul:'🏯', london:'🎡', barcelona:'🎨',
  amsterdam:'🚲', 'los angeles':'🎬', toronto:'🍁', sydney:'🦘',
  patagonia:'🏔️', interlaken:'🎿', queenstown:'🦅', banff:'🦌',
  monaco:'🎰', santorini:'🌅', 'swiss alps':'⛷️', 'bora bora':'🌺',
  kyoto:'⛩️', prague:'🏰', cairo:'🛕', 'cape town':'🦁',
  marrakech:'🪔', vienna:'🎼', lisbon:'🐟', florence:'🎨',
  athens:'🏛️', 'rio de janeiro':'🎭', iceland:'🌋', phuket:'🏝️',
};

function initHeroSearch() {
  const input = document.getElementById('heroSearch');
  const box   = document.getElementById('searchSuggestions');
  if (!input || !box) return;

  input.addEventListener('input', () => {
    const q = input.value.trim().toLowerCase();
    if (!q) { box.innerHTML = ''; return; }
    const matches = DEST_LIST.filter(d => d.toLowerCase().includes(q));
    if (!matches.length) { box.innerHTML = ''; return; }
    box.innerHTML = matches.map(d => `
      <div class="search-suggestion-item" onclick="selectHeroDest('${d}')">
        <span>${DEST_EMOJIS[d.toLowerCase()] || '📍'}</span>
        <span>${d}</span>
      </div>`).join('');
  });

  document.addEventListener('click', e => {
    if (!e.target.closest('.hero-search-wrap')) box.innerHTML = '';
  });
}

function selectHeroDest(dest) {
  const input = document.getElementById('heroSearch');
  if (input) input.value = dest;
  document.getElementById('searchSuggestions').innerHTML = '';
}

function heroSearch() {
  const q = (document.getElementById('heroSearch')?.value || '').trim();
  if (!q) { showToast('Enter a destination first', 'info'); return; }
  window.location.href = `/planner.html?dest=${encodeURIComponent(q)}`;
}

// ── Home destinations ──────────────────────────────────────────
async function loadHomeDests() {
  const grid = document.getElementById('destGrid');
  if (!grid) return;
  try {
    const res  = await fetch('/api/destinations');
    const data = await res.json();
    const dests = (data.destinations || []).slice(0, 6);
    grid.innerHTML = dests.map(renderDestCard).join('');
  } catch (_) {
    grid.innerHTML = '<p style="color:var(--text-muted)">Could not load destinations.</p>';
  }
}

// ── Unsplash destination image map (free, no API key needed) ──
const DEST_IMAGES = {
  'paris':         'https://images.unsplash.com/photo-1499856871958-5b9357976b82?w=400&q=80',
  'tokyo':         'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400&q=80',
  'dubai':         'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=400&q=80',
  'bali':          'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=400&q=80',
  'new york':      'https://images.unsplash.com/photo-1499092346589-b9b6be3e94b2?w=400&q=80',
  'istanbul':      'https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=400&q=80',
  'rome':          'https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=400&q=80',
  'maldives':      'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=400&q=80',
  'hunza':         'https://images.unsplash.com/photo-1626082927389-6cd097cee6a5?w=400&q=80',
  'skardu':        'https://images.unsplash.com/photo-1580502304784-8985b7eb7260?w=400&q=80',
  'fairy meadows': 'https://images.unsplash.com/photo-1585016495481-8c4e6e809f02?w=400&q=80',
  'naran':         'https://images.unsplash.com/photo-1625244724120-1fd1d34d00f6?w=400&q=80',
  'swat':          'https://images.unsplash.com/photo-1586348943529-beaae6c28db9?w=400&q=80',
  'murree':        'https://images.unsplash.com/photo-1583922606661-0822ed0bd916?w=400&q=80',
  'lahore':        'https://images.unsplash.com/photo-1582461833047-2aeb4f9a1203?w=400&q=80',
  'makkah':        'https://images.unsplash.com/photo-1591604466107-ec97de577aff?w=400&q=80',
  'madinah':       'https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?w=400&q=80',
  'karachi':       'https://images.unsplash.com/photo-1567157577867-05ccb1388e66?w=400&q=80',
  'antalya':       'https://images.unsplash.com/photo-1524820801657-fd59673fbb05?w=400&q=80',
  'doha':          'https://images.unsplash.com/photo-1588880331179-bc9b93a8cb5e?w=400&q=80',
  'kuala lumpur':  'https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=400&q=80',
  'singapore':     'https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=400&q=80',
  'bangkok':       'https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=400&q=80',
  'seoul':         'https://images.unsplash.com/photo-1538485399081-7191377e8241?w=400&q=80',
  'london':        'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=400&q=80',
  'barcelona':     'https://images.unsplash.com/photo-1583422409516-2895a77efded?w=400&q=80',
  'amsterdam':     'https://images.unsplash.com/photo-1534351590666-13e3e96b5017?w=400&q=80',
  'los angeles':   'https://images.unsplash.com/photo-1534190760961-74e8c1c5c3da?w=400&q=80',
  'toronto':       'https://images.unsplash.com/photo-1517090504586-fde19ea6066f?w=400&q=80',
  'sydney':        'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=400&q=80',
  'kyoto':         'https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=400&q=80',
  'prague':        'https://images.unsplash.com/photo-1541849546-216549ae216d?w=400&q=80',
  'cairo':         'https://images.unsplash.com/photo-1572252009286-268acec5ca0a?w=400&q=80',
  'cape town':     'https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=400&q=80',
  'marrakech':     'https://images.unsplash.com/photo-1534430480872-3498386e7856?w=400&q=80',
  'vienna':        'https://images.unsplash.com/photo-1516550893923-42d28e5677af?w=400&q=80',
  'santorini':     'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=400&q=80',
  'phuket':        'https://images.unsplash.com/photo-1589394815804-964ed0be2eb5?w=400&q=80',
  'iceland':       'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=400&q=80',
  'lisbon':        'https://images.unsplash.com/photo-1555881400-74d7acaacd8b?w=400&q=80',
  'florence':      'https://images.unsplash.com/photo-1541370976299-4d24be63b9cc?w=400&q=80',
  'athens':        'https://images.unsplash.com/photo-1555993539-1732b0258235?w=400&q=80',
  'banff':         'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=400&q=80',
  'patagonia':     'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=400&q=80',
  'queenstown':    'https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=400&q=80',
  'interlaken':    'https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=400&q=80',
  'monaco':        'https://images.unsplash.com/photo-1562883676-8c7feb83f09b?w=400&q=80',
  'gwadar':        'https://images.unsplash.com/photo-1596003906949-67221c17b9e4?w=400&q=80',
};

function getDestImage(name) {
  const key = (name || '').toLowerCase();
  return DEST_IMAGES[key] || `https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=400&q=80`;
}

function renderDestCard(d, showMatch = false) {
  const imgUrl = getDestImage(d.name);
  const tags  = (d.tags || []).slice(0, 3).map(t => `<span class="dest-tag">${t}</span>`).join('');
  const budgetLow = d.daily_budget?.low || d.estimated_daily_cost || 0;
  const matchBadge = showMatch && d.match_pct
    ? `<div class="dest-card-match">${d.match_pct}% match</div>` : '';

  return `
    <div class="dest-card" onclick="window.location.href='/planner.html?dest=${encodeURIComponent(d.name)}'">
      <div class="dest-card-img">
        <img src="${imgUrl}" alt="${d.name}" loading="lazy" onerror="this.parentElement.style.background='linear-gradient(135deg,#e040fb22,#00e5ff22)'; this.style.display='none'"/>
        <div class="dest-card-img-overlay"></div>
        ${matchBadge}
      </div>
      <div class="dest-card-body">
        <div class="dest-card-country">${d.country || ''}</div>
        <div class="dest-card-name">${d.name}</div>
        <div class="dest-card-desc">${d.description || ''}</div>
        <div class="dest-card-footer">
          <div class="dest-card-tags">${tags}</div>
          <div class="dest-card-cost">From <strong>$${budgetLow}</strong>/day</div>
        </div>
      </div>
    </div>`;
}

// ── Toast notifications ────────────────────────────────────────
function createToastContainer() {
  if (document.getElementById('toastContainer')) return;
  const el = document.createElement('div');
  el.id = 'toastContainer';
  document.body.appendChild(el);
}

function showToast(msg, type = 'info', duration = 3500) {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type] || ''}</span><span>${msg}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(24px)';
    toast.style.transition = 'all 300ms ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ── Utility: format currency ───────────────────────────────────
function fmt(n) {
  if (n === undefined || n === null) return '$0';
  return '$' + Number(n).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

// ── Escape HTML ────────────────────────────────────────────────
function esc(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

// ── Auth redirect handler ──────────────────────────────────────
// Called on every DOMContentLoaded.
// 1. If the server redirected with ?login=1, open the login modal
//    so the user can authenticate and be returned to their destination.
// 2. If the current page is dashboard and the user is not logged in
//    after checkAuth resolves, redirect them away.
function _handleAuthRedirect() {
  const params = new URLSearchParams(window.location.search);

  // Server set ?login=1 after blocking a protected page request
  if (params.get('login') === '1') {
    // Show the login modal automatically
    setTimeout(() => {
      openModal('loginModal');
      showToast('Please log in to access that page.', 'info', 4000);
    }, 300);

    // After successful login, redirect to the `next` param
    const next = params.get('next') || '/dashboard.html';
    // Monkey-patch handleLogin to redirect after success
    const _origLogin = window.handleLogin;
    window.handleLogin = async function (e) {
      await _origLogin(e);
      if (App.user) {
        // Clean the URL and navigate
        window.location.href = next;
      }
    };
  }

  // Client-side guard for dashboard: if user is not authenticated
  // after a short delay (enough for checkAuth to finish), redirect
  if (window.location.pathname === '/dashboard.html') {
    setTimeout(() => {
      if (!App.user) {
        showToast('Please log in to access your dashboard.', 'info', 3000);
        setTimeout(() => {
          window.location.href = '/?next=/dashboard.html&login=1';
        }, 1200);
      }
    }, 1800);  // allow checkAuth time to complete
  }
}
