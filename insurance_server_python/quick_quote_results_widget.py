"""Quick quote results display widget markup for the Python MCP server - Carrier Table Format."""

QUICK_QUOTE_RESULTS_WIDGET_HTML = """
<div id="quick-quote-results-root"></div>
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
    font-size: 18px;
    font-weight: 700;
    color: #c41e3a;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .logo-mercury::before {
    content: "▲";
    font-size: 24px;
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
    grid-template-columns: 1fr 1fr 2fr;
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

  .notes-column {
    text-align: left;
  }

  .notes-label {
    font-size: 12px;
    color: #999;
    margin-bottom: 4px;
    font-weight: 500;
  }

  .notes-text {
    font-size: 14px;
    color: #333;
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

<script>
(() => {
  if (typeof document === "undefined") return;

  const root = document.getElementById("quick-quote-results-root");
  if (!root) return;

  const currencyFormatter = new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });

  function formatCurrency(value) {
    if (value === null || value === undefined) return "--";
    try {
      return currencyFormatter.format(value);
    } catch {
      return `$${value}`;
    }
  }

  function createWidget(data) {
    if (!data) {
      console.error("Quick quote widget: No data provided");
      return null;
    }

    const {
      zip_code,
      city,
      state,
      carriers = []
    } = data;

    const widget = document.createElement("div");
    widget.className = "quote-container";

    // Header
    const header = document.createElement("div");
    header.className = "header";
    header.innerHTML = `
      <div class="logo-mercury">MERCURY INSURANCE</div>
      <div class="powered-by">Powered by AIS</div>
    `;
    widget.appendChild(header);

    // Description
    const description = document.createElement("div");
    description.className = "description";
    description.textContent = `Assuming you're in the ${city || 'Los Angeles'} area as a solo driver and own one vehicle, the estimates shown below are ranges you may see for insurance. However, final rates may differ.`;
    widget.appendChild(description);

    // Carriers Table
    const table = document.createElement("div");
    table.className = "carriers-table";

    carriers.forEach(carrier => {
      const row = document.createElement("div");
      row.className = "carrier-row";

      // Left section - Logo
      const left = document.createElement("div");
      left.className = "carrier-left";

      const logo = document.createElement("img");
      logo.className = "carrier-logo";
      logo.src = carrier.logo || "";
      logo.alt = carrier.name;
      left.appendChild(logo);

      // Right section - Costs and Notes
      const right = document.createElement("div");
      right.className = "carrier-right";

      // Annual Cost
      const annualCost = document.createElement("div");
      annualCost.className = "cost-column";
      annualCost.innerHTML = `
        <div class="cost-label">Est. Annual Cost</div>
        <div class="cost-value">${formatCurrency(carrier.annual_cost)}</div>
      `;
      right.appendChild(annualCost);

      // Monthly Cost
      const monthlyCost = document.createElement("div");
      monthlyCost.className = "cost-column";
      monthlyCost.innerHTML = `
        <div class="cost-label">Est. Monthly Cost</div>
        <div class="cost-value">${formatCurrency(carrier.monthly_cost)}</div>
      `;
      right.appendChild(monthlyCost);

      // Notes
      const notes = document.createElement("div");
      notes.className = "notes-column";
      notes.innerHTML = `
        <div class="notes-label">Notes</div>
        <div class="notes-text">${carrier.notes || ''}</div>
      `;
      right.appendChild(notes);

      row.appendChild(left);
      row.appendChild(right);
      table.appendChild(row);
    });

    widget.appendChild(table);

    // CTA Button
    const ctaContainer = document.createElement("div");
    ctaContainer.className = "cta-container";

    const ctaButton = document.createElement("a");
    ctaButton.className = "cta-button";
    ctaButton.href = `https://aisinsurance.com/?zip=${encodeURIComponent(zip_code)}`;
    ctaButton.target = "_blank";
    ctaButton.rel = "noopener noreferrer";
    ctaButton.textContent = "Continue to Personalized Quote";

    ctaContainer.appendChild(ctaButton);
    widget.appendChild(ctaContainer);

    return widget;
  }

  function render(data) {
    root.innerHTML = "";
    if (!data) {
      root.textContent = "No quick quote data available.";
      return;
    }

    const widget = createWidget(data);
    if (widget) {
      root.appendChild(widget);
    } else {
      root.textContent = "Unable to display quick quote.";
    }
  }

  function hydrate(globals) {
    console.log("Quick quote widget: Hydrating with globals", globals);
    if (!globals || typeof globals !== "object") {
      console.warn("Quick quote widget: No valid globals object");
      return;
    }
    const toolOutput = globals.toolOutput || globals.tool_output;
    console.log("Quick quote widget: toolOutput", toolOutput);
    if (toolOutput) {
      render(toolOutput);
    } else {
      console.warn("Quick quote widget: No toolOutput found in globals");
    }
  }

  // Initial hydration
  const initialGlobals =
    typeof window !== "undefined" && window.openai ? window.openai : {};
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
