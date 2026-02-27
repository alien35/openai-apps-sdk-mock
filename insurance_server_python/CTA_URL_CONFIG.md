# CTA URL Configuration Guide

This guide explains how to configure the "Get personalized quote" button URL in the insurance widgets.

## 📍 Configuration File

**File:** `insurance_server_python/url_config.py`

This file centralizes all CTA (Call-to-Action) URL configuration. Simply edit the values at the top of the file.

## 🔧 Current Configuration

Open `insurance_server_python/url_config.py` and you'll see:

```python
# ============================================================================
# CONFIGURATION - Edit these values as needed
# ============================================================================

# Base URL where users will be redirected to complete their quote
# Change this to switch between test and production
CTA_BASE_URL = "https://tst.aisinsurance.com"

# Query parameters that will be appended to the URL
# These are used for tracking and attribution
CTA_PARAMS = {
    "sid": "chatgptapp",
    "refid3": "mercuryais",
}
```

### Generated URL Format

The widget generates URLs in this format:
```
https://tst.aisinsurance.com?sid=chatgptapp&refid3=mercuryais&zip=90210
```

Where:
- `sid` - Source identifier (default: "chatgptapp")
- `refid3` - Reference ID (default: "mercuryais")
- `zip` - User's ZIP code (dynamically inserted)

## 📝 Updating the Configuration

### Change to Production

Edit `insurance_server_python/url_config.py`:

```python
CTA_BASE_URL = "https://aisinsurance.com"  # Changed from tst.aisinsurance.com
```

Then restart the server.

### Change Tracking Parameters

Edit `insurance_server_python/url_config.py`:

```python
CTA_PARAMS = {
    "sid": "myapp",        # Changed
    "refid3": "mypartner", # Changed
}
```

Then restart the server.

### Change Everything

Edit `insurance_server_python/url_config.py`:

```python
CTA_BASE_URL = "https://custom.aisinsurance.com"

CTA_PARAMS = {
    "sid": "customapp",
    "refid3": "customref",
    "source": "widget",  # Add new parameters if needed
}
```

Then restart the server.

## 🧪 Testing the Configuration

### 1. Check Current Configuration

Start the Python interpreter:

```bash
cd insurance_server_python
python
```

Then:

```python
from url_config import get_cta_url, get_cta_params_json

# Generate a URL
url = get_cta_url("90210")
print(url)
# Output: https://tst.aisinsurance.com?sid=chatgptapp&refid3=mercuryais&zip=90210

# Get current config
import json
config = get_cta_params_json()
print(json.dumps(config, indent=2))
# Output:
# {
#   "base_url": "https://tst.aisinsurance.com",
#   "params": {
#     "sid": "chatgptapp",
#     "refid3": "mercuryais"
#   }
# }
```

### 2. Test in Widget

Start the server and trigger a quote. Check the browser console:

```javascript
// In browser console after quote is generated
console.log(window.openai.toolOutput.cta_config);
// Shows: { base_url: "...", params: { sid: "...", refid3: "..." } }
```

### 3. Inspect Generated Link

Right-click the "Get personalized quote" button → Inspect Element

The href should show:
```html
<a href="https://tst.aisinsurance.com?sid=chatgptapp&refid3=mercuryais&zip=90210" ...>
```

## 🔍 How It Works

### 1. Server Side (tool_handlers.py)

When generating a quote, the server includes CTA configuration in structured_content:

```python
from .url_config import get_cta_params_json

structured_content = {
    "zip_code": "90210",
    "carriers": [...],
    "cta_config": get_cta_params_json(),  # Passes config to widget
}
```

### 2. Widget Side (quick_quote_results_widget.py)

The widget receives the configuration and builds the URL:

```javascript
function buildCtaUrl(zipCode, ctaConfig) {
  const config = ctaConfig || {};
  const baseUrl = config.base_url || "https://tst.aisinsurance.com";
  const sid = config.sid || "chatgptapp";
  const refid3 = config.refid3 || "mercuryais";

  return `${baseUrl}?sid=${sid}&refid3=${refid3}&zip=${zipCode}`;
}

// Update button
ctaButtonEl.href = buildCtaUrl(zipCode, data.cta_config);
```

## 🎯 Common Use Cases

### Switching to Production

Edit `url_config.py`:

```python
CTA_BASE_URL = "https://aisinsurance.com"  # Remove 'tst.'
```

Restart the server. URLs will now use:
```
https://aisinsurance.com?sid=chatgptapp&refid3=mercuryais&zip=90210
```

### Using a Different Tracking ID

Edit `url_config.py`:

```python
CTA_PARAMS = {
    "sid": "chatgptapp",
    "refid3": "newpartner",  # Changed
}
```

Restart the server. URLs will now include:
```
https://tst.aisinsurance.com?sid=chatgptapp&refid3=newpartner&zip=90210
```

### Adding Additional Parameters

Edit `url_config.py` to add more parameters:

```python
CTA_PARAMS = {
    "sid": "chatgptapp",
    "refid3": "mercuryais",
    "source": "widget",  # New parameter
    "version": "v2",     # New parameter
}
```

Restart the server. URLs will now include:
```
https://tst.aisinsurance.com?sid=chatgptapp&refid3=mercuryais&source=widget&version=v2&zip=90210
```

## 🚨 Important Notes

1. **ZIP code is always dynamic** - It's extracted from the user's input and appended at runtime
2. **Restart required** - Changes to `url_config.py` require server restart
3. **Widget updates** - The widget will automatically use the new configuration
4. **Fallback values** - If config is missing, widget uses hardcoded defaults
5. **URL encoding** - Parameters are not URL-encoded (add encoding if special characters needed)

## 🔗 Related Files

- `insurance_server_python/url_config.py` - Main configuration file (edit this!)
- `insurance_server_python/tool_handlers.py` - Passes config to widget (line ~493, ~263, ~673)
- `insurance_server_python/quick_quote_results_widget.py` - Uses config to build URLs (line ~594, ~687)

## 💡 Tips

1. **Always restart after changes:**
   ```bash
   # Stop server (Ctrl+C)
   # Then restart
   uvicorn insurance_server_python.main:app --port 8000
   ```

2. **Verify configuration on startup:**
   Add this to `main.py` if you want to see the URL on startup:
   ```python
   from .url_config import get_cta_url
   logger.info(f"CTA URL example: {get_cta_url('90210')}")
   ```

3. **Check browser console for debugging:**
   The widget logs the CTA config when hydrating:
   ```
   Quick quote widget: Received data: {...}
   ```

4. **Keep a backup:**
   Before making changes, copy the original values:
   ```python
   # Original values
   # CTA_BASE_URL = "https://tst.aisinsurance.com"
   # CTA_PARAMS = {"sid": "chatgptapp", "refid3": "mercuryais"}

   # Your new values
   CTA_BASE_URL = "https://aisinsurance.com"
   CTA_PARAMS = {"sid": "myapp", "refid3": "myref"}
   ```
