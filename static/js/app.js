/* AquaReserve common UI logic */

function toast(msg, type = '') {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = msg;
  el.className = 'toast' + (type ? ' ' + type : '');
  el.hidden = false;
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => { el.hidden = true; }, 3000);
}

function formatMoney(n) {
  const num = typeof n === 'number' ? n : parseFloat(n || 0);
  return '$' + num.toFixed(2);
}

function formatStatus(s) {
  return `<span class="pill pill-${s}">${s}</span>`;
}

function placeholderImage(type) {
  // Inline SVG placeholders by type
  const colors = {
    boat: '#1d8ecf',
    jet_ski: '#ff6f61',
    yacht: '#062a4a',
    speed_boat: '#2ec4b6',
  };
  const c = colors[type] || '#1d8ecf';
  const emoji = { boat: '⛵', jet_ski: '🛥️', yacht: '🛳️', speed_boat: '🚤' }[type] || '⛵';
  return `data:image/svg+xml;utf8,${encodeURIComponent(
    `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'>
      <defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>
        <stop offset='0' stop-color='${c}'/><stop offset='1' stop-color='#7fdcff'/></linearGradient></defs>
      <rect width='400' height='300' fill='url(#g)'/>
      <text x='50%' y='55%' text-anchor='middle' font-size='110' fill='white' opacity='0.85'>${emoji}</text>
    </svg>`)}`;
}

function craftImage(craft) {
  return craft.display_image || craft.image_url || placeholderImage(craft.type);
}

// Navbar auth state
function refreshNavbar() {
  const user = AquaAPI.getUser();
  const isAuth = !!user;
  const isAdmin = !!(user && (user.role === 'admin' || user.is_staff));
  document.querySelectorAll('.auth-only').forEach(el => el.hidden = !isAuth);
  document.querySelectorAll('.guest-only').forEach(el => el.hidden = isAuth);
  document.querySelectorAll('.admin-only').forEach(el => el.hidden = !isAdmin);
  if (isAuth) {
    document.querySelectorAll('.user-name').forEach(el => el.textContent = user.username);
  }
}

// Logout
document.addEventListener('click', async (e) => {
  if (e.target && e.target.id === 'logoutBtn') {
    await AquaAPI.logout();
    AquaAPI.clearTokens();
    toast('Logged out', 'success');
    setTimeout(() => { window.location.href = '/'; }, 400);
  }
});

document.addEventListener('DOMContentLoaded', refreshNavbar);

function requireAuth(redirect = '/login/') {
  if (!AquaAPI.getUser()) {
    toast('Please sign in first', 'error');
    setTimeout(() => { window.location.href = redirect; }, 500);
    return false;
  }
  return true;
}

function requireAdmin() {
  const u = AquaAPI.getUser();
  if (!u || (u.role !== 'admin' && !u.is_staff)) {
    toast('Admin access required', 'error');
    setTimeout(() => { window.location.href = '/'; }, 500);
    return false;
  }
  return true;
}
