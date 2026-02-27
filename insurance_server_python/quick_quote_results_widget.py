"""Quick quote results display widget markup for the Python MCP server - New Card Design.

IMPORTANT: Images are embedded as base64 data URIs to ensure they work in ChatGPT's
rendering context where external HTTP requests for images are not supported.
All image assets should be converted to base64 and embedded directly in the HTML.
"""

from .widget_assets import CAR_BACKGROUND_BASE64, POWERED_BY_LOGO_BASE64, PHONE_BACKGROUND_BASE64

QUICK_QUOTE_RESULTS_WIDGET_HTML = f"""
<style>
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background: #ffffff;
    padding: 0;
    margin: 0;
  }}

  .quote-container {{
    max-width: 1400px;
    margin: 0 auto;
    background: white;
    border-radius: 24px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0,0,0,0.07);
  }}

  /* Header section */
  .header-section {{
    background: white;
    position: relative;
    padding: 0 0 40px 0;
    overflow: hidden;
  }}

  /* Reduce spacing for phone-only mode */
  .phone-only-mode .header-section {{
    padding: 0 0 8px 0;
  }}

  .phone-only-mode .header-branding {{
    margin-bottom: 8px;
  }}

  .phone-only-mode .phone-call-section {{
    padding: 8px 40px 48px;
  }}

  .car-illustration {{
    width: 100%;
    margin: 0;
    padding: 0;
    line-height: 0;
  }}

  .car-illustration img {{
    width: 100%;
    height: auto;
    display: block;
  }}

  .header-branding {{
    text-align: center;
    padding: 24px 40px 0;
    margin-bottom: 32px;
  }}

  .powered-by-logo {{
    max-width: 280px;
    height: auto;
    margin: 0 auto;
    display: block;
  }}

  .disclaimer-text {{
    text-align: center;
    font-size: 15px;
    color: #546e7a;
    line-height: 1.6;
    max-width: 800px;
    margin: 0 auto;
    padding: 0 40px;
  }}

  /* Main content area */
  .content-area {{
    padding: 32px;
  }}

  /* Quote cards */
  .quotes-list {{
    display: flex;
    flex-direction: column;
    gap: 0;
    margin-bottom: 32px;
  }}

  .quote-card {{
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 24px 32px;
    border-bottom: 1px solid #e0e0e0;
    transition: background 0.2s ease;
  }}

  .quote-card:hover {{
    background: #fafafa;
  }}

  .quote-card:last-child {{
    border-bottom: none;
  }}

  .carrier-logo-section {{
    flex: 0 0 220px;
    display: flex;
    justify-content: flex-start;
    align-items: center;
  }}

  .carrier-logo-section img {{
    max-width: 200px;
    max-height: 55px;
    height: auto;
  }}

  .price-section {{
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-around;
    gap: 40px;
    min-width: 0;
  }}

  .monthly-price, .annual-price {{
    text-align: center;
    flex: 1;
    min-width: 0;
  }}

  .price-value {{
    font-size: 32px;
    font-weight: 700;
    color: #1565c0;
    line-height: 1.2;
    margin-bottom: 4px;
  }}

  .annual-price .price-value {{
    color: #2c3e50;
  }}

  .price-label {{
    font-size: 13px;
    color: #78909c;
    font-weight: 500;
  }}

  /* CTA Button */
  .cta-section {{
    padding: 0 32px 24px;
  }}

  .cta-button {{
    display: block;
    width: 100%;
    padding: 20px;
    background: #e67e22;
    color: white;
    text-decoration: none;
    border-radius: 8px;
    font-size: 18px;
    font-weight: 600;
    text-align: center;
    transition: background 0.2s ease;
    border: none;
    cursor: pointer;
  }}

  .cta-button:hover {{
    background: #d35400;
  }}

  .cta-button::after {{
    content: ' →';
    margin-left: 8px;
  }}

  /* Legal Disclosure */
  .legal-disclosure {{
    padding: 24px 32px 32px;
    background: #f8f9fa;
    border-top: 1px solid #e0e0e0;
  }}

  .legal-disclosure p {{
    font-size: 12px;
    color: #5f6368;
    line-height: 1.6;
    margin: 0;
  }}

  .legal-disclosure strong {{
    font-weight: 600;
    color: #3c4043;
  }}

  /* Hide disclaimer and legal disclosure in phone-only mode */
  .phone-only-mode .disclaimer-text {{
    display: none;
  }}

  .phone-only-mode .legal-disclosure {{
    display: none;
  }}

  /* Loading skeleton styles */
  .loading-skeleton {{
    display: block;
  }}

  .loading-skeleton.hidden {{
    display: none;
  }}

  .skeleton {{
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 8px;
  }}

  @keyframes shimmer {{{{
    0% {{{{
      background-position: 200% 0;
    }}}}
    100% {{{{
      background-position: -200% 0;
    }}}}
  }}}}

  .skeleton-card {{
    padding: 24px 32px;
    border-bottom: 1px solid #e0e0e0;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }}

  .skeleton-logo {{
    flex: 0 0 220px;
    width: 180px;
    height: 50px;
  }}

  .skeleton-prices {{
    flex: 1;
    display: flex;
    gap: 40px;
    justify-content: space-around;
    align-items: center;
  }}

  .skeleton-price {{
    width: 140px;
    height: 50px;
  }}

  .content-loaded {{
    display: none;
  }}

  .content-loaded.visible {{
    display: block;
  }}

  .phone-call-section {{
    display: none;
    padding: 48px 40px;
    text-align: center;
  }}

  .phone-call-section.visible {{
    display: block;
  }}

  .phone-call-icon {{
    font-size: 48px;
    margin-bottom: 20px;
  }}

  .phone-call-title {{
    font-size: 24px;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 16px;
  }}

  .phone-call-text {{
    font-size: 16px;
    color: #666;
    line-height: 1.7;
    max-width: 600px;
    margin: 0 auto 32px;
  }}

  .phone-number {{
    font-size: 32px;
    font-weight: 700;
    color: #1565c0;
    margin-bottom: 16px;
  }}

  .phone-hours {{
    font-size: 14px;
    color: #78909c;
  }}

  /* Tablet and small desktop - make more compact but keep horizontal */
  @media (max-width: 768px) {{
    .quote-card {{
      padding: 20px 24px;
    }}

    .carrier-logo-section {{
      flex: 0 0 180px;
    }}

    .carrier-logo-section img {{
      max-width: 160px;
      max-height: 50px;
    }}

    .price-section {{
      gap: 24px;
    }}

    .price-value {{
      font-size: 28px;
    }}

    .price-label {{
      font-size: 12px;
    }}

    .content-area {{
      padding: 32px 24px;
    }}

    .header-branding {{
      padding: 24px 24px 0;
    }}

    .disclaimer-text {{
      padding: 0 24px;
    }}

    .legal-disclosure {{
      padding: 24px;
    }}

    .legal-disclosure p {{
      font-size: 11px;
    }}
  }}

  /* Very compact - still horizontal down to 475px */
  @media (max-width: 600px) {{
    .quote-card {{
      padding: 16px 20px;
    }}

    .carrier-logo-section {{
      flex: 0 0 140px;
    }}

    .carrier-logo-section img {{
      max-width: 130px;
      max-height: 45px;
    }}

    .price-section {{
      gap: 16px;
    }}

    .price-value {{
      font-size: 24px;
    }}

    .price-label {{
      font-size: 11px;
    }}

    .content-area {{
      padding: 24px 16px;
    }}

    .cta-section {{
      padding: 0 16px 24px;
    }}

    .header-branding {{
      padding: 24px 16px 0;
    }}

    .disclaimer-text {{
      padding: 0 16px;
    }}

    .legal-disclosure {{
      padding: 20px 16px 24px;
    }}

    .legal-disclosure p {{
      font-size: 10px;
    }}
  }}

  /* Only stack vertically below 475px */
  @media (max-width: 474px) {{
    .quote-card {{
      flex-direction: column;
      padding: 24px 16px;
      gap: 20px;
    }}

    .carrier-logo-section {{
      flex: none;
      width: 100%;
      justify-content: center;
    }}

    .carrier-logo-section img {{
      max-width: 180px;
      max-height: 60px;
    }}

    .price-section {{
      flex: none;
      width: 100%;
      gap: 32px;
    }}

    .price-value {{
      font-size: 28px;
    }}

    .price-label {{
      font-size: 12px;
    }}
  }}
</style>

<div class="quote-container" id="quote-container">
  <!-- Loading Skeleton -->
  <div class="loading-skeleton" id="loading-skeleton">
    <div class="header-section">
      <div class="car-illustration">
        <div class="skeleton" style="width: 100%; height: 180px;"></div>
      </div>
      <div class="header-branding">
        <div class="skeleton" style="width: 250px; height: 50px; margin: 0 auto;"></div>
      </div>
      <div class="disclaimer-text">
        <div class="skeleton" style="width: 80%; height: 20px; margin: 0 auto;"></div>
      </div>
    </div>

    <div class="content-area">
      <div class="quotes-list">
        <div class="skeleton-card">
          <div class="skeleton skeleton-logo"></div>
          <div class="skeleton-prices">
            <div class="skeleton skeleton-price"></div>
            <div class="skeleton skeleton-price"></div>
          </div>
        </div>
        <div class="skeleton-card">
          <div class="skeleton skeleton-logo"></div>
          <div class="skeleton-prices">
            <div class="skeleton skeleton-price"></div>
            <div class="skeleton skeleton-price"></div>
          </div>
        </div>
        <div class="skeleton-card">
          <div class="skeleton skeleton-logo"></div>
          <div class="skeleton-prices">
            <div class="skeleton skeleton-price"></div>
            <div class="skeleton skeleton-price"></div>
          </div>
        </div>
      </div>

      <div class="cta-section">
        <div class="skeleton" style="width: 100%; height: 60px;"></div>
      </div>
    </div>

    <!-- Legal Disclosure (in skeleton) -->
    <div class="legal-disclosure">
      <div class="skeleton" style="width: 100%; height: 50px;"></div>
    </div>
  </div>

  <!-- Actual Content (hidden until loaded) -->
  <div class="content-loaded" id="content-loaded">
    <div class="header-section">
      <div class="car-illustration">
        <img id="header-image" src="{CAR_BACKGROUND_BASE64}" alt="Car illustration">
      </div>

      <div class="header-branding">
        <img class="powered-by-logo" src="{POWERED_BY_LOGO_BASE64}" alt="Mercury Insurance - Powered by AIS">
      </div>

      <div class="disclaimer-text" id="disclaimer-text">
        The estimates shown below are assuming you're in the Brea area as a solo driver and own one vehicle. Final rates may differ.
      </div>
    </div>

    <div class="content-area">
      <div class="phone-call-section" id="phone-call-section">
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

      <div class="quotes-list" id="quotes-list">
        <!-- Quotes will be populated by JavaScript -->
      </div>

      <div class="cta-section">
        <a class="cta-button" id="cta-button" href="https://tst.aisinsurance.com?sid=chatgptapp&refid3=mercuryais&zip=90210" target="_blank" rel="noopener noreferrer">
          Get personalized quote
        </a>
      </div>
    </div>

    <!-- Legal Disclosure -->
    <div class="legal-disclosure">
      <p><strong>Important:</strong> These are estimated price ranges based on limited information and industry averages. Actual quotes from carriers may differ significantly based on your complete driving history (accidents, violations), credit score (where permitted), exact coverage selections and deductibles, discounts you may qualify for (bundling, safety features, etc.), and carrier-specific underwriting criteria. To get an accurate quote, you'll need to contact carriers directly or complete a full application.</p>
    </div>
  </div>
</div>

<script>
(() => {{
  if (typeof document === "undefined") return;

  const loadingSkeletonEl = document.getElementById("loading-skeleton");
  const contentLoadedEl = document.getElementById("content-loaded");
  const disclaimerTextEl = document.getElementById("disclaimer-text");
  const quotesListEl = document.getElementById("quotes-list");
  const phoneCallSectionEl = document.getElementById("phone-call-section");
  const ctaButtonEl = document.getElementById("cta-button");
  const headerImageEl = document.getElementById("header-image");
  const quoteContainerEl = document.getElementById("quote-container");

  if (!disclaimerTextEl || !quotesListEl || !loadingSkeletonEl || !contentLoadedEl || !phoneCallSectionEl || !ctaButtonEl || !headerImageEl || !quoteContainerEl) return;

  // Image constants for header switching
  const CAR_BACKGROUND = "{CAR_BACKGROUND_BASE64}";
  const PHONE_BACKGROUND = "{PHONE_BACKGROUND_BASE64}";

  function formatCurrency(value) {{
    if (!value) return "--";
    return `$${{value.toLocaleString()}}`;
  }}

  // Function to build CTA URL with all parameters
  function buildCtaUrl(zipCode, ctaConfig) {{
    const config = ctaConfig || {{}};
    const baseUrl = config.base_url || "https://tst.aisinsurance.com";
    const sid = config.sid || "chatgptapp";
    const refid3 = config.refid3 || "mercuryais";

    return `${{baseUrl}}?sid=${{sid}}&refid3=${{refid3}}&zip=${{zipCode}}`;
  }}

  function updateWidget(data) {{
    if (!data) {{
      console.log("Quick quote widget: No data for widget");
      return;
    }}

    console.log("Quick quote widget: Received data:", data);

    const zipCode = data.zip_code || "";
    const city = data.city || null;
    const state = data.state || null;
    const numDrivers = data.num_drivers || 1;
    const numVehicles = data.num_vehicles || 1;
    const lookupFailed = data.lookup_failed || false;
    const ctaConfig = data.cta_config || {{}};

    // Check if this is a phone-only state (AK, HI, MA) OR if lookup failed
    const phoneOnlyStates = ["AK", "HI", "MA", "Alaska", "Hawaii", "Massachusetts"];
    const isPhoneOnlyState = (state && phoneOnlyStates.includes(state)) || lookupFailed;

    // For phone-only states, ALWAYS force empty carriers
    let carriers = [];

    if (!isPhoneOnlyState) {{
      carriers = data.carriers || [];

      // If no carriers provided, use hard-coded fallback
      if (carriers.length === 0) {{
        console.warn("Quick quote widget: No carriers in data, using fallback");
        carriers = [
          {{ name: "Geico", annual_cost: 3100, monthly_cost: 258 }},
          {{ name: "Progressive Insurance", annual_cost: 3600, monthly_cost: 300 }},
          {{ name: "Safeco Insurance", annual_cost: 3800, monthly_cost: 317 }}
        ];
      }}
    }} else {{
      console.log(`Quick quote widget: ${{state || 'unknown location'}} is a phone-only state/lookup failed - forcing empty carriers and call prompt`);
    }}

    console.log("Quick quote widget: Carriers:", carriers);
    console.log("Quick quote widget: City/State:", city, state);
    console.log("Quick quote widget: Drivers/Vehicles:", numDrivers, numVehicles);

    const driverText = numDrivers === 1 ? "a solo driver" : `${{numDrivers}} drivers`;
    const vehicleText = numVehicles === 1 ? "one vehicle" : `${{numVehicles}} vehicles`;
    const locationText = city ? `the ${{city}} area` : `zip code ${{zipCode}}`;

    // Update disclaimer text with actual data
    disclaimerTextEl.textContent = `The estimates shown below are assuming you're in ${{locationText}} as ${{driverText}} and own ${{vehicleText}}. Final rates may differ.`;

    // Handle phone-only states differently
    if (isPhoneOnlyState) {{
      console.log(`Quick quote widget: ${{state || 'unknown location'}} is a phone-only state/lookup failed - showing call prompt`);

      // Add phone-only mode class to container (hides disclaimer and legal text, reduces spacing)
      quoteContainerEl.classList.add("phone-only-mode");

      // Switch header image to phone background
      headerImageEl.src = PHONE_BACKGROUND;
      headerImageEl.alt = "Phone illustration";

      // Hide quotes list
      quotesListEl.style.display = "none";

      // Personalize phone call text
      const phoneCallTextEl = document.getElementById("phone-call-text");
      if (phoneCallTextEl) {{
        if (lookupFailed) {{
          phoneCallTextEl.textContent = `We're ready to help you get the best insurance rates for zip code ${{zipCode}}. Our licensed agents can provide personalized quotes and answer any questions you have.`;
        }} else {{
          phoneCallTextEl.textContent = `We're ready to help you get the best insurance rates in the ${{city}} area. Our licensed agents specialize in ${{state}} insurance and can provide personalized quotes and answer any questions you have.`;
        }}
      }}

      // Show phone call section
      phoneCallSectionEl.classList.add("visible");

      // Update CTA button to call
      ctaButtonEl.href = "tel:+18887724247";
      ctaButtonEl.textContent = "Call Now";

    }} else {{
      // Normal flow - show quotes
      quoteContainerEl.classList.remove("phone-only-mode");
      quotesListEl.style.display = "";
      phoneCallSectionEl.classList.remove("visible");

      // Reset header image to car background
      headerImageEl.src = CAR_BACKGROUND;
      headerImageEl.alt = "Car illustration";

      // Reset CTA button with configured URL
      ctaButtonEl.href = buildCtaUrl(zipCode, ctaConfig);
      ctaButtonEl.textContent = "Get personalized quote";
    }}

    // Populate quotes list (only if not phone-only state)
    if (!isPhoneOnlyState && carriers.length > 0) {{
      quotesListEl.innerHTML = ""; // Clear existing content

      carriers.forEach((carrier) => {{
        const card = document.createElement("div");
        card.className = "quote-card";

        const logoSrc = carrier.logo || "";

        // Log detailed information to console
        console.log(`Quick quote widget: ${{carrier.name}} details:`);
        if (carrier.confidence) {{
          console.log(`  Confidence: ${{carrier.confidence}}`);
        }}
        if (carrier.range_monthly_low && carrier.range_monthly_high) {{
          console.log(`  Range: ${{formatCurrency(carrier.range_monthly_low)}} - ${{formatCurrency(carrier.range_monthly_high)}}/month`);
        }}
        if (carrier.explanations && carrier.explanations.length > 0) {{
          console.log(`  Pricing factors:`);
          carrier.explanations.forEach(exp => console.log(`    • ${{exp}}`));
        }}

        card.innerHTML = `
          <div class="carrier-logo-section">
            ${{logoSrc ? `<img src="${{logoSrc}}" alt="${{carrier.name}}">` : `<div style="font-weight: 600; font-size: 18px;">${{carrier.name}}</div>`}}
          </div>
          <div class="price-section">
            <div class="monthly-price">
              <div class="price-value">${{formatCurrency(carrier.monthly_cost)}}/mo</div>
              <div class="price-label">Avg. Price</div>
            </div>
            <div class="annual-price">
              <div class="price-value">${{formatCurrency(carrier.annual_cost)}}</div>
              <div class="price-label">Est. Annual Cost</div>
            </div>
          </div>
        `;

        quotesListEl.appendChild(card);
      }});

      console.log(`Quick quote widget: Populated ${{carriers.length}} carriers`);
    }} else if (!isPhoneOnlyState) {{
      console.error("Quick quote widget: No carriers available to display!");
    }}

    // Hide loading skeleton and show content
    loadingSkeletonEl.classList.add("hidden");
    contentLoadedEl.classList.add("visible");
  }}

  // Track hydration calls
  let hydrationCount = 0;
  const hydrationTimestamps = [];

  function hydrate(globals) {{
    hydrationCount++;
    const timestamp = new Date().toISOString();
    hydrationTimestamps.push(timestamp);

    console.log("═══════════════════════════════════════════════════════════");
    console.log("🔄 WIDGET HYDRATION CALL #" + hydrationCount);
    console.log("═══════════════════════════════════════════════════════════");
    console.log("Timestamp:", timestamp);
    console.log("Previous hydration calls:", hydrationTimestamps.length - 1);

    if (hydrationTimestamps.length > 1) {{
      const lastTimestamp = new Date(hydrationTimestamps[hydrationTimestamps.length - 2]);
      const currentTimestamp = new Date(timestamp);
      const timeDiff = (currentTimestamp - lastTimestamp) / 1000;
      console.log("⚠️  Time since last hydration:", timeDiff.toFixed(2), "seconds");

      if (timeDiff < 5) {{
        console.warn("⚠️⚠️⚠️ RAPID HYDRATION DETECTED - Less than 5 seconds since last call!");
      }}
    }}

    console.log("Globals object:", globals);
    console.log("Globals type:", typeof globals);
    console.log("Globals keys:", globals ? Object.keys(globals) : "null");

    if (!globals || typeof globals !== "object") {{
      console.warn("❌ Invalid globals object - skipping hydration");
      console.log("═══════════════════════════════════════════════════════════");
      return;
    }}

    // Try multiple ways to access the data
    let data = null;
    let dataSource = "none";

    // Method 1: Direct access
    try {{
      data = globals.toolOutput || globals.tool_output || globals.structuredContent || globals.structured_content;
      if (data) {{
        dataSource = "direct";
        console.log("✅ Data found via direct access");
      }}
    }} catch (e) {{
      console.log("Quick quote widget: Error accessing toolOutput directly:", e);
    }}

    // Method 2: Check toolResponseMetadata
    if (!data && globals.toolResponseMetadata) {{
      try {{
        data = globals.toolResponseMetadata.structuredContent || globals.toolResponseMetadata.structured_content;
        if (data) {{
          dataSource = "toolResponseMetadata";
          console.log("✅ Data found via toolResponseMetadata");
        }}
      }} catch (e) {{
        console.log("Quick quote widget: Error accessing toolResponseMetadata:", e);
      }}
    }}

    // Method 3: Check widget object
    if (!data && globals.widget) {{
      try {{
        data = globals.widget.structuredContent || globals.widget.structured_content;
        if (data) {{
          dataSource = "widget";
          console.log("✅ Data found via widget object");
        }}
      }} catch (e) {{
        console.log("Quick quote widget: Error accessing widget:", e);
      }}
    }}

    if (data && typeof data === 'object') {{
      console.log("✅ Data found via:", dataSource);
      console.log("Data keys:", Object.keys(data));
      console.log("Number of carriers:", data.carriers ? data.carriers.length : 0);
      console.log("State:", data.state);
      console.log("City:", data.city);
      console.log("ZIP:", data.zip_code);
      console.log("🎨 Calling updateWidget...");
      updateWidget(data);
      console.log("✅ updateWidget completed");
    }} else {{
      console.warn("❌ No valid data found in globals object");
    }}

    console.log("═══════════════════════════════════════════════════════════");
  }}

  // Initial hydration
  console.log("🚀 Widget script loaded - Performing initial hydration");
  const initialGlobals = typeof window !== "undefined" && window.openai ? window.openai : {{}};
  console.log("Initial globals available:", !!window.openai);
  hydrate(initialGlobals);

  // Listen for updates
  console.log("📡 Setting up event listener for openai:set_globals");
  let eventCount = 0;
  window.addEventListener("openai:set_globals", (event) => {{
    eventCount++;
    console.log("═══════════════════════════════════════════════════════════");
    console.log("📨 EVENT RECEIVED: openai:set_globals #" + eventCount);
    console.log("═══════════════════════════════════════════════════════════");
    console.log("Event:", event);
    console.log("Event detail:", event.detail);

    const detail = event.detail;
    if (!detail || !detail.globals) {{
      console.warn("❌ Event detail or globals missing");
      return;
    }}

    console.log("✅ Valid event received, calling hydrate");
    hydrate(detail.globals);
  }});
}})();
</script>
""".strip()
