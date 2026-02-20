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

<div class="quote-container">
  <div class="header">
    <div class="logo-mercury">MERCURY INSURANCE</div>
    <div class="powered-by">Powered by AIS</div>
  </div>

  <div class="description">
    Assuming you're in the Los Angeles area as a solo driver and own one vehicle, the estimates shown below are ranges you may see for insurance. However, final rates may differ.
  </div>

  <div class="carriers-table">
    <!-- Mercury Auto Insurance -->
    <div class="carrier-row">
      <div class="carrier-left">
        <img class="carrier-logo" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 60'%3E%3Ctext x='10' y='40' font-family='Arial' font-size='24' font-weight='bold' fill='%23c41e3a'%3E%E2%96%B2 MERCURY%3C/text%3E%3C/svg%3E" alt="Mercury Auto Insurance">
      </div>
      <div class="carrier-right">
        <div class="cost-column">
          <div class="cost-label">Est. Annual Cost</div>
          <div class="cost-value">$3,200</div>
        </div>
        <div class="cost-column">
          <div class="cost-label">Est. Monthly Cost</div>
          <div class="cost-value">$267</div>
        </div>
        <div class="notes-column">
          <div class="notes-label">Notes</div>
          <div class="notes-text">Strong digital tools & mobile app</div>
        </div>
      </div>
    </div>

    <!-- Progressive Insurance -->
    <div class="carrier-row">
      <div class="carrier-left">
        <img class="carrier-logo" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 60'%3E%3Ctext x='10' y='40' font-family='Arial' font-size='20' font-weight='bold' fill='%230066b2'%3EPROGRESSIVE%3C/text%3E%3C/svg%3E" alt="Progressive Insurance">
      </div>
      <div class="carrier-right">
        <div class="cost-column">
          <div class="cost-label">Est. Annual Cost</div>
          <div class="cost-value">$4,064</div>
        </div>
        <div class="cost-column">
          <div class="cost-label">Est. Monthly Cost</div>
          <div class="cost-value">$339</div>
        </div>
        <div class="notes-column">
          <div class="notes-label">Notes</div>
          <div class="notes-text">Best balance of cost & claims service</div>
        </div>
      </div>
    </div>

    <!-- Orion -->
    <div class="carrier-row">
      <div class="carrier-left">
        <img class="carrier-logo" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 60'%3E%3Ctext x='10' y='40' font-family='Arial' font-size='24' font-weight='bold' fill='%23004080'%3EORION%3C/text%3E%3C/svg%3E" alt="Orion">
      </div>
      <div class="carrier-right">
        <div class="cost-column">
          <div class="cost-label">Est. Annual Cost</div>
          <div class="cost-value">$3,360</div>
        </div>
        <div class="cost-column">
          <div class="cost-label">Est. Monthly Cost</div>
          <div class="cost-value">$280</div>
        </div>
        <div class="notes-column">
          <div class="notes-label">Notes</div>
          <div class="notes-text">Competitive rates for safe drivers</div>
        </div>
      </div>
    </div>
  </div>

  <div class="cta-container">
    <a class="cta-button" href="https://aisinsurance.com/?zip=90210" target="_blank" rel="noopener noreferrer">
      Continue to Personalized Quote
    </a>
  </div>
</div>
""".strip()
