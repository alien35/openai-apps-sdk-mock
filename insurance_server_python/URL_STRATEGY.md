# URL Strategy - Dynamic Configuration

## Current Setup

### 1. Widget URLs (template_uri)
**Location:** `widget_registry.py`

**Current (Hardcoded):**
```python
QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI = "ui://widget/quick-quote-results.html"
PHONE_ONLY_WIDGET_TEMPLATE_URI = "ui://widget/phone-only.html"
```

These are **local references** - not actual URLs. The widget HTML is embedded in the response.

### 2. API Base URL (server_url in structured_content)
**Location:** `tool_handlers.py`

**Current (Environment Variable):**
```python
server_base_url = os.getenv("SERVER_BASE_URL", "http://localhost:8000")
```

This IS dynamic! Controlled by `.env` file or environment variable.

### 3. CTA URLs (Get personalized quote button)
**Location:** `url_config.py`

**Current (Hardcoded but Configurable):**
```python
CTA_BASE_URL = "https://tst.aisinsurance.com"
CTA_PARAMS = {
    "sid": "chatgptapp",
    "refid3": "mercuryais",
}
```

This is hardcoded in the file but easy to change.

## Strategy for Staging vs Production

### Recommended Approach: Environment Variables

Make widget URLs dynamic so you can switch between staging and production:

**1. Add WIDGET_BASE_URL to your environment:**

In `.env`:
```bash
# Staging
WIDGET_BASE_URL=https://stg-api.mercuryinsurance.com/widgets

# Production (when ready)
# WIDGET_BASE_URL=https://widgets.mercuryinsurance.com
```

**2. Update widget_registry.py to use it:**

```python
import os

# Get widget base URL from environment
WIDGET_BASE_URL = os.getenv(
    "WIDGET_BASE_URL",
    "https://stg-api.mercuryinsurance.com/widgets"  # Default to staging
)

# Build template URIs dynamically
INSURANCE_STATE_WIDGET_TEMPLATE_URI = f"{WIDGET_BASE_URL}/insurance-state.html"
QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI = f"{WIDGET_BASE_URL}/quick-quote-results.html"
PHONE_ONLY_WIDGET_TEMPLATE_URI = f"{WIDGET_BASE_URL}/phone-only.html"
```

Now you can switch environments by changing `.env`!

### Alternative: Configuration File

If you prefer a config file approach:

**1. Create `config.py`:**
```python
import os

class Config:
    # Environment: 'staging' or 'production'
    ENVIRONMENT = os.getenv("ENVIRONMENT", "staging")

    # URL configurations
    URLS = {
        "staging": {
            "api": "https://stg-api.mercuryinsurance.com",
            "widgets": "https://stg-api.mercuryinsurance.com/widgets",
            "cta": "https://tst.aisinsurance.com",
        },
        "production": {
            "api": "https://api.mercuryinsurance.com",
            "widgets": "https://widgets.mercuryinsurance.com",
            "cta": "https://aisinsurance.com",
        }
    }

    @classmethod
    def get_widget_base_url(cls):
        return cls.URLS[cls.ENVIRONMENT]["widgets"]

    @classmethod
    def get_api_base_url(cls):
        return cls.URLS[cls.ENVIRONMENT]["api"]

    @classmethod
    def get_cta_base_url(cls):
        return cls.URLS[cls.ENVIRONMENT]["cta"]
```

**2. Use in widget_registry.py:**
```python
from .config import Config

WIDGET_BASE_URL = Config.get_widget_base_url()
QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI = f"{WIDGET_BASE_URL}/quick-quote-results.html"
```

**3. Switch environments:**
```bash
ENVIRONMENT=production uvicorn insurance_server_python.main:app --port 8000
```

## Quick Implementation (Simplest)

If you just want to prove it works with staging, here's the quickest change:

**Edit `widget_registry.py` directly:**

Change:
```python
QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI = "ui://widget/quick-quote-results.html"
```

To:
```python
QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI = "https://stg-api.mercuryinsurance.com/api/ai-quote-tools/widgets/quick-quote-results.html"
```

Then add the static file serving route to `main.py` (see below).

## Serving Widgets from Your API

Add these routes to `insurance_server_python/main.py`:

```python
@app.route("/api/ai-quote-tools/widgets/quick-quote-results.html", methods=["GET"])
async def serve_quick_quote_widget(request: Request):
    """Serve quick quote widget with CSP headers."""
    from .quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML
    from starlette.responses import HTMLResponse

    return HTMLResponse(
        QUICK_QUOTE_RESULTS_WIDGET_HTML,
        headers={
            "Content-Security-Policy": (
                "default-src 'none'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self' https://stg-api.mercuryinsurance.com https://api.mercuryinsurance.com; "
                "frame-ancestors https://chatgpt.com https://chat.openai.com;"
            ),
            "Access-Control-Allow-Origin": "https://chatgpt.com",
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "public, max-age=3600",
        }
    )


@app.route("/api/ai-quote-tools/widgets/phone-only.html", methods=["GET"])
async def serve_phone_only_widget(request: Request):
    """Serve phone-only widget with CSP headers."""
    from .phone_only_widget import PHONE_ONLY_WIDGET_HTML
    from starlette.responses import HTMLResponse

    return HTMLResponse(
        PHONE_ONLY_WIDGET_HTML,
        headers={
            "Content-Security-Policy": (
                "default-src 'none'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self' https://stg-api.mercuryinsurance.com https://api.mercuryinsurance.com; "
                "frame-ancestors https://chatgpt.com https://chat.openai.com;"
            ),
            "Access-Control-Allow-Origin": "https://chatgpt.com",
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "public, max-age=3600",
        }
    )
```

## Summary

**What's currently dynamic:**
- ✅ API base URL (`SERVER_BASE_URL` from environment)
- ❌ Widget URLs (hardcoded as `ui://widget/...`)
- ❌ CTA URLs (hardcoded in `url_config.py`)

**What you should make dynamic:**
- Widget URLs - Use environment variable or config file
- Optionally: CTA URLs if you need staging/prod switching

**Recommended for staging proof:**
1. Add static file serving routes to your API (code above)
2. Update template URIs to point to your staging URL
3. Test in ChatGPT
4. When ready for prod, just change the URLs

**Recommended for production:**
1. Use environment variables for all URLs
2. Have separate `.env.staging` and `.env.production` files
3. Deploy widgets to proper hosting (Cloudflare Pages, etc.)
4. Switch environment via `ENVIRONMENT=production` variable
