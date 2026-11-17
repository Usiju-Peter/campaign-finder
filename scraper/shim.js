// Minimal stand-in for the dashboard runtime: loads the data file and reruns every drawing.
window.dash = (() => {
  const data = { campaigns: { status: 'loading', data: [], message: '', refreshing: false, truncated: false, meta: [] } };
  const draws = new Map();
  const run = (name) => document.querySelectorAll(`[data-draw="${name}"]`).forEach((el) => { try { draws.get(name)(el); } catch (e) { console.error(name, e); } });
  let started = false;
  const all = () => draws.forEach((_, n) => run(n));
  window.addEventListener('DOMContentLoaded', () => {
    started = true; all();
    fetch(window.__DATA_URL || 'data/campaigns.json', { cache: 'no-store' }).then((r) => r.json()).then((j) => {
      window.__META = j.meta; data.campaigns = { status: 'ok', data: j.rows, message: '', refreshing: false, truncated: false, meta: [] }; all();
    }).catch((e) => { data.campaigns = { status: 'error', data: [], message: String(e) }; all(); });
  });
  let w = 0; window.addEventListener('resize', () => { if (Math.abs(innerWidth - w) > 20) { w = innerWidth; all(); } });
  return {
    colors: window.__COLORS || ['#3d6fd9', '#d9733d', '#3da67a', '#a65dd1'],
    data: (id) => data[id] || { status: 'missing', data: [] },
    onData: (fn) => fn(),
    draw: (name, fn) => { if (fn) { draws.set(name, fn); if (started) run(name); } else if (draws.has(name)) run(name); },
    params: () => ({}), setParams: () => {}, resetParams: () => {}, setLink: () => {}, refresh: () => {},
  };
})();
