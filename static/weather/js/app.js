const form = document.getElementById("search-form");
const input = document.getElementById("city-input");
const results = document.getElementById("results");
const toggle = document.getElementById("unit-toggle");
const recentList = document.getElementById("recent-list");

let isCelsius = true;

// Fetch and render recent searches on load
window.addEventListener("DOMContentLoaded", fetchRecentSearches);

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const city = input.value.trim();
  if (!city) return;

  results.innerHTML = "<p>Loading…</p>";
  try {
    const resp = await fetch(`/api/weather/?city=${encodeURIComponent(city)}`);
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.error || "Unknown error");
    }
    const data = await resp.json();
    renderWeather(data);
    await fetchRecentSearches(); // update list after logging in DB
  } catch (error) {
    results.innerHTML = `<p class="error">${error.message}</p>`;
  }
});

toggle.addEventListener("change", () => {
  isCelsius = !toggle.checked;
  // If there’s already rendered data, re-render it
  const lastData = results.dataset.lastData;
  if (lastData) renderWeather(JSON.parse(lastData));
});

function renderWeather(data) {
  const { city, current, daily } = data;
  // Save for re-render on toggle
  results.dataset.lastData = JSON.stringify(data);

  // Temperature respects the toggle…
  const temp = isCelsius
    ? `${current.temperature}°C`
    : `${(current.temperature * 9/5 + 32).toFixed(1)}°F`;

  // …but wind speed is always m/s
  const speed = `${current.windspeed} m/s`;

  let html = `
    <h2>Weather in ${city}</h2>
    <p>Temperature: ${temp}</p>
    <p>Wind Speed: ${speed}</p>
    <h3>${daily.time.length}-Day Forecast</h3>
    <ul>
  `;
  for (let i = 0; i < daily.time.length; i++) {
    const max = isCelsius
      ? `${daily.temperature_2m_max[i]}°C`
      : `${(daily.temperature_2m_max[i] * 9/5 + 32).toFixed(1)}°F`;
    const min = isCelsius
      ? `${daily.temperature_2m_min[i]}°C`
      : `${(daily.temperature_2m_min[i] * 9/5 + 32).toFixed(1)}°F`;
    html += `<li>
      ${daily.time[i]}: High ${max}, Low ${min}
    </li>`;
  }
  html += "</ul>";
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
    // silently fail
  }
}

function renderRecent(items) {
  recentList.innerHTML = "";
  if (!items.length) {
    recentList.innerHTML = "<li>No recent searches</li>";
    return;
  }
  items.forEach(({city, time}) => {
    const li = document.createElement("li");
    li.textContent = `${city} at ${time}`;
    recentList.appendChild(li);
  });
}
