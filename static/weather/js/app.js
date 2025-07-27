const form = document.getElementById("search-form");
const input = document.getElementById("city-input");
const results = document.getElementById("results");

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
  } catch (error) {
    results.innerHTML = `<p class="error">${error.message}</p>`;
  }
});

function renderWeather(data) {
  const { city, current, daily } = data;

  console.log("Days of forecast:", daily.time.length);

  let html = `
    <h2>Weather in ${city}</h2>
    <p>Temperature: ${current.temperature}°C</p>
    <p>Wind Speed: ${current.windspeed} m/s</p>
    <h3>${daily.time.length}-Day Forecast</h3>
    <ul>
  `;
  for (let i = 0; i < daily.time.length; i++) {
    html += `<li>
      ${daily.time[i]}: High ${daily.temperature_2m_max[i]}°C, Low ${daily.temperature_2m_min[i]}°C
    </li>`;
  }
  html += "</ul>";
  results.innerHTML = html;
}
