# Widget Hosting via Assets Directory

## Summary

Widgets are now hosted as static HTML files in the `assets/images/` directory alongside your logos and images. This provides a simple, single-domain hosting solution that's ready for ChatGPT App Store submission.

## Implementation

### 1. Widget HTML Files Location

```
insurance_server_python/assets/images/
├── quick-quote-results.html      (252 KB)
├── phone-only.html               (191 KB)
├── insurance-state.html          (104 KB)
├── mercury-logo.png
├── progressive.png
├── orion.png
├── car-background.png
├── phone-background.png
└── powered-by.png
```

### 2. Widget URLs

All widgets are now accessible at:

```
https://stg-api.mercuryinsurance.com/assets/images/quick-quote-results.html
https://stg-api.mercuryinsurance.com/assets/images/phone-only.html
https://stg-api.mercuryinsurance.com/assets/images/insurance-state.html
```

### 3. Updated Files

**`insurance_server_python/widget_registry.py`**
- Updated all widget template URIs to point to assets/images URLs

**`insurance_server_python/main.py`**
- Enhanced `/assets/images/{filename}` route to detect HTML files
- Serves HTML with CSP headers for ChatGPT compatibility
- Serves images with CORS headers as before

## How It Works

### Request Flow

1. User requests a quote in ChatGPT
2. Your MCP server returns metadata with `template_uri`:
   ```
   https://stg-api.mercuryinsurance.com/assets/images/quick-quote-results.html
   ```
3. ChatGPT fetches the widget from your staging domain
4. The `/assets/images/{filename}` route detects it's an HTML file
5. Serves it with CSP headers and proper CORS configuration
6. Widget loads in sandboxed iframe and hydrates with data

### CSP Headers Applied to HTML Files

```
Content-Security-Policy:
  default-src 'none';
  script-src 'self' 'unsafe-inline';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data:;
  font-src 'self';
  connect-src 'self' https://stg-api.mercuryinsurance.com https://api.mercuryinsurance.com;
  frame-ancestors https://chatgpt.com https://chat.openai.com;

Access-Control-Allow-Origin: https://chatgpt.com
X-Content-Type-Options: nosniff
Cache-Control: public, max-age=3600
```

## Testing

### 1. Local Testing

Start your server:
```bash
uvicorn insurance_server_python.main:app --port 8000
```

Test widget endpoint:
```bash
curl -I http://localhost:8000/assets/images/quick-quote-results.html
```

Should return:
```
HTTP/1.1 200 OK
content-security-policy: default-src 'none'; script-src...
access-control-allow-origin: https://chatgpt.com
x-content-type-options: nosniff
cache-control: public, max-age=3600
content-type: text/html; charset=utf-8
```

View widget in browser:
```
http://localhost:8000/assets/images/quick-quote-results.html
```

### 2. Test Image Serving Still Works

Images should still load with CORS headers:
```bash
curl -I http://localhost:8000/assets/images/mercury-logo.png
```

Should return:
```
HTTP/1.1 200 OK
access-control-allow-origin: *
content-type: image/png
```

### 3. ChatGPT Integration

Once deployed to staging:
1. Configure ChatGPT with your MCP endpoint
2. Request a quote
3. Widget should load from `https://stg-api.mercuryinsurance.com/assets/images/quick-quote-results.html`
4. Verify in browser DevTools → Network tab

## ChatGPT App Store Configuration

When submitting to the App Store, use these settings:

**Widget Domain:**
```
https://stg-api.mercuryinsurance.com/assets/images
```

**Widget CSP:**
```
default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://stg-api.mercuryinsurance.com https://api.mercuryinsurance.com; frame-ancestors https://chatgpt.com https://chat.openai.com;
```

## For Production Deployment

When switching to production:

### 1. Update Widget URLs

In `widget_registry.py`:
```python
QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI = "https://api.mercuryinsurance.com/assets/images/quick-quote-results.html"
PHONE_ONLY_WIDGET_TEMPLATE_URI = "https://api.mercuryinsurance.com/assets/images/phone-only.html"
INSURANCE_STATE_WIDGET_TEMPLATE_URI = "https://api.mercuryinsurance.com/assets/images/insurance-state.html"
```

### 2. Update CSP Headers

In `main.py`, update `connect-src` to production only:
```python
"connect-src 'self' https://api.mercuryinsurance.com;"
```

### 3. Update App Store Settings

**Widget Domain:**
```
https://api.mercuryinsurance.com/assets/images
```

**Widget CSP:**
```
default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://api.mercuryinsurance.com; frame-ancestors https://chatgpt.com https://chat.openai.com;
```

## Regenerating Widget HTML Files

If you update widget code in the Python modules, regenerate the static files:

```bash
python -c "
import sys
sys.path.insert(0, '.')

from insurance_server_python.quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML
from insurance_server_python.phone_only_widget import PHONE_ONLY_WIDGET_HTML
from insurance_server_python.insurance_state_widget import INSURANCE_STATE_WIDGET_HTML

# Write quick quote widget
with open('insurance_server_python/assets/images/quick-quote-results.html', 'w', encoding='utf-8') as f:
    f.write(QUICK_QUOTE_RESULTS_WIDGET_HTML)
print('✓ Updated quick-quote-results.html')

# Write phone-only widget
with open('insurance_server_python/assets/images/phone-only.html', 'w', encoding='utf-8') as f:
    f.write(PHONE_ONLY_WIDGET_HTML)
print('✓ Updated phone-only.html')

# Write insurance state widget
with open('insurance_server_python/assets/images/insurance-state.html', 'w', encoding='utf-8') as f:
    f.write(INSURANCE_STATE_WIDGET_HTML)
print('✓ Updated insurance-state.html')
"
```

Or create a helper script: `scripts/update_widget_assets.py`

## Benefits of This Approach

1. **Single Domain:** All assets (images + widgets) served from same domain
2. **Simple Deployment:** Just commit the HTML files to git
3. **No Build Step:** HTML files are ready to serve
4. **Consistent Path:** Widgets alongside images they reference
5. **Easy Testing:** Can test widgets directly in browser
6. **CSP Ready:** Security headers automatically applied
7. **No External CDN:** Everything on your infrastructure

## Troubleshooting

### Widget Not Loading

**Check file exists:**
```bash
ls -lh insurance_server_python/assets/images/quick-quote-results.html
```

**Check CSP headers:**
```bash
curl -I http://localhost:8000/assets/images/quick-quote-results.html | grep -i "content-security-policy"
```

**Check widget URL in logs:**
When you call the tool, check server logs for:
```
template_uri: https://stg-api.mercuryinsurance.com/assets/images/quick-quote-results.html
```

### Images in Widget Not Loading

All images should be base64-embedded in the HTML. Check that:
```bash
grep -c "data:image" insurance_server_python/assets/images/quick-quote-results.html
```

Should show several matches.

### CSP Errors

If you see console errors like "Refused to load...":
- Verify `frame-ancestors` includes `https://chatgpt.com`
- Check that `script-src` includes `'unsafe-inline'`
- Ensure `img-src` includes `data:` for base64 images

## Files Modified

1. `insurance_server_python/main.py` - Updated assets route for HTML + CSP
2. `insurance_server_python/widget_registry.py` - Updated widget URIs to assets URLs
3. `insurance_server_python/assets/images/*.html` - Added widget HTML files

## Next Steps

1. ✅ Widget HTML extracted to assets/images/
2. ✅ Route updated to serve HTML with CSP headers
3. ✅ Widget URLs updated in registry
4. ⏳ Deploy to staging and test in ChatGPT
5. ⏳ Verify widget loads from hosted URL
6. ⏳ Switch to production domain when ready
