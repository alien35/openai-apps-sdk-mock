console.log("🟢 Insurance widget JS loaded");

function render(data) {
  console.log("📦 Rendering insurance data:", data);

  let container = document.getElementById('insurance-root');
  if (!container) {
    console.warn("⚠️ #insurance-root not found, creating fallback container");
    container = document.createElement('div');
    container.id = 'insurance-root';
    document.body.appendChild(container);
  }

  // Build subtitle
  const parts = [];

  if (data.city) {
    parts.push(data.city);
  } else if (data.zip_code) {
    parts.push(`ZIP ${data.zip_code}`);
  }

  const numVehicles = data.num_vehicles || 1;
  const numDrivers = data.num_drivers || 1;
  parts.push(numVehicles === 1 ? '1 vehicle' : `${numVehicles} vehicles`);
  parts.push(numDrivers === 1 ? '1 driver' : `${numDrivers} drivers`);

  const subtitle = parts.join(' • ');

  // Build carrier list
  const carriers = data.carriers || [];
  const carrierHtml = carriers.map(c => `
    <div class="carrier">
      <div class="carrier-name">${c.name}</div>
      <div class="price">
        <div class="monthly">$${c.monthly_cost}/mo</div>
        <div class="annual">$${c.annual_cost}/year</div>
      </div>
    </div>
  `).join('');

  container.innerHTML = `
    <div class="container">
      <div class="title">Your Insurance Quote</div>
      <div class="subtitle">${subtitle}</div>
      ${carrierHtml}
    </div>
  `;

  console.log("✅ Rendered");
}

// Check for existing data
if (window.openai && window.openai.toolOutput) {
  console.log("✅ Found window.openai.toolOutput");
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => render(window.openai.toolOutput), { once: true });
  } else {
    render(window.openai.toolOutput);
  }
}

// Listen for hydration
window.addEventListener('openai:set_globals', (event) => {
  console.log("🎯 Received openai:set_globals");
  if (event.detail && event.detail.globals && event.detail.globals.toolOutput) {
    render(event.detail.globals.toolOutput);
  }
});
