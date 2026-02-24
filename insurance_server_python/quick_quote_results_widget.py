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

  /* Loading skeleton styles */
  .loading-skeleton {
    display: block;
  }

  .loading-skeleton.hidden {
    display: none;
  }

  .skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 4px;
  }

  @keyframes shimmer {
    0% {
      background-position: 200% 0;
    }
    100% {
      background-position: -200% 0;
    }
  }

  .skeleton-logo {
    width: 120px;
    height: 40px;
    margin-right: 12px;
  }

  .skeleton-description {
    height: 20px;
    width: 80%;
    margin-bottom: 32px;
  }

  .skeleton-carrier {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px 20px;
    border-bottom: 1px solid #ddd;
  }

  .skeleton-carrier:last-child {
    border-bottom: none;
  }

  .skeleton-carrier-logo {
    width: 150px;
    height: 50px;
  }

  .skeleton-costs {
    display: flex;
    gap: 60px;
    flex: 1;
    justify-content: flex-end;
  }

  .skeleton-cost {
    width: 120px;
    height: 40px;
  }

  .content-loaded {
    display: none;
  }

  .content-loaded.visible {
    display: block;
  }

  .phone-call-section {
    display: none;
    border: 1px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 32px;
  }

  .phone-call-section.visible {
    display: block;
  }

  .phone-call-content {
    text-align: center;
    padding: 48px 40px;
    background: white;
  }

  .phone-call-icon {
    font-size: 48px;
    margin-bottom: 20px;
    opacity: 0.9;
  }

  .phone-call-title {
    font-size: 22px;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 12px;
  }

  .phone-call-text {
    font-size: 15px;
    color: #666;
    line-height: 1.7;
    max-width: 560px;
    margin: 0 auto 28px;
  }

  .phone-number {
    font-size: 28px;
    font-weight: 700;
    color: #2563eb;
    margin-bottom: 16px;
    letter-spacing: 0.5px;
  }

  .phone-hours {
    font-size: 14px;
    color: #6b7280;
    line-height: 1.6;
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
  <!-- Loading Skeleton -->
  <div class="loading-skeleton" id="loading-skeleton">
    <div class="header">
      <div class="skeleton skeleton-logo"></div>
      <div class="powered-by">Powered by AIS</div>
    </div>

    <div class="skeleton skeleton-description"></div>

    <div class="carriers-table">
      <div class="skeleton-carrier">
        <div class="skeleton skeleton-carrier-logo"></div>
        <div class="skeleton-costs">
          <div class="skeleton skeleton-cost"></div>
          <div class="skeleton skeleton-cost"></div>
        </div>
      </div>
      <div class="skeleton-carrier">
        <div class="skeleton skeleton-carrier-logo"></div>
        <div class="skeleton-costs">
          <div class="skeleton skeleton-cost"></div>
          <div class="skeleton skeleton-cost"></div>
        </div>
      </div>
      <div class="skeleton-carrier">
        <div class="skeleton skeleton-carrier-logo"></div>
        <div class="skeleton-costs">
          <div class="skeleton skeleton-cost"></div>
          <div class="skeleton skeleton-cost"></div>
        </div>
      </div>
    </div>

    <div class="cta-container">
      <div class="skeleton cta-button" style="width: 300px; height: 56px; margin: 0 auto;"></div>
    </div>
  </div>

  <!-- Actual Content (hidden until loaded) -->
  <div class="content-loaded" id="content-loaded">
    <div class="header">
      <div class="logo-mercury">
        <img id="mercury-logo" src="" alt="Insurance Carrier">
      </div>
      <div class="powered-by">Powered by AIS</div>
    </div>

    <div class="description" id="quote-description">
      <!-- Description will be populated by JavaScript -->
    </div>

    <div class="carriers-table" id="carriers-table-content">
      <!-- Carriers will be populated by JavaScript -->
    </div>

    <div class="phone-call-section" id="phone-call-section">
      <div class="phone-call-content">
        <div class="phone-call-icon">📞</div>
        <div class="phone-call-title">Speak with a Licensed Agent</div>
        <div class="phone-call-text" id="phone-call-text">
          To get your personalized quote, please call us. Our licensed insurance agents specialize in your area and can help you find the best coverage options and competitive rates.
        </div>
        <div class="phone-number">(888) 772-4247</div>
        <div class="phone-hours">
          Monday - Friday: 8am - 8pm ET<br>
          Saturday: 9am - 5pm ET
        </div>
      </div>
    </div>

    <div class="cta-container">
      <a class="cta-button" id="cta-button" href="https://aisinsurance.com/?zip=90210" target="_blank" rel="noopener noreferrer">
        Continue to Personalized Quote
      </a>
    </div>

    <div class="disclaimer" id="disclaimer" style="margin-top: 32px; padding: 16px; background: #f9fafb; border-left: 3px solid #2563eb; font-size: 12px; color: #666; line-height: 1.6;">
      <strong style="color: #333;">Important:</strong> These are estimated price ranges based on limited information and industry averages. Actual quotes from carriers may differ significantly based on your complete driving history (accidents, violations), credit score (where permitted), exact coverage selections and deductibles, discounts you may qualify for (bundling, safety features, etc.), and carrier-specific underwriting criteria. To get an accurate quote, you'll need to contact carriers directly or complete a full application.
    </div>
  </div>
</div>

<script>
(() => {
  if (typeof document === "undefined") return;

  const loadingSkeletonEl = document.getElementById("loading-skeleton");
  const contentLoadedEl = document.getElementById("content-loaded");
  const descriptionEl = document.getElementById("quote-description");
  const mercuryHeaderLogoEl = document.getElementById("mercury-logo");
  const carriersTableEl = document.getElementById("carriers-table-content");
  const phoneCallSectionEl = document.getElementById("phone-call-section");
  const ctaButtonEl = document.getElementById("cta-button");
  const disclaimerEl = document.getElementById("disclaimer");

  if (!descriptionEl || !carriersTableEl || !loadingSkeletonEl || !contentLoadedEl || !phoneCallSectionEl || !ctaButtonEl) return;

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

    const zipCode = data.zip_code || "";
    const city = data.city || null;
    const state = data.state || null;
    const numDrivers = data.num_drivers || (data.additional_driver ? 2 : 1);
    const numVehicles = data.num_vehicles || (data.vehicle_2 ? 2 : 1);
    const lookupFailed = data.lookup_failed || false;

    // Check if this is a phone-only state (AK, HI, MA) OR if lookup failed
    // IMPORTANT: Check this FIRST before processing carriers
    // Note: State can be abbreviation ("MA") OR full name ("Massachusetts")
    const phoneOnlyStates = ["AK", "HI", "MA", "Alaska", "Hawaii", "Massachusetts"];
    const isPhoneOnlyState = (state && phoneOnlyStates.includes(state)) || lookupFailed;

    // For phone-only states, ALWAYS force empty carriers (ignore backend data)
    // This provides defense-in-depth: even if backend mistakenly sends carriers,
    // we'll show the call prompt based on state alone
    let carriers = [];

    if (!isPhoneOnlyState) {
      // Only process carriers for non-phone-only states
      carriers = data.carriers || [];

      // If no carriers provided, use hard-coded fallback (defaults)
      if (carriers.length === 0) {
        console.warn("Quick quote widget: No carriers in data, using fallback");
        carriers = [
          { name: "Geico", annual_cost: 3100, monthly_cost: 258 },
          { name: "Progressive Insurance", annual_cost: 3600, monthly_cost: 300 },
          { name: "Safeco Insurance", annual_cost: 3800, monthly_cost: 317 }
        ];
      }
    } else {
      console.log(`Quick quote widget: ${state || 'unknown location'} is a phone-only state/lookup failed - forcing empty carriers and call prompt`);
    }

    console.log("Quick quote widget: Carriers:", carriers);
    console.log("Quick quote widget: City/State:", city, state);
    console.log("Quick quote widget: Drivers/Vehicles:", numDrivers, numVehicles);
    console.log("Quick quote widget: Lookup failed:", lookupFailed);

    const driverText = numDrivers === 1 ? "a solo driver" : `${numDrivers} drivers`;
    const vehicleText = numVehicles === 1 ? "one vehicle" : `${numVehicles} vehicles`;

    // Use city if available, otherwise use zip code (don't default to "Los Angeles")
    const locationText = city ? `the ${city} area` : `zip code ${zipCode}`;
    descriptionEl.textContent = `Assuming you're in ${locationText} as ${driverText} and own ${vehicleText}, the estimates shown below are ranges you may see for insurance. However, final rates may differ.`;

    // Always use Mercury logo in header
    if (data.mercury_logo) {
      mercuryHeaderLogoEl.src = data.mercury_logo;
      mercuryHeaderLogoEl.alt = "Mercury Auto Insurance";
    }

    // Handle phone-only states differently
    if (isPhoneOnlyState) {
      console.log(`Quick quote widget: ${state || 'unknown location'} is a phone-only state/lookup failed - showing call prompt`);

      // Hide carrier table, regular description, and disclaimer
      carriersTableEl.style.display = "none";
      descriptionEl.style.display = "none";
      if (disclaimerEl) disclaimerEl.style.display = "none";

      // Personalize phone call text with city/state (or zip code if lookup failed)
      const phoneCallTextEl = document.getElementById("phone-call-text");
      if (phoneCallTextEl) {
        if (lookupFailed) {
          // When lookup fails, use zip code instead of city/state
          phoneCallTextEl.textContent = `We're ready to help you get the best insurance rates for zip code ${zipCode}. Our licensed agents can provide personalized quotes and answer any questions you have.`;
        } else {
          // Normal phone-only state with known city/state
          phoneCallTextEl.textContent = `We're ready to help you get the best insurance rates in the ${city} area. Our licensed agents specialize in ${state} insurance and can provide personalized quotes and answer any questions you have.`;
        }
      }

      // Show phone call section
      phoneCallSectionEl.classList.add("visible");

      // Update CTA button to call
      ctaButtonEl.href = "tel:+18887724247";
      ctaButtonEl.textContent = "Call Now";
      ctaButtonEl.style.background = "#e67e50"; // Keep brand orange color

    } else {
      // Normal flow - show carrier table
      carriersTableEl.style.display = "";
      descriptionEl.style.display = "";
      if (disclaimerEl) disclaimerEl.style.display = "";
      phoneCallSectionEl.classList.remove("visible");

      // Reset CTA button to normal
      ctaButtonEl.href = "https://aisinsurance.com/?zip=90210";
      ctaButtonEl.textContent = "Continue to Personalized Quote";
      ctaButtonEl.style.background = "#e67e50";
    }

    // Populate carriers table dynamically (only if not phone-only state)
    if (!isPhoneOnlyState && carriers.length > 0) {
      carriersTableEl.innerHTML = ""; // Clear existing content

      carriers.forEach((carrier, idx) => {
        const row = document.createElement("div");
        row.className = "carrier-row";

        // Use logo from backend (base64 data URI)
        const logoSrc = carrier.logo || "";

        // Log detailed information to console (not displayed in UI)
        console.log(`Quick quote widget: ${carrier.name} details:`);
        if (carrier.confidence) {
          console.log(`  Confidence: ${carrier.confidence}`);
        }
        if (carrier.range_low && carrier.range_high) {
          console.log(`  Range: $${carrier.range_low.toLocaleString()} - $${carrier.range_high.toLocaleString()}/month`);
        }
        if (carrier.explanations && carrier.explanations.length > 0) {
          console.log(`  Pricing factors:`);
          carrier.explanations.forEach(exp => console.log(`    • ${exp}`));
        }

        row.innerHTML = `
          <div class="carrier-left">
            ${logoSrc ? `<img class="carrier-logo" src="${logoSrc}" alt="${carrier.name}">` : `<div style="font-weight: 600; font-size: 16px;">${carrier.name}</div>`}
          </div>
          <div class="carrier-right">
            <div class="cost-column">
              <div class="cost-label">Est. Monthly Cost</div>
              <div class="cost-value">${formatCurrency(carrier.monthly_cost)}</div>
            </div>
            <div class="cost-column">
              <div class="cost-label">Est. Annual Cost</div>
              <div class="cost-value">${formatCurrency(carrier.annual_cost)}</div>
            </div>
          </div>
        `;

        carriersTableEl.appendChild(row);
      });

      console.log(`Quick quote widget: Populated ${carriers.length} carriers`);
    } else {
      console.error("Quick quote widget: No carriers available to display!");
    }

    // Hide loading skeleton and show content
    loadingSkeletonEl.classList.add("hidden");
    contentLoadedEl.classList.add("visible");
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
