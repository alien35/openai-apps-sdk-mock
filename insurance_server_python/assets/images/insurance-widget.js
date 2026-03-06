console.log("🟢 Insurance widget JS loaded");

// Get the BASE_URL from the script tag's src attribute
const scriptTag = document.currentScript || document.querySelector('script[src*="insurance-widget.js"]');
const scriptSrc = scriptTag ? scriptTag.src : '';
const BASE_URL = scriptSrc ? scriptSrc.substring(0, scriptSrc.lastIndexOf('/assets')) : '';

console.log("📦 Base URL:", BASE_URL);

function formatCurrency(value) {
  if (!value) return "--";
  return `$${value.toLocaleString()}`;
}

function render(data) {
  console.log("📦 Rendering insurance widget with data:", data);

  const container = document.getElementById('insurance-root');
  if (!container) {
    console.error("❌ Container #insurance-root not found");
    return;
  }

  // Extract data
  const zipCode = data.zip_code || "90210";
  const city = data.city || null;
  const state = data.state || null;
  const numDrivers = data.num_drivers || 1;
  const numVehicles = data.num_vehicles || 1;
  const carriers = data.carriers || [
    { name: "Geico", monthly_cost: 258, annual_cost: 3100 },
    { name: "Progressive", monthly_cost: 300, annual_cost: 3600 },
    { name: "State Farm", monthly_cost: 317, annual_cost: 3800 },
  ];

  // Build disclaimer text
  const driverText = numDrivers === 1 ? "a solo driver" : `${numDrivers} drivers`;
  const vehicleText = numVehicles === 1 ? "one vehicle" : `${numVehicles} vehicles`;
  const locationText = city ? `the ${city} area` : `zip code ${zipCode}`;

  // Build vehicle description if available
  let vehicleDescription = '';
  if (data.vehicle && (data.vehicle.year || data.vehicle.make || data.vehicle.model)) {
    const parts = [];
    if (data.vehicle.year) parts.push(data.vehicle.year);
    if (data.vehicle.make) parts.push(data.vehicle.make);
    if (data.vehicle.model) parts.push(data.vehicle.model);
    vehicleDescription = parts.join(' ');
  }

  // Build driver description if available
  let driverDescription = '';
  if (data.driver_age) {
    const parts = [`age ${data.driver_age}`];
    if (data.marital_status) parts.push(data.marital_status);
    driverDescription = parts.join(', ');
  }

  // Build coverage description
  const coverageText = data.coverage_type ? `, with ${data.coverage_type}` : '';

  // Construct detailed disclaimer
  let disclaimerParts = [`The estimates shown below are for ${locationText}`];
  if (vehicleDescription) {
    disclaimerParts.push(`for a ${vehicleDescription}`);
  } else {
    disclaimerParts.push(`with ${vehicleText}`);
  }
  if (driverDescription) {
    disclaimerParts.push(`driven by ${driverDescription}`);
  } else {
    disclaimerParts.push(`and ${driverText}`);
  }
  const disclaimerText = disclaimerParts.join(' ') + coverageText + '. Final rates may differ.';

  // Build carrier cards
  const carrierCards = carriers.map(carrier => `
    <div class="quote-card">
      <div class="carrier-logo-section">
        <div class="carrier-name">${carrier.name}</div>
      </div>
      <div class="price-section">
        <div class="monthly-price">
          <div class="price-value">${formatCurrency(carrier.monthly_cost)}/mo</div>
          <div class="price-label">Avg. Price</div>
        </div>
        <div class="annual-price">
          <div class="price-value">${formatCurrency(carrier.annual_cost)}</div>
          <div class="price-label">Est. Annual Cost</div>
        </div>
      </div>
    </div>
  `).join('');

  // Render the complete widget
  container.innerHTML = `
    <div class="quote-container">
      <div class="header-section">
        <div class="car-illustration">
          <img src="${BASE_URL}/assets/images/car-background.png" alt="Car illustration">
        </div>

        <div class="header-branding">
          <img class="powered-by-logo" src="${BASE_URL}/assets/images/powered-by.png" alt="Mercury Insurance - Powered by AIS">
        </div>

        <div class="disclaimer-text">
          ${disclaimerText}
        </div>
      </div>

      <div class="content-area">
        <div class="quotes-list">
          ${carrierCards}
        </div>

        <div class="cta-section">
          <a class="cta-button" href="https://tst.aisinsurance.com/auto-quote?refid5=chatgptapp&zip=${zipCode}" target="_blank" rel="noopener noreferrer">
            Get personalized quote
          </a>
        </div>
      </div>

      <div class="legal-disclosure">
        <p><strong>Important:</strong> These are estimated price ranges based on limited information and industry averages. Actual quotes from carriers may differ significantly based on your complete driving history (accidents, violations), credit score (where permitted), exact coverage selections and deductibles, discounts you may qualify for (bundling, safety features, etc.), and carrier-specific underwriting criteria. To get an accurate quote, you'll need to contact carriers directly or complete a full application.</p>
      </div>
    </div>
  `;

  console.log("✅ Insurance widget rendered");
}

// Check for existing data (like pizzaz does)
if (window.openai && window.openai.toolOutput) {
  console.log("✅ Found window.openai.toolOutput");
  render(window.openai.toolOutput);
}

// Listen for hydration event (like pizzaz does)
window.addEventListener('openai:set_globals', (event) => {
  console.log("🎯 Received openai:set_globals", event.detail);
  if (event.detail && event.detail.globals && event.detail.globals.toolOutput) {
    render(event.detail.globals.toolOutput);
  }
});
