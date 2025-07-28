const form = document.getElementById("search-form");
const input = document.getElementById("city-input");
const results = document.getElementById("results");
const unitToggle = document.getElementById("unit-toggle");
const nightToggle = document.getElementById("night-toggle");
const locBtn = document.getElementById("loc-btn");
const recentList = document.getElementById("recent-list");

let isCelsius = true;

// Initialize
window.addEventListener("DOMContentLoaded", () => {
  fetchRecentSearches();
  if (localStorage.getItem("weatherly-theme") === "dark") {
    enableDarkMode();
    nightToggle.checked = true;
  }
});

// Search by city
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  await fetchAndRender(`/api/weather/?city=${encodeURIComponent(input.value)}`);
});

// Search by geolocation
locBtn.addEventListener("click", () => {
  if (!navigator.geolocation) return showError("Geolocation not supported.");
  navigator.geolocation.getCurrentPosition(
    (pos) => fetchAndRender(`/api/weather-coords/?lat=${pos.coords.latitude}&lon=${pos.coords.longitude}`),
    () => showError("Unable to retrieve your location.")
  );
});

// Unit toggle
unitToggle.addEventListener("change", () => {
  isCelsius = !unitToggle.checked;
  const last = results.dataset.lastData;
  if (last) renderWeather(JSON.parse(last));
});

// Night mode toggle
nightToggle.addEventListener("change", () => {
  nightToggle.checked ? enableDarkMode() : disableDarkMode();
  localStorage.setItem("weatherly-theme", nightToggle.checked ? "dark" : "light");
});

function enableDarkMode() {
  document.body.classList.add("dark-mode");
}
function disableDarkMode() {
  document.body.classList.remove("dark-mode");
}

// Fetch + render helper
async function fetchAndRender(url) {
  results.innerHTML = `<div class="text-center py-3">Loading…</div>`;
  try {
    const resp = await fetch(url);
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "Unknown error");
    renderWeather(data);
    await fetchRecentSearches();
  } catch (err) {
    showError(err.message);
  }
}

// Render weather
function renderWeather(data) {
  results.dataset.lastData = JSON.stringify(data);

  const temp = isCelsius
    ? `${data.current.temperature}°C`
    : `${(data.current.temperature * 9/5 + 32).toFixed(1)}°F`;
  const speed = `${data.current.windspeed} m/s`;

  let html = `
    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title">${data.city}</h2>
        <p class="card-text">Temperature: ${temp}</p>
        <p class="card-text">Wind Speed: ${speed}</p>
        <h5>${data.daily.time.length}-Day Forecast</h5>
        <ul class="list-group list-group-flush">
  `;
  data.daily.time.forEach((day, i) => {
    const max = isCelsius
      ? `${data.daily.temperature_2m_max[i]}°C`
      : `${(data.daily.temperature_2m_max[i] * 9/5 + 32).toFixed(1)}°F`;
    const min = isCelsius
      ? `${data.daily.temperature_2m_min[i]}°C`
      : `${(data.daily.temperature_2m_min[i] * 9/5 + 32).toFixed(1)}°F`;
    html += `
      <li class="list-group-item">
        ${day}: High ${max}, Low ${min}
      </li>`;
  });
  html += `</ul></div></div>`;
  results.innerHTML = html;
}

// Show error
function showError(msg) {
  results.innerHTML = `<div class="alert alert-danger">${msg}</div>`;
}

// Recent searches
async function fetchRecentSearches() {
  try {
    const resp = await fetch("/api/searches/");
    const list = await resp.json();
    renderRecent(list.map(i => ({
      city: i.city,
      time: new Date(i.searched_at).toLocaleString(),
    })));
  } catch {}
}
function renderRecent(items) {
  recentList.innerHTML = "";
  if (!items.length) {
    recentList.innerHTML = `<li class="list-group-item">No recent searches</li>`;
    return;
  }
  items.forEach(({ city, time }) => {
    const li = document.createElement("li");
    li.className = "list-group-item";
    li.textContent = `${city} at ${time}`;
    recentList.appendChild(li);
  });
}
