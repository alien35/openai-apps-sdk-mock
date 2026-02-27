# ChatGPT App Store Configuration

## Required Settings for Widget Support

When you configure your app in the ChatGPT App Store, you need to add these two settings to enable widget rendering:

### 1. Widget Domain

**Setting Name:** `widgetDomain`

**Value to Enter:**
```
https://stg-api.mercuryinsurance.com/assets/images
```

**What it does:**
- Tells ChatGPT where your widget HTML files are hosted
- ChatGPT will only load widgets from this domain
- Must be a fully qualified HTTPS URL
- Should NOT include a trailing slash
- Should NOT include the filename (just the directory path)

**For Production:** Change to `https://api.mercuryinsurance.com/assets/images`

---

### 2. Widget Content Security Policy (CSP)

**Setting Name:** `widgetCSP`

**Value to Enter:**
```
default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://stg-api.mercuryinsurance.com https://api.mercuryinsurance.com; frame-ancestors https://chatgpt.com https://chat.openai.com;
```

**What it does:**
- Defines security policy for loading widget content
- Restricts what the widget can do (scripts, styles, API calls)
- Required for app submission
- Must match what your server sends in CSP headers

**For Production:** Update to:
```
default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://api.mercuryinsurance.com; frame-ancestors https://chatgpt.com https://chat.openai.com;
```
(Note: Only includes production domain in `connect-src`)

---

## How to Configure in ChatGPT

### If Using API Configuration

If you're configuring your app via API, add these to your app manifest:

```json
{
  "name": "Mercury Insurance Quote Tool",
  "description": "Get personalized auto insurance quotes",
  "widgetDomain": "https://stg-api.mercuryinsurance.com/assets/images",
  "widgetCSP": "default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://stg-api.mercuryinsurance.com https://api.mercuryinsurance.com; frame-ancestors https://chatgpt.com https://chat.openai.com;",
  "mcp": {
    "endpoint": "https://stg-api.mercuryinsurance.com/api/ai-quote-tools/v1/mcp"
  }
}
```

### If Using Web Interface

If you're using the ChatGPT developer dashboard:

1. Go to your app settings
2. Find the "Widget Configuration" section
3. Add these two fields:
   - **Widget Domain:** `https://stg-api.mercuryinsurance.com/assets/images`
   - **Widget CSP:** (paste the CSP string above)
4. Save changes
5. Test your app

---

## Verification

After configuring, verify the settings are correct:

### 1. Check Widget URL Resolution

ChatGPT should resolve widget URLs like this:

**Your tool returns:**
```python
"openai.com/widget": {
    "type": "resource",
    "resource": {
        "uri": "https://stg-api.mercuryinsurance.com/assets/images/quick-quote-results.html"
    }
}
```

**ChatGPT validates:**
- Does the URI start with the configured `widgetDomain`? ✅
- Is the domain HTTPS? ✅
- Does the CSP allow loading from this domain? ✅

### 2. Test Widget Loading

After configuration:
1. Request a quote in ChatGPT
2. Open browser DevTools (F12)
3. Go to Network tab
4. Look for request to `quick-quote-results.html`
5. Check Response Headers include CSP

**Expected Response Headers:**
```
content-security-policy: default-src 'none'; script-src...
access-control-allow-origin: https://chatgpt.com
x-content-type-options: nosniff
```

### 3. Check Console for Errors

If you see CSP errors in console:
- ❌ `Refused to load...` - CSP is too restrictive
- ❌ `frame-ancestors` - Widget domain not allowed
- ✅ No CSP errors - Configuration is correct

---

## Common Configuration Issues

### Issue: "Widget domain is not set"
**Cause:** `widgetDomain` field is missing or empty
**Fix:** Add `widgetDomain: https://stg-api.mercuryinsurance.com/assets/images`

### Issue: "Widget CSP is not set"
**Cause:** `widgetCSP` field is missing or empty
**Fix:** Add the full CSP string (see above)

### Issue: Widget won't load (CORS error)
**Cause:** Widget domain doesn't match configured domain
**Fix:** Ensure widget URLs in `widget_registry.py` match `widgetDomain`

### Issue: Widget loads but is blank/broken
**Cause:** CSP is blocking resources
**Fix:** Check browser console for CSP violations and adjust CSP accordingly

### Issue: "Refused to frame"
**Cause:** `frame-ancestors` not set correctly
**Fix:** Ensure CSP includes `frame-ancestors https://chatgpt.com https://chat.openai.com;`

---

## CSP Policy Explained

Breaking down the CSP string:

| Directive | Value | Why |
|-----------|-------|-----|
| `default-src 'none'` | Block everything by default | Security best practice |
| `script-src 'self' 'unsafe-inline'` | Allow inline scripts in widget | Widget JS needs to run |
| `style-src 'self' 'unsafe-inline'` | Allow inline styles | Widget CSS needs to apply |
| `img-src 'self' data:` | Allow data URIs for images | Images are base64-embedded |
| `font-src 'self'` | Allow fonts from same origin | If widget uses custom fonts |
| `connect-src 'self' https://stg-api...` | Allow API calls to your domains | Widget fetches data from API |
| `frame-ancestors https://chatgpt.com...` | Only allow embedding in ChatGPT | Prevent unauthorized embedding |

---

## Testing Checklist

Before submitting to App Store:

- [ ] `widgetDomain` configured in app settings
- [ ] `widgetCSP` configured in app settings
- [ ] Widget URLs in code match `widgetDomain`
- [ ] CSP headers on server match `widgetCSP` config
- [ ] Widget loads successfully in ChatGPT
- [ ] No CSP errors in browser console
- [ ] Widget hydrates with data correctly
- [ ] Images display (base64-embedded)
- [ ] CTA button works
- [ ] Phone-only state widget works

---

## Production Deployment

When switching to production:

### 1. Update Widget Domain
```
https://api.mercuryinsurance.com/assets/images
```

### 2. Update Widget CSP
```
default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://api.mercuryinsurance.com; frame-ancestors https://chatgpt.com https://chat.openai.com;
```

### 3. Update Code
In `widget_registry.py`:
```python
QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI = "https://api.mercuryinsurance.com/assets/images/quick-quote-results.html"
```

In `main.py`:
```python
"connect-src 'self' https://api.mercuryinsurance.com;"  # Remove staging domain
```

### 4. Redeploy
- Deploy code changes
- Update app configuration in ChatGPT
- Test thoroughly before making app public

---

## Need Help?

If widgets still aren't loading after configuration:

1. Check server logs for widget requests
2. Check browser DevTools → Network tab for 404s
3. Check Console for CSP violations
4. Verify `widgetDomain` matches exactly (no trailing slash)
5. Verify CSP string has no line breaks or extra spaces
6. Test widget URL directly in browser

If you see the widget HTML but it's not rendering:
- Check that `window.openai.toolOutput` is set
- Check hydration function runs
- Check console for JavaScript errors
- Verify structured content format matches widget expectations
