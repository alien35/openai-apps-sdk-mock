"""Quick quote results display widget markup for the Python MCP server - Carrier Table Format."""

QUICK_QUOTE_RESULTS_WIDGET_HTML = """
<style>
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background: #f5f5f5;
    padding: 20px;
  }

  .quote-container {
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    padding: 40px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }

  .header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
  }

  .logo-mercury {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .logo-mercury img {
    height: 40px;
    width: auto;
  }

  .powered-by {
    font-size: 12px;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .description {
    font-size: 14px;
    color: #666;
    margin-bottom: 32px;
    line-height: 1.6;
  }

  .carriers-table {
    border: 1px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 32px;
  }

  .carrier-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px 20px;
    border-bottom: 1px solid #ddd;
  }

  .carrier-row:last-child {
    border-bottom: none;
  }

  .carrier-row:nth-child(even) {
    background: #fafafa;
  }

  .carrier-left {
    flex: 0 0 200px;
    display: flex;
    align-items: center;
  }

  .carrier-logo {
    max-width: 100%;
    height: auto;
    max-height: 60px;
  }

  .carrier-right {
    flex: 1;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
    align-items: center;
  }

  .cost-column {
    text-align: left;
  }

  .cost-label {
    font-size: 12px;
    color: #999;
    margin-bottom: 4px;
    font-weight: 500;
  }

  .cost-value {
    font-size: 28px;
    font-weight: 700;
    color: #2563eb;
  }

  .cta-container {
    text-align: center;
  }

  .cta-button {
    display: inline-block;
    padding: 16px 48px;
    background: #e67e50;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    font-size: 18px;
    font-weight: 600;
    transition: background 0.2s ease;
  }

  .cta-button:hover {
    background: #d46940;
  }

  @media (max-width: 768px) {
    .carrier-row {
      grid-template-columns: 1fr;
      gap: 12px;
    }

    .cost-value {
      font-size: 20px;
    }
  }
</style>

<div class="quote-container">
  <div class="header">
    <div class="logo-mercury">
      <img id="mercury-logo" src="" alt="Insurance Carrier">
    </div>
    <div class="powered-by">Powered by AIS</div>
  </div>

  <div class="description" id="quote-description">
    <!-- Description will be populated by JavaScript -->
  </div>

  <div class="carriers-table">
    <!-- Carriers will be populated by JavaScript -->
  </div>

  <div class="cta-container">
    <a class="cta-button" href="https://aisinsurance.com/?zip=90210" target="_blank" rel="noopener noreferrer">
      Continue to Personalized Quote
    </a>
  </div>
</div>

<script>
(() => {
  if (typeof document === "undefined") return;

  const descriptionEl = document.getElementById("quote-description");
  const mercuryHeaderLogoEl = document.getElementById("mercury-logo");
  const carriersTableEl = document.querySelector(".carriers-table");

  if (!descriptionEl || !carriersTableEl) return;

  // Logo handling moved to backend - logos are now passed as base64 data URIs in carrier.logo field

  function formatCurrency(value) {
    if (!value) return "--";
    return `$${value.toLocaleString()}`;
  }

  function updateWidget(data) {
    if (!data) {
      console.log("Quick quote widget: No data for widget");
      return;
    }

    console.log("Quick quote widget: Received data:", data);

    const city = data.city || "Los Angeles";
    const state = data.state || "CA";
    const numDrivers = data.num_drivers || (data.additional_driver ? 2 : 1);
    const numVehicles = data.num_vehicles || (data.vehicle_2 ? 2 : 1);

    // Use provided carriers or fallback to defaults
    let carriers = data.carriers || [];

    // If no carriers provided, use hard-coded fallback (California defaults)
    if (carriers.length === 0) {
      console.warn("Quick quote widget: No carriers in data, using fallback");
      carriers = [
        { name: "Orion Indemnity", annual_cost: 3360, monthly_cost: 280 },
        { name: "Mercury Auto Insurance", annual_cost: 3200, monthly_cost: 267 },
        { name: "Progressive Insurance", annual_cost: 4064, monthly_cost: 339 }
      ];
    }

    console.log("Quick quote widget: Carriers:", carriers);
    console.log("Quick quote widget: City/State:", city, state);
    console.log("Quick quote widget: Drivers/Vehicles:", numDrivers, numVehicles);

    const driverText = numDrivers === 1 ? "a solo driver" : `${numDrivers} drivers`;
    const vehicleText = numVehicles === 1 ? "one vehicle" : `${numVehicles} vehicles`;

    descriptionEl.textContent = `Assuming you're in the ${city} area as ${driverText} and own ${vehicleText}, the estimates shown below are ranges you may see for insurance. However, final rates may differ.`;

    // Set header logo to match the first carrier
    if (carriers.length > 0 && carriers[0].logo) {
      mercuryHeaderLogoEl.src = carriers[0].logo;
      mercuryHeaderLogoEl.alt = carriers[0].name;
    }

    // Populate carriers table dynamically
    if (carriers.length > 0) {
      carriersTableEl.innerHTML = ""; // Clear existing content

      carriers.forEach(carrier => {
        const row = document.createElement("div");
        row.className = "carrier-row";

        // Use logo from backend (base64 data URI)
        const logoSrc = carrier.logo || "";

        row.innerHTML = `
          <div class="carrier-left">
            ${logoSrc ? `<img class="carrier-logo" src="${logoSrc}" alt="${carrier.name}">` : `<div style="font-weight: 600; font-size: 16px;">${carrier.name}</div>`}
          </div>
          <div class="carrier-right">
            <div class="cost-column">
              <div class="cost-label">Est. Annual Cost</div>
              <div class="cost-value">${formatCurrency(carrier.annual_cost)}</div>
            </div>
            <div class="cost-column">
              <div class="cost-label">Est. Monthly Cost</div>
              <div class="cost-value">${formatCurrency(carrier.monthly_cost)}</div>
            </div>
          </div>
        `;

        carriersTableEl.appendChild(row);
      });

      console.log(`Quick quote widget: Populated ${carriers.length} carriers`);
    } else {
      console.error("Quick quote widget: No carriers available to display!");
    }
  }

  function hydrate(globals) {
    console.log("Quick quote widget: Hydrating widget");
    console.log("Quick quote widget: globals keys:", Object.keys(globals || {}));

    if (!globals || typeof globals !== "object") {
      console.warn("Quick quote widget: No valid globals object");
      return;
    }

    const toolOutput = globals.toolOutput || globals.tool_output || globals.structuredContent || globals.structured_content;
    console.log("Quick quote widget: toolOutput", toolOutput);

    if (toolOutput) {
      if (toolOutput.carriers) {
        console.log(`Quick quote widget: Found ${toolOutput.carriers.length} carriers in toolOutput`);
        toolOutput.carriers.forEach((c, i) => {
          console.log(`  Carrier ${i+1}: ${c.name} - $${c.annual_cost}/$${c.monthly_cost}`);
        });
      } else {
        console.warn("Quick quote widget: NO CARRIERS in toolOutput!", toolOutput);
      }
      updateWidget(toolOutput);
    } else {
      console.error("Quick quote widget: No toolOutput found. globals keys:", Object.keys(globals));
    }
  }

  // Initial hydration
  const initialGlobals = typeof window !== "undefined" && window.openai ? window.openai : {};
  hydrate(initialGlobals);

  // Listen for updates
  window.addEventListener("openai:set_globals", (event) => {
    const detail = event.detail;
    if (!detail || !detail.globals) return;
    hydrate(detail.globals);
  });
})();
</script>
""".strip()
