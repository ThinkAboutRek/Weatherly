// existing selectors
const form = document.getElementById("search-form");
const input = document.getElementById("city-input");
const results = document.getElementById("results");
const toggle = document.getElementById("unit-toggle");
const recentList = document.getElementById("recent-list");

// new night mode toggle
const nightToggle = document.getElementById("night-toggle");
const htmlEl = document.documentElement;

let isCelsius = true;

// On load
window.addEventListener("DOMContentLoaded", () => {
  fetchRecentSearches();
  // initialize night mode from localStorage
  if (localStorage.getItem("weatherly-theme") === "dark") {
    nightToggle.checked = true;
    htmlEl.setAttribute("data-theme", "dark");
  }
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const city = input.value.trim();
  if (!city) return;

  results.innerHTML = `<div class="text-center py-3">Loading…</div>`;
  try {
    const resp = await fetch(`/api/weather/?city=${encodeURIComponent(city)}`);
    if (!resp.ok) throw new Error((await resp.json()).error || "Unknown error");
    const data = await resp.json();
    renderWeather(data);
    await fetchRecentSearches();
  } catch (error) {
    results.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
  }
});

toggle.addEventListener("change", () => {
  isCelsius = !toggle.checked;
  const lastData = results.dataset.lastData;
  if (lastData) renderWeather(JSON.parse(lastData));
});

nightToggle.addEventListener("change", () => {
  const theme = nightToggle.checked ? "dark" : "light";
  htmlEl.setAttribute("data-theme", theme);
  localStorage.setItem("weatherly-theme", theme);
});

// Render functions unchanged except minor Bootstrap tweaks
function renderWeather(data) {
  const { city, current, daily } = data;
  results.dataset.lastData = JSON.stringify(data);

  const temp = isCelsius
    ? `${current.temperature}°C`
    : `${(current.temperature * 9/5 + 32).toFixed(1)}°F`;

  const speed = `${current.windspeed} m/s`;

  let html = `
    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title">${city}</h2>
        <p class="card-text">Temperature: ${temp}</p>
        <p class="card-text">Wind Speed: ${speed}</p>
        <h5>${daily.time.length}-Day Forecast</h5>
        <ul class="list-group list-group-flush">
  `;
  for (let i = 0; i < daily.time.length; i++) {
    const max = isCelsius
      ? `${daily.temperature_2m_max[i]}°C`
      : `${(daily.temperature_2m_max[i] * 9/5 + 32).toFixed(1)}°F`;
    const min = isCelsius
      ? `${daily.temperature_2m_min[i]}°C`
      : `${(daily.temperature_2m_min[i] * 9/5 + 32).toFixed(1)}°F`;
    html += `
      <li class="list-group-item">
        ${daily.time[i]}: High ${max}, Low ${min}
      </li>`;
  }
  html += `
        </ul>
      </div>
    </div>
  `;
  results.innerHTML = html;
}

async function fetchRecentSearches() {
  try {
    const resp = await fetch("/api/searches/");
    const list = await resp.json();
    renderRecent(list.map(item => ({
      city: item.city,
      time: new Date(item.searched_at).toLocaleString(),
    })));
  } catch {
    // silent
  }
}

function renderRecent(items) {
  recentList.innerHTML = "";
  if (!items.length) {
    recentList.innerHTML = `<li class="list-group-item">No recent searches</li>`;
    return;
  }
  items.forEach(({city, time}) => {
    const li = document.createElement("li");
    li.className = "list-group-item";
    li.textContent = `${city} at ${time}`;
    recentList.appendChild(li);
  });
}
