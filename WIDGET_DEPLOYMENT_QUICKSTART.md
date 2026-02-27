# Widget Deployment - Quick Start Guide

**Goal:** Host your insurance quote widget to meet ChatGPT App Store requirements.

## 🚀 Quick Deploy (5 Minutes)

### Option A: Cloudflare Pages (Recommended)

**1. Extract widgets:**
```bash
python scripts/extract_widget.py
```

This creates: `widgets-deploy/` with:
- `quick-quote-results.html`
- `phone-only.html`
- `_headers` (CSP configuration)
- `README.md`

**2. Deploy to Cloudflare Pages:**
```bash
cd widgets-deploy
npx wrangler pages deploy . --project-name mercury-insurance-widgets
```

**3. Note the URL:**
```
https://mercury-insurance-widgets.pages.dev
```

**4. Update your code:**
```bash
python scripts/update_widget_urls.py https://mercury-insurance-widgets.pages.dev
```

**5. Test:**
```bash
uvicorn insurance_server_python.main:app --port 8000
```

Generate a quote in ChatGPT - widget should load from the hosted URL!

### Option B: Using Your API Domain

If you want to serve widgets from your existing API:

**1. Add static file serving to your API:**

In `main.py`:
```python
from starlette.responses import FileResponse, HTMLResponse

@app.route("/widgets/quick-quote-results.html", methods=["GET"])
async def serve_quick_quote_widget(request: Request):
    """Serve quick quote widget with CSP headers."""
    from .quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML

    return HTMLResponse(
        QUICK_QUOTE_RESULTS_WIDGET_HTML,
        headers={
            "Content-Security-Policy": "default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://api.mercuryinsurance.com; frame-ancestors https://chatgpt.com https://chat.openai.com;",
            "Access-Control-Allow-Origin": "https://chatgpt.com",
            "X-Content-Type-Options": "nosniff",
        }
    )
```

**2. Update widget URLs:**
```bash
python scripts/update_widget_urls.py https://api.mercuryinsurance.com/widgets
```

**3. Test:**
```bash
curl -I https://api.mercuryinsurance.com/widgets/quick-quote-results.html
```

Should show CSP headers.

## 📋 App Store Configuration

After deployment, when submitting to ChatGPT App Store, configure:

```json
{
  "widgetDomain": "https://YOUR-DEPLOYED-URL",
  "widgetCSP": "default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://api.mercuryinsurance.com; frame-ancestors https://chatgpt.com https://chat.openai.com;"
}
```

Replace `YOUR-DEPLOYED-URL` with:
- `https://mercury-insurance-widgets.pages.dev` (Cloudflare)
- `https://widgets.mercuryinsurance.com` (Custom domain)
- `https://api.mercuryinsurance.com/widgets` (Same domain)

## ⚠️ Important: Production Domain

For App Store submission, **do not use** staging domains:
- ❌ `stg-api.mercuryinsurance.com`
- ❌ `staging.mercuryinsurance.com`
- ❌ `test.mercuryinsurance.com`

Use production URLs only:
- ✅ `api.mercuryinsurance.com`
- ✅ `widgets.mercuryinsurance.com`
- ✅ `prod-api.mercuryinsurance.com`

## 🔧 Tool Flow Fix

The `submit-carrier-estimates` tool is **not needed** because `get-enhanced-quick-quote` already:
- Generates all carrier estimates
- Returns the complete widget
- No further action required

**To fix the contradiction:**

Option 1: Remove `submit-carrier-estimates` tool entirely (recommended)

Option 2: Update its description:
```python
description="""
DEPRECATED: This tool is no longer needed.
Use get-enhanced-quick-quote instead, which generates the complete quote.
"""
```

## ✅ Verification Checklist

Before submitting to App Store:

- [ ] Widget loads from hosted URL (not inline)
- [ ] CSP headers present when accessing widget
- [ ] Widget renders correctly in ChatGPT
- [ ] `widgetDomain` configured
- [ ] `widgetCSP` configured
- [ ] Using production domain (not staging)
- [ ] Tool flow contradiction resolved
- [ ] Tested end-to-end quote generation

## 🐛 Troubleshooting

**Widget not loading:**
- Check CSP headers: `curl -I YOUR-WIDGET-URL`
- Check browser console for CSP violations
- Verify `template_uri` in widget_registry.py is correct

**CSP errors:**
- If you see "Refused to execute inline script", that's expected - your CSP is working
- Make sure `'unsafe-inline'` is in `script-src` and `style-src`

**CORS errors:**
- Add `Access-Control-Allow-Origin: https://chatgpt.com` header
- Check `frame-ancestors` in CSP includes ChatGPT domains

## 📚 Full Documentation

See `WIDGET_HOSTING_PLAN.md` for complete details on:
- Different hosting options
- Custom domain configuration
- AWS/Vercel deployment
- DNS setup
- Security considerations

## 💡 Need Help?

Common scenarios:

**"I want to use Cloudflare Pages with custom domain"**
1. Deploy to Pages (steps above)
2. In Pages dashboard: Custom Domains → Add `widgets.mercuryinsurance.com`
3. Update DNS as instructed
4. Run: `python scripts/update_widget_urls.py https://widgets.mercuryinsurance.com`

**"I want to use my existing API server"**
1. Follow Option B above
2. Add CSP headers to the route
3. Update widget URLs

**"I want to use Vercel"**
1. Extract widgets: `python scripts/extract_widget.py`
2. Deploy: `cd widgets-deploy && vercel --prod`
3. Update URLs: `python scripts/update_widget_urls.py https://your-vercel-url.vercel.app`

**"I need staging AND production"**
1. Deploy widgets to both environments
2. Use environment variables in widget_registry.py:
   ```python
   WIDGET_DOMAIN = os.getenv("WIDGET_DOMAIN", "https://widgets.mercuryinsurance.com")
   template_uri=f"{WIDGET_DOMAIN}/quick-quote-results.html"
   ```
3. For App Store submission, use production URLs only
