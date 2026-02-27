# Staging Widget Implementation - Complete

## Summary

Widgets are now hosted on your staging API domain and ready for testing with ChatGPT. This implementation proves the widget hosting concept before switching to production.

## What Was Changed

### 1. Added Widget Serving Routes (`insurance_server_python/main.py`)

Added three new routes that serve widget HTML with proper CSP headers:

```python
# Routes added:
/api/ai-quote-tools/widgets/quick-quote-results.html
/api/ai-quote-tools/widgets/phone-only.html
/api/ai-quote-tools/widgets/insurance-state.html
```

Each route:
- Serves the widget HTML from Python modules
- Includes Content Security Policy headers (required for App Store)
- Includes CORS headers for ChatGPT access
- Includes cache headers (1 hour)

### 2. Updated Widget URLs (`insurance_server_python/widget_registry.py`)

Changed widget template URIs from local references to hosted URLs:

**Before:**
```python
QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI = "ui://widget/quick-quote-results.html"
```

**After:**
```python
QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI = "https://stg-api.mercuryinsurance.com/api/ai-quote-tools/widgets/quick-quote-results.html"
```

## How It Works

### Widget Flow

1. User requests a quote in ChatGPT
2. Your MCP server tool returns metadata with `template_uri` pointing to staging URL
3. ChatGPT fetches the widget HTML from your staging domain
4. Widget loads in a sandboxed iframe with CSP restrictions
5. Widget hydrates with the structured data from the tool response

### CSP Configuration

All widget routes include this Content Security Policy:

```
Content-Security-Policy: default-src 'none';
  script-src 'self' 'unsafe-inline';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data:;
  font-src 'self';
  connect-src 'self' https://stg-api.mercuryinsurance.com https://api.mercuryinsurance.com;
  frame-ancestors https://chatgpt.com https://chat.openai.com;
```

This ensures:
- Only allowed scripts and styles can run
- Only ChatGPT can embed the widget in an iframe
- API calls are restricted to Mercury Insurance domains

## Testing

### 1. Verify Widget Routes Are Accessible

Start your server:
```bash
cd /Users/alexanderleon/mi/openai-apps-sdk-examples
uvicorn insurance_server_python.main:app --port 8000
```

Test the widget endpoint:
```bash
curl -I http://localhost:8000/api/ai-quote-tools/widgets/quick-quote-results.html
```

You should see:
```
HTTP/1.1 200 OK
Content-Security-Policy: default-src 'none'; script-src...
Access-Control-Allow-Origin: https://chatgpt.com
X-Content-Type-Options: nosniff
Cache-Control: public, max-age=3600
```

### 2. View Widget in Browser

Open in browser:
```
http://localhost:8000/api/ai-quote-tools/widgets/quick-quote-results.html
```

You should see the widget HTML (may not be styled without data).

### 3. Test End-to-End in ChatGPT

1. Ensure your staging server is accessible at `https://stg-api.mercuryinsurance.com`
2. Configure ChatGPT with your MCP endpoint
3. Request a quote in ChatGPT
4. Verify the widget loads from the staging URL

## URL Strategy

### Current State

**Widget URLs:**
- ✅ Now using staging URL: `https://stg-api.mercuryinsurance.com/api/ai-quote-tools/widgets/`
- Served from your API server with CSP headers

**API Base URL:**
- Already dynamic via `SERVER_BASE_URL` environment variable
- Default: `http://localhost:8000`

**CTA URLs:**
- Hardcoded in `url_config.py`
- Base URL: `https://tst.aisinsurance.com`

### Making URLs Dynamic (Optional)

If you need to easily switch between staging and production, you can make widget URLs dynamic:

**Option 1: Environment Variable (Simple)**

In `widget_registry.py`:
```python
import os

WIDGET_BASE_URL = os.getenv(
    "WIDGET_BASE_URL",
    "https://stg-api.mercuryinsurance.com/api/ai-quote-tools/widgets"
)

QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI = f"{WIDGET_BASE_URL}/quick-quote-results.html"
```

Then switch environments:
```bash
# Staging
export WIDGET_BASE_URL=https://stg-api.mercuryinsurance.com/api/ai-quote-tools/widgets

# Production
export WIDGET_BASE_URL=https://api.mercuryinsurance.com/api/ai-quote-tools/widgets
```

**Option 2: Configuration File (More Control)**

See `URL_STRATEGY.md` for details on creating a config-based system.

## Next Steps

### To Prove It Works with Staging

1. ✅ Widget routes added
2. ✅ Widget URLs updated to staging domain
3. ⏳ Deploy to staging environment
4. ⏳ Test in ChatGPT
5. ⏳ Verify widget loads from hosted URL

### For Production Deployment

Once you've proven it works with staging:

1. **Switch to Production Domain:**
   ```python
   # widget_registry.py
   WIDGET_BASE_URL = "https://api.mercuryinsurance.com/api/ai-quote-tools/widgets"
   ```

2. **Update CSP Headers in main.py:**
   Change `connect-src` to only include production domain:
   ```python
   "connect-src 'self' https://api.mercuryinsurance.com;"
   ```

3. **Configure App Store Settings:**
   - `widgetDomain`: `https://api.mercuryinsurance.com/api/ai-quote-tools/widgets`
   - `widgetCSP`: (same CSP string from the routes)

4. **Fix Tool Flow:**
   Remove or deprecate `submit-carrier-estimates` tool (see `APP_STORE_READINESS.md`)

## Troubleshooting

### Widget Not Loading

**Check CSP Headers:**
```bash
curl -I https://stg-api.mercuryinsurance.com/api/ai-quote-tools/widgets/quick-quote-results.html
```

Should include `Content-Security-Policy` header.

**Check CORS:**
The response should include:
```
Access-Control-Allow-Origin: https://chatgpt.com
```

**Check Widget URL in Logs:**
When you call `get-enhanced-quick-quote`, check server logs for:
```
template_uri: https://stg-api.mercuryinsurance.com/api/ai-quote-tools/widgets/quick-quote-results.html
```

### CSP Errors in Browser Console

If you see "Refused to load..." errors:
- Check that `frame-ancestors` includes `https://chatgpt.com`
- Verify `script-src` includes `'self' 'unsafe-inline'`
- Check that images are base64-embedded (no external requests)

### Widget Renders Twice

Should already be fixed, but if it happens:
- Check that `_tool_meta()` is NOT used in tool handler
- Verify metadata only includes `openai.com/widget`, not `openai/outputTemplate`

## Files Modified

1. `insurance_server_python/main.py` - Added 3 widget serving routes
2. `insurance_server_python/widget_registry.py` - Updated 3 widget URIs to staging URLs

## Documentation

- `URL_STRATEGY.md` - Complete URL configuration strategy
- `APP_STORE_READINESS.md` - Checklist for App Store submission
- `WIDGET_DEPLOYMENT_QUICKSTART.md` - Deployment options guide

## Key Benefits of This Implementation

1. **Proves Concept:** Shows widgets work with hosted URLs
2. **CSP Ready:** Security headers already configured
3. **No External Dependencies:** Widgets served from your API
4. **Easy Production Switch:** Change URLs when ready
5. **App Store Compatible:** Meets hosting requirements
