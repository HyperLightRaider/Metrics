// ===== Общий helper для запросов =====
async function apiFetch(path, options = {}) {
  const res = await fetch('/api' + path, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options
  });
  let data = null;
  try { data = await res.json(); } catch {}
  return { res, data };
}

// ===== index.html =====
async function checkAuthAndRedirect() {
  const { res } = await apiFetch('/user', { method: 'GET' });
  if (res.ok) {
    location.href = 'dashboard.html';
  } else {
    location.href = 'login.html';
  }
}

// ===== login.html =====
function initLoginPage() {
  const form = document.getElementById('loginForm');
  const errorEl = document.getElementById('login-error');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorEl.textContent = '';

    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;

    const { res, data } = await apiFetch('/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });

    if (res.ok) {
      location.href = 'dashboard.html';
    } else {
      errorEl.textContent = data?.error || 'Ошибка входа';
    }
  });
}

// ===== register.html =====
function initRegisterPage() {
  const form = document.getElementById('registerForm');
  const msgEl = document.getElementById('reg-message');
  const errEl = document.getElementById('reg-error');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    msgEl.textContent = '';
    errEl.textContent = '';

    const username = document.getElementById('reg-username').value.trim();
    const password = document.getElementById('reg-password').value;

    const { res, data } = await apiFetch('/register', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });

    if (res.status === 201) {
      msgEl.textContent = 'Регистрация успешна, теперь войдите';
    } else {
      errEl.textContent = data?.error || 'Ошибка регистрации';
    }
  });
}

// ===== dashboard.html =====
let metricsChart = null;

function initDashboardPage() {
  checkUserOrRedirect();
  initDefaultDate();
  initLogout();
  initEntryForm();
  loadEntriesAndRender();
  loadCorrelation();
}

async function checkUserOrRedirect() {
  const { res, data } = await apiFetch('/user', { method: 'GET' });
  if (!res.ok) {
    location.href = 'login.html';
    return;
  }
  const greeting = document.getElementById('greeting');
  greeting.textContent = 'Здравствуйте, ' + data.username;
}

function initDefaultDate() {
  const input = document.getElementById('entry-date');
  input.value = new Date().toISOString().slice(0, 10);
}

function initLogout() {
  const btn = document.getElementById('logoutBtn');
  btn.addEventListener('click', async () => {
    await apiFetch('/logout', { method: 'POST' });
    location.href = 'login.html';
  });
}

function initEntryForm() {
  const form = document.getElementById('entryForm');
  const okEl = document.getElementById('entry-success');
  const errEl = document.getElementById('entry-error');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    okEl.textContent = '';
    errEl.textContent = '';

    const payload = {
      date: document.getElementById('entry-date').value,
      sleep: parseFloat(document.getElementById('entry-sleep').value),
      energy: parseInt(document.getElementById('entry-energy').value),
      mood: parseInt(document.getElementById('entry-mood').value),
      productivity: parseInt(document.getElementById('entry-productivity').value),
      activity: parseInt(document.getElementById('entry-activity').value)
    };

    const { res, data } = await apiFetch('/entries', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    if (res.status === 201) {
      okEl.textContent = 'Запись добавлена';
      await loadEntriesAndRender();
      await loadCorrelation();
    } else {
      errEl.textContent = data?.error || 'Ошибка сохранения';
    }
  });
}

async function loadEntriesAndRender() {
  const { res, data } = await apiFetch('/entries?period=week', { method: 'GET' });
  if (!res.ok) return;
  renderMetricsChart(data.entries || []);
}

function renderMetricsChart(entries) {
  const ctx = document.getElementById('metricsChart').getContext('2d');

  const labels = entries.map(e => e.date);
  const sleep = entries.map(e => e.sleep);
  const energy = entries.map(e => e.energy);
  const mood = entries.map(e => e.mood);
  const productivity = entries.map(e => e.productivity);
  const activity = entries.map(e => e.activity);

  if (metricsChart) metricsChart.destroy();

  metricsChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Сон', data: sleep, borderColor: 'blue', tension: 0.2 },
        { label: 'Энергия', data: energy, borderColor: 'red', tension: 0.2 },
        { label: 'Настроение', data: mood, borderColor: 'green', tension: 0.2 },
        { label: 'Продуктивность', data: productivity, borderColor: 'purple', tension: 0.2 },
        { label: 'Активность', data: activity, borderColor: 'orange', tension: 0.2 }
      ]
    },
    options: {
      responsive: true,
      scales: {
        x: { title: { display: true, text: 'Дата' } },
        y: { title: { display: true, text: 'Значение' } }
      }
    }
  });
}

async function loadCorrelation() {
  const { res, data } = await apiFetch('/correlation', { method: 'GET' });
  const el = document.getElementById('correlationText');

  if (!res.ok) {
    el.textContent = 'Ошибка загрузки аналитики';
    return;
  }

  if (!data.top_correlation) {
    el.textContent = data.message || 'Недостаточно данных для анализа';
    return;
  }

  const { pair, value, strength } = data.top_correlation;
  el.textContent = `${pair[0]} → ${pair[1]}: ${strength} (коэффициент ${value.toFixed(2)})`;
}
