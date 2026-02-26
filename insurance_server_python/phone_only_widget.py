"""Phone-only state widget for states that require a phone call (AK, HI, MA).

IMPORTANT: This widget is specifically for states where online quoting is not available
and customers must call to speak with a licensed agent.
"""

from .widget_assets import PHONE_BACKGROUND_BASE64, POWERED_BY_LOGO_BASE64

PHONE_ONLY_WIDGET_HTML = f"""
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

  .phone-container {{
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
    padding: 0 0 8px 0;
    overflow: hidden;
  }}

  .phone-illustration {{
    width: 100%;
    margin: 0;
    padding: 0;
    line-height: 0;
  }}

  .phone-illustration img {{
    width: 100%;
    height: auto;
    display: block;
  }}

  .header-branding {{
    text-align: center;
    padding: 24px 40px 0;
    margin-bottom: 8px;
  }}

  .powered-by-logo {{
    max-width: 280px;
    height: auto;
    margin: 0 auto;
    display: block;
  }}

  /* Main content area */
  .content-area {{
    padding: 8px 40px 48px;
    text-align: center;
  }}

  .phone-call-icon {{
    font-size: 64px;
    margin-bottom: 24px;
  }}

  .phone-call-title {{
    font-size: 28px;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 16px;
  }}

  .phone-call-text {{
    font-size: 17px;
    color: #4b5563;
    line-height: 1.7;
    max-width: 600px;
    margin: 0 auto 32px;
  }}

  .phone-number {{
    font-size: 36px;
    font-weight: 700;
    color: #1565c0;
    margin-bottom: 16px;
  }}

  .phone-hours {{
    font-size: 15px;
    color: #78909c;
    line-height: 1.6;
  }}

  /* CTA Button */
  .cta-section {{
    padding: 0 40px 32px;
  }}

  .cta-button {{
    display: block;
    width: 100%;
    max-width: 400px;
    margin: 0 auto;
    padding: 18px;
    background: #1565c0;
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
    background: #0d47a1;
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

  .content-loaded {{
    display: none;
  }}

  .content-loaded.visible {{
    display: block;
  }}

  /* Responsive styles */
  @media (max-width: 768px) {{
    .header-branding {{
      padding: 20px 24px 0;
    }}

    .content-area {{
      padding: 8px 24px 40px;
    }}

    .phone-call-icon {{
      font-size: 56px;
    }}

    .phone-call-title {{
      font-size: 24px;
    }}

    .phone-call-text {{
      font-size: 16px;
    }}

    .phone-number {{
      font-size: 32px;
    }}

    .cta-section {{
      padding: 0 24px 32px;
    }}
  }}

  @media (max-width: 474px) {{
    .header-branding {{
      padding: 16px 16px 0;
    }}

    .content-area {{
      padding: 8px 16px 32px;
    }}

    .phone-call-icon {{
      font-size: 48px;
    }}

    .phone-call-title {{
      font-size: 22px;
    }}

    .phone-call-text {{
      font-size: 15px;
    }}

    .phone-number {{
      font-size: 28px;
    }}

    .cta-section {{
      padding: 0 16px 24px;
    }}
  }}
</style>

<div class="phone-container" id="phone-container">
  <!-- Loading Skeleton -->
  <div class="loading-skeleton" id="loading-skeleton">
    <div class="header-section">
      <div class="phone-illustration">
        <div class="skeleton" style="width: 100%; height: 180px;"></div>
      </div>
      <div class="header-branding">
        <div class="skeleton" style="width: 250px; height: 50px; margin: 0 auto;"></div>
      </div>
    </div>

    <div class="content-area">
      <div class="skeleton" style="width: 80px; height: 80px; margin: 0 auto 24px; border-radius: 50%;"></div>
      <div class="skeleton" style="width: 300px; height: 30px; margin: 0 auto 16px;"></div>
      <div class="skeleton" style="width: 500px; height: 60px; margin: 0 auto 32px; max-width: 90%;"></div>
      <div class="skeleton" style="width: 280px; height: 40px; margin: 0 auto 16px;"></div>
      <div class="skeleton" style="width: 200px; height: 20px; margin: 0 auto;"></div>
    </div>

    <div class="cta-section">
      <div class="skeleton" style="width: 100%; max-width: 400px; height: 60px; margin: 0 auto;"></div>
    </div>
  </div>

  <!-- Actual Content (hidden until loaded) -->
  <div class="content-loaded" id="content-loaded">
    <div class="header-section">
      <div class="phone-illustration">
        <img src="{PHONE_BACKGROUND_BASE64}" alt="Phone illustration">
      </div>

      <div class="header-branding">
        <img class="powered-by-logo" src="{POWERED_BY_LOGO_BASE64}" alt="Mercury Insurance - Powered by AIS">
      </div>
    </div>

    <div class="content-area">
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

    <div class="cta-section">
      <a class="cta-button" href="tel:+18887724247">Call Now</a>
    </div>
  </div>
</div>

<script>
(() => {{
  if (typeof document === "undefined") return;

  const loadingSkeletonEl = document.getElementById("loading-skeleton");
  const contentLoadedEl = document.getElementById("content-loaded");
  const phoneCallTextEl = document.getElementById("phone-call-text");

  if (!loadingSkeletonEl || !contentLoadedEl || !phoneCallTextEl) return;

  function updateWidget(data) {{
    if (!data) {{
      console.log("Phone-only widget: No data provided");
      return;
    }}

    console.log("Phone-only widget: Received data:", data);

    const zipCode = data.zip_code || "";
    const city = data.city || null;
    const state = data.state || null;
    const lookupFailed = data.lookup_failed || false;

    // Personalize the message based on location
    if (lookupFailed) {{
      phoneCallTextEl.textContent = `We're ready to help you get the best insurance rates for zip code ${{zipCode}}. Our licensed agents can provide personalized quotes and answer any questions you have.`;
    }} else if (city && state) {{
      phoneCallTextEl.textContent = `We're ready to help you get the best insurance rates in the ${{city}} area. Our licensed agents specialize in ${{state}} insurance and can provide personalized quotes and answer any questions you have.`;
    }} else {{
      phoneCallTextEl.textContent = "To get your personalized quote, please call us. Our licensed insurance agents specialize in your area and can help you find the best coverage options and competitive rates.";
    }}

    // Hide loading skeleton and show content
    loadingSkeletonEl.classList.add("hidden");
    contentLoadedEl.classList.add("visible");
  }}

  function hydrate(globals) {{
    if (!globals || typeof globals !== "object") {{
      return;
    }}

    // Try multiple ways to access the data
    let data = null;

    // Method 1: Direct access
    try {{
      data = globals.toolOutput || globals.tool_output || globals.structuredContent || globals.structured_content;
    }} catch (e) {{
      // Silently continue
    }}

    // Method 2: Check toolResponseMetadata
    if (!data && globals.toolResponseMetadata) {{
      try {{
        data = globals.toolResponseMetadata.structuredContent || globals.toolResponseMetadata.structured_content;
      }} catch (e) {{
        // Silently continue
      }}
    }}

    // Method 3: Check widget object
    if (!data && globals.widget) {{
      try {{
        data = globals.widget.structuredContent || globals.widget.structured_content;
      }} catch (e) {{
        // Silently continue
      }}
    }}

    if (data && typeof data === 'object') {{
      updateWidget(data);
    }}
  }}

  // Initial hydration
  const initialGlobals = typeof window !== "undefined" && window.openai ? window.openai : {{}};
  hydrate(initialGlobals);

  // Listen for updates
  window.addEventListener("openai:set_globals", (event) => {{
    const detail = event.detail;
    if (!detail || !detail.globals) return;
    hydrate(detail.globals);
  }});
}})();
</script>
""".strip()
