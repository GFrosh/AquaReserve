/* AquaReserve API client */
const AquaAPI = (() => {
  const BASE = '/api';

  function getTokens() {
    try { return JSON.parse(localStorage.getItem('aqua_tokens') || 'null'); }
    catch { return null; }
  }
  function setTokens(t) { localStorage.setItem('aqua_tokens', JSON.stringify(t)); }
  function clearTokens() { localStorage.removeItem('aqua_tokens'); localStorage.removeItem('aqua_user'); }

  function getUser() {
    try { return JSON.parse(localStorage.getItem('aqua_user') || 'null'); }
    catch { return null; }
  }
  function setUser(u) { localStorage.setItem('aqua_user', JSON.stringify(u)); }

  async function request(path, { method = 'GET', body, auth = false, isFormData = false } = {}) {
    const headers = {};
    if (!isFormData) headers['Content-Type'] = 'application/json';
    if (auth) {
      const t = getTokens();
      if (t?.access) headers['Authorization'] = `Bearer ${t.access}`;
    }
    const opts = { method, headers };
    if (body) opts.body = isFormData ? body : JSON.stringify(body);
    const res = await fetch(`${BASE}${path}`, opts);
    let data = null;
    const txt = await res.text();
    try { data = txt ? JSON.parse(txt) : null; } catch { data = txt; }
    if (!res.ok) {
      const err = new Error(typeof data === 'string' ? data : (data?.detail || 'Request failed'));
      err.status = res.status;
      err.data = data;
      throw err;
    }
    return data;
  }

  return {
    // auth
    register: (payload) => request('/auth/register', { method: 'POST', body: payload }),
    login:    (payload) => request('/auth/login', { method: 'POST', body: payload }),
    logout:   () => {
      const t = getTokens();
      return request('/auth/logout', { method: 'POST', auth: true, body: { refresh: t?.refresh } }).catch(()=>{});
    },
    me:       () => request('/auth/me', { auth: true }),

    // watercraft
    listWatercraft: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return request(`/watercraft/${qs ? '?' + qs : ''}`);
    },
    getWatercraft:  (id) => request(`/watercraft/${id}/`),
    createWatercraft: (payload) => request('/watercraft/', { method: 'POST', auth: true, body: payload }),
    updateWatercraft: (id, payload) => request(`/watercraft/${id}/`, { method: 'PUT', auth: true, body: payload }),
    deleteWatercraft: (id) => request(`/watercraft/${id}/`, { method: 'DELETE', auth: true }),
    watercraftAvailability: (id, date) => request(`/watercraft/${id}/availability?date=${date}`),

    // reservations
    listReservations: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return request(`/reservations/${qs ? '?' + qs : ''}`, { auth: true });
    },
    createReservation: (payload) => request('/reservations/', { method: 'POST', auth: true, body: payload }),
    cancelReservation: (id) => request(`/reservations/${id}/cancel/`, { method: 'POST', auth: true }),

    // admin
    adminReservations: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return request(`/admin/reservations${qs ? '?' + qs : ''}`, { auth: true });
    },
    adminUpdateStatus: (id, status) =>
      request(`/admin/reservations/${id}/status`, { method: 'PATCH', auth: true, body: { status } }),
    adminStats: () => request('/admin/stats', { auth: true }),

    // helpers
    getTokens, setTokens, clearTokens, getUser, setUser,
  };
})();
