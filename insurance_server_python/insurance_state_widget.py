"""Simplified insurance state widget markup for the Python MCP server."""

INSURANCE_STATE_WIDGET_HTML = """
<div id=\"insurance-state-root\"></div>
<style>
  :root {
    color-scheme: light dark;
  }

  #insurance-state-root {
    font-family: \"Inter\", \"Segoe UI\", system-ui, -apple-system,
      BlinkMacSystemFont, \"Helvetica Neue\", Arial, sans-serif;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 180px;
    padding: 16px;
  }

  .insurance-hello-widget {
    border-radius: 16px;
    border: 1px solid rgba(15, 23, 42, 0.12);
    background: rgba(255, 255, 255, 0.94);
    padding: 32px 40px;
    font-size: 20px;
    font-weight: 600;
    color: rgba(15, 23, 42, 0.84);
    box-shadow: 0 18px 48px rgba(15, 23, 42, 0.12);
    text-align: center;
  }

  @media (prefers-color-scheme: dark) {
    .insurance-hello-widget {
      background: rgba(15, 23, 42, 0.9);
      color: rgba(226, 232, 240, 0.92);
      border-color: rgba(255, 255, 255, 0.14);
      box-shadow: 0 18px 48px rgba(0, 0, 0, 0.45);
    }
  }
</style>
<script>
  (function () {
    const root = document.getElementById("insurance-state-root");
    if (!root) {
      console.warn("[insurance-state-widget] root element not found");
      return;
    }

    const container = document.createElement("div");
    container.className = "insurance-hello-widget";
    container.textContent = "Hello insurance world!";

    root.appendChild(container);
  })();
</script>
"""
