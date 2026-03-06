"""Ultra-minimal test widget to debug Android rendering issues."""

SIMPLE_TEST_WIDGET_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      padding: 20px;
      background: #f5f5f5;
    }
    .container {
      background: white;
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .title {
      font-size: 24px;
      font-weight: bold;
      color: #333;
      margin-bottom: 16px;
    }
    .message {
      font-size: 16px;
      color: #666;
      line-height: 1.5;
    }
    .data-display {
      margin-top: 16px;
      padding: 16px;
      background: #f0f0f0;
      border-radius: 8px;
      font-family: monospace;
      font-size: 14px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="title">Simple Test Widget</div>
    <div class="message">If you can see this, the widget HTML is rendering.</div>
    <div class="data-display" id="data-display">Waiting for data...</div>
  </div>

  <script>
    console.log("🟢 Simple test widget script loaded");
    
    // Display initial state
    const dataDisplay = document.getElementById('data-display');
    
    function updateDisplay(data) {
      console.log("📦 Received data:", data);
      dataDisplay.textContent = JSON.stringify(data, null, 2);
    }
    
    // Check if globals already exist
    if (window.openai && window.openai.toolOutput) {
      console.log("✅ Found existing window.openai.toolOutput");
      updateDisplay(window.openai.toolOutput);
    } else {
      console.log("⏳ Waiting for openai:set_globals event");
    }
    
    // Listen for hydration event
    window.addEventListener('openai:set_globals', (event) => {
      console.log("🎯 Received openai:set_globals event", event.detail);
      if (event.detail && event.detail.globals && event.detail.globals.toolOutput) {
        updateDisplay(event.detail.globals.toolOutput);
      }
    });
    
    console.log("👂 Event listener registered for openai:set_globals");
  </script>
</body>
</html>
"""
