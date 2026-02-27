# Widget Hosting Plan for ChatGPT App Store Submission

This document outlines the complete plan to host the insurance quote widget and meet ChatGPT App Store requirements.

## 📋 Requirements Checklist

### ❌ Current Blockers
- [ ] Widget Domain not configured
- [ ] Content Security Policy (CSP) not set
- [ ] Tool flow contradiction (get-enhanced-quick-quote vs submit-carrier-estimates)
- [ ] Using staging domain (stg-api.mercuryinsurance.com)

### ✅ What's Already Correct
- [x] Proper structured multi-step collection
- [x] Explicit guardrails against premature tool calls
- [x] Widget rendering enabled
- [x] Duplicate prevention handled
- [x] Read-only hint set properly
- [x] All resources embedded as base64 (no external HTTP requests)

## 🎯 Recommended Architecture

### Option 1: Dedicated Widget Subdomain (Recommended for Production)

**Setup:**
```
API:    https://api.mercuryinsurance.com/ai-quote-tools/v1/mcp
Widget: https://widgets.mercuryinsurance.com/quick-quote-results.html
```

**Pros:**
- Clean separation of concerns
- Easier CSP management
- Professional appearance
- Matches OpenAI's best practices

**Cons:**
- Requires DNS configuration
- Need separate hosting/CDN setup

### Option 2: Same Domain, Different Path

**Setup:**
```
API:    https://api.mercuryinsurance.com/ai-quote-tools/v1/mcp
Widget: https://api.mercuryinsurance.com/widgets/quick-quote-results.html
```

**Pros:**
- Single domain to manage
- Can use same hosting infrastructure
- Simpler deployment

**Cons:**
- Need careful CSP configuration
- Less isolated

### Option 3: Static Hosting Service (Quick Start)

**Setup:**
```
API:    https://api.mercuryinsurance.com/ai-quote-tools/v1/mcp
Widget: https://mercury-insurance-widgets.pages.dev/quick-quote-results.html
        (Cloudflare Pages)
OR
Widget: https://mercury-insurance-widgets.vercel.app/quick-quote-results.html
        (Vercel)
```

**Pros:**
- Zero infrastructure management
- Free tier available
- Automatic HTTPS
- Built-in CDN
- Easy deployments

**Cons:**
- External domain (not mercuryinsurance.com)
- Subject to third-party terms

## 🚀 Recommended Approach: Option 1 (Dedicated Subdomain)

### Step 1: DNS Configuration

Create a CNAME record:
```
widgets.mercuryinsurance.com → your-cdn-or-hosting.com
```

OR create an A record pointing to your static file server.

### Step 2: Host the Widget Files

**File Structure:**
```
/
├── quick-quote-results.html      # The widget HTML
├── phone-only.html                # Phone-only state widget
└── (optional) shared-assets/      # If you extract common resources
```

**Hosting Options:**

**A. Cloudflare Pages (Recommended - Easy)**
1. Create a new Pages project
2. Upload the widget HTML files
3. Custom domain: `widgets.mercuryinsurance.com`
4. Configure CSP in `_headers` file

**B. AWS S3 + CloudFront**
1. Create S3 bucket
2. Upload widget files
3. Create CloudFront distribution
4. Point custom domain
5. Configure CSP in CloudFront response headers

**C. Your Existing API Server**
1. Add static file serving to your API
2. Serve from `/widgets/` path
3. Configure CSP headers in middleware
4. Ensure CORS headers allow ChatGPT origins

### Step 3: Configure Content Security Policy

**Minimal CSP for Your Widget:**

```
Content-Security-Policy:
  default-src 'none';
  script-src 'self' 'unsafe-inline';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data:;
  font-src 'self';
  connect-src 'self' https://api.mercuryinsurance.com;
  frame-ancestors https://chatgpt.com https://chat.openai.com;
```

**Explanation:**
- `default-src 'none'` - Block everything by default
- `script-src 'self' 'unsafe-inline'` - Allow inline scripts (widget needs this)
- `style-src 'self' 'unsafe-inline'` - Allow inline styles
- `img-src 'self' data:` - Allow base64 images (your logos)
- `connect-src` - Allow API calls to your server + self
- `frame-ancestors` - Allow embedding in ChatGPT

**Why `'unsafe-inline'` is needed:**
Your widget has inline JavaScript and CSS. This is acceptable for App Store submission as long as it's scoped properly.

**Production-Ready CSP (More Strict):**

If you want to remove `unsafe-inline`, you'd need to:
1. Extract all `<script>` tags to external files
2. Extract all `<style>` tags to external CSS
3. Use nonces or hashes

For your use case, the minimal CSP above is fine.

### Step 4: Update Widget Registry

**Current code (widget_registry.py):**
```python
WidgetDefinition(
    identifier="quick-quote-results",
    title="Quick Quote Results",
    template_uri="ui://widget/quick-quote-results.html",  # ❌ Local reference
    html=QUICK_QUOTE_RESULTS_WIDGET_HTML,
    # ...
)
```

**Update to:**
```python
WidgetDefinition(
    identifier="quick-quote-results",
    title="Quick Quote Results",
    template_uri="https://widgets.mercuryinsurance.com/quick-quote-results.html",  # ✅ Hosted URL
    html=QUICK_QUOTE_RESULTS_WIDGET_HTML,  # Still send embedded for now
    # ...
)
```

### Step 5: Configure Widget Domain in App Config

When you submit to ChatGPT App Store, you'll configure:

```json
{
  "widgetDomain": "https://widgets.mercuryinsurance.com",
  "widgetCSP": "default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://api.mercuryinsurance.com; frame-ancestors https://chatgpt.com https://chat.openai.com;"
}
```

### Step 6: Test the Setup

**Test URL access:**
```bash
curl -I https://widgets.mercuryinsurance.com/quick-quote-results.html
```

Should return:
- `200 OK`
- `Content-Type: text/html`
- `Content-Security-Policy: ...`

**Test in ChatGPT:**
1. Update your MCP endpoint to use the hosted URL
2. Trigger a quote
3. Verify widget loads from `widgets.mercuryinsurance.com`
4. Check browser console for CSP violations

## 🔧 Implementation: Cloudflare Pages (Quickest)

### Setup Steps (5 minutes)

1. **Install Wrangler CLI:**
   ```bash
   npm install -g wrangler
   ```

2. **Create project directory:**
   ```bash
   mkdir mercury-insurance-widgets
   cd mercury-insurance-widgets
   ```

3. **Copy widget files:**
   ```bash
   cp ../quick_quote_results_widget.py .

   # Extract the HTML to a file
   python -c "
   from quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML
   with open('quick-quote-results.html', 'w') as f:
       f.write(QUICK_QUOTE_RESULTS_WIDGET_HTML)
   "
   ```

4. **Create _headers file for CSP:**
   ```bash
   cat > _headers << 'EOF'
   /quick-quote-results.html
     Content-Security-Policy: default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://api.mercuryinsurance.com; frame-ancestors https://chatgpt.com https://chat.openai.com;
     Access-Control-Allow-Origin: https://chatgpt.com
     X-Content-Type-Options: nosniff
   EOF
   ```

5. **Deploy:**
   ```bash
   wrangler pages project create mercury-insurance-widgets
   wrangler pages deploy . --project-name mercury-insurance-widgets
   ```

6. **Configure custom domain:**
   - Go to Cloudflare Pages dashboard
   - Select your project
   - Custom Domains → Add `widgets.mercuryinsurance.com`
   - Update DNS as instructed

## 🐛 Fix: Tool Flow Contradiction

### Current Problem

**get-enhanced-quick-quote says:**
```
After calling this tool, show the tool's response and STOP.
```

**submit-carrier-estimates says:**
```
REQUIRED: CALL THIS TOOL IMMEDIATELY AFTER 'get-enhanced-quick-quote'
```

These contradict each other.

### Solution: Remove submit-carrier-estimates Tool

Looking at your code, `submit-carrier-estimates` appears to be unused. The `get-enhanced-quick-quote` tool already:
- ✅ Generates all carrier estimates
- ✅ Returns the complete widget
- ✅ No further action needed

**Action:** Remove or deprecate the `submit-carrier-estimates` tool entirely.

**If you need it for some workflow:**
Update the instructions to be clear:

**Option A: Sequential (Not Recommended)**
```
get-enhanced-quick-quote: Collect all data, then call this tool.
After response, ASK USER if they want to proceed, then call submit-carrier-estimates.
```

**Option B: Single Tool (Recommended)**
```
get-enhanced-quick-quote: This tool generates the complete quote and widget.
No additional tools needed.
```

## 📝 Deployment Checklist

### Pre-Deployment
- [ ] Choose hosting approach (Option 1, 2, or 3)
- [ ] Configure DNS (if using custom domain)
- [ ] Extract widget HTML to static files
- [ ] Create CSP headers file
- [ ] Test CSP with CSP Evaluator: https://csp-evaluator.withgoogle.com/

### Deployment
- [ ] Deploy widget files to hosting
- [ ] Verify HTTPS works
- [ ] Test widget loads directly in browser
- [ ] Check CSP headers are present

### Code Updates
- [ ] Update `template_uri` in widget_registry.py
- [ ] Update any hardcoded widget URLs
- [ ] Test with MCP Inspector
- [ ] Test in ChatGPT

### App Store Config
- [ ] Set `widgetDomain` to your hosted URL
- [ ] Set `widgetCSP` to your CSP policy
- [ ] Remove/fix tool flow contradiction
- [ ] Switch from staging to production domain
- [ ] Submit for review

## 🚨 Production Domain Requirement

**Critical:** Replace `stg-api.mercuryinsurance.com` with production URL:
- ✅ `api.mercuryinsurance.com`
- ✅ `prod-api.mercuryinsurance.com`
- ❌ `stg-api.mercuryinsurance.com` (will be rejected)

Staging/testing endpoints are not allowed for App Store submission.

## 💡 Quick Start Guide

If you want to test immediately:

1. **Deploy to Cloudflare Pages (Free):**
   ```bash
   # Extract widget
   python -c "from quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML; open('widget.html', 'w').write(QUICK_QUOTE_RESULTS_WIDGET_HTML)"

   # Deploy
   npx wrangler pages deploy . --project-name mercury-widgets
   ```

2. **Get the URL:**
   ```
   https://mercury-widgets.pages.dev/widget.html
   ```

3. **Update widget_registry.py:**
   ```python
   template_uri="https://mercury-widgets.pages.dev/widget.html"
   ```

4. **Test:**
   Request a quote in ChatGPT and verify it works.

5. **Add custom domain later** when ready for production.

## 📞 Next Steps

Reply with:
1. Which hosting approach you prefer (1, 2, or 3)
2. Do you have access to configure DNS for `widgets.mercuryinsurance.com`?
3. Are you ready to deploy, or do you need help with any specific step?

I can provide exact commands and code changes based on your choice.
