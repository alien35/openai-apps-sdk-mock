# ChatGPT App Store Readiness Summary

This document summarizes what needs to be done to submit your insurance quote app to the ChatGPT App Store.

## 🚨 Current Status: Not Ready for Submission

### ❌ Blocking Issues

1. **Widget Domain Not Configured**
   - **Issue:** Widgets are embedded inline, not hosted
   - **Required:** Host widgets on a public URL
   - **Fix:** See WIDGET_DEPLOYMENT_QUICKSTART.md

2. **CSP Not Configured**
   - **Issue:** No Content Security Policy headers
   - **Required:** CSP is mandatory for app submission
   - **Fix:** Included in deployment scripts (automatic)

3. **Tool Flow Contradiction**
   - **Issue:** `get-enhanced-quick-quote` says "STOP" but `submit-carrier-estimates` says "call immediately after"
   - **Required:** Clear, unambiguous tool execution flow
   - **Fix:** Remove or deprecate `submit-carrier-estimates`

4. **Staging Domain**
   - **Issue:** Using `stg-api.mercuryinsurance.com`
   - **Required:** Production domain only
   - **Fix:** Switch to `api.mercuryinsurance.com` or similar

### ✅ What's Already Correct

- [x] Proper structured data collection
- [x] Guardrails against premature tool calls
- [x] Widget rendering works
- [x] Duplicate prevention implemented
- [x] Read-only hints set
- [x] All resources embedded (no external dependencies)

## 🎯 Action Plan

### Phase 1: Deploy Widgets (Required)

**Choose ONE deployment method:**

#### A. Cloudflare Pages (Fastest - 5 minutes)
```bash
# Extract widgets
python scripts/extract_widget.py

# Deploy
cd widgets-deploy
npx wrangler pages deploy . --project-name mercury-insurance-widgets

# Update code
cd ..
python scripts/update_widget_urls.py https://mercury-insurance-widgets.pages.dev
```

**Result:** Widgets hosted at `https://mercury-insurance-widgets.pages.dev`

#### B. Custom Domain (Professional - 30 minutes)
1. Configure DNS: `widgets.mercuryinsurance.com`
2. Deploy to Cloudflare Pages with custom domain
3. Update code with custom URL

**Result:** Widgets hosted at `https://widgets.mercuryinsurance.com`

#### C. Same Domain (Alternative)
Add static file serving to your API server (see WIDGET_DEPLOYMENT_QUICKSTART.md)

**Result:** Widgets at `https://api.mercuryinsurance.com/widgets/`

### Phase 2: Fix Tool Flow (Required)

**Option 1: Remove submit-carrier-estimates (Recommended)**

The tool is unused - `get-enhanced-quick-quote` already does everything.

In your tool configuration, remove or comment out the `submit-carrier-estimates` tool.

**Option 2: Update Instructions**

If you need both tools for some workflow, update the descriptions to be clear:

```python
# get-enhanced-quick-quote
description="""
...
After calling this tool, the complete quote is generated and displayed.
If the user wants to proceed with a specific carrier, ask them first,
then call submit-carrier-estimates.
"""

# submit-carrier-estimates
description="""
...
OPTIONAL: Only call this tool if the user explicitly wants to proceed
with a specific carrier after reviewing the quick quote.
Do NOT call this automatically.
"""
```

### Phase 3: Switch to Production Domain (Required)

Update all references from:
- `stg-api.mercuryinsurance.com` → `api.mercuryinsurance.com`

In your code:
```python
# Change this
SERVER_BASE_URL = "https://stg-api.mercuryinsurance.com"

# To this
SERVER_BASE_URL = "https://api.mercuryinsurance.com"
```

Or use environment variables:
```bash
export SERVER_BASE_URL=https://api.mercuryinsurance.com
```

### Phase 4: Configure App Store Settings (Required)

When submitting, configure these settings:

**Widget Domain:**
```
https://YOUR-DEPLOYED-URL
```

Examples:
- `https://mercury-insurance-widgets.pages.dev`
- `https://widgets.mercuryinsurance.com`
- `https://api.mercuryinsurance.com/widgets`

**Widget CSP:**
```
default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://api.mercuryinsurance.com; frame-ancestors https://chatgpt.com https://chat.openai.com;
```

(This is automatically configured if you use the deployment scripts)

## 📝 Pre-Submission Checklist

Before submitting to App Store:

### Widget Hosting
- [ ] Widgets deployed to public URL
- [ ] CSP headers configured
- [ ] Widget loads when accessed directly
- [ ] Widget renders in ChatGPT

### Code Updates
- [ ] `template_uri` updated in widget_registry.py
- [ ] Production domain (not staging)
- [ ] Tested end-to-end

### Tool Configuration
- [ ] Tool flow contradiction resolved
- [ ] Tool descriptions are clear
- [ ] No ambiguous execution paths

### App Store Config
- [ ] `widgetDomain` set
- [ ] `widgetCSP` set
- [ ] Production URLs only

## 🚀 Quick Start (Fastest Path)

To get ready for submission in 10 minutes:

```bash
# 1. Deploy widgets to Cloudflare Pages
python scripts/extract_widget.py
cd widgets-deploy
npx wrangler pages deploy . --project-name mercury-insurance-widgets
cd ..

# 2. Update code (replace URL with your actual deployed URL)
python scripts/update_widget_urls.py https://mercury-insurance-widgets.pages.dev

# 3. Test
uvicorn insurance_server_python.main:app --port 8000
# Generate quote in ChatGPT - verify widget loads

# 4. For production: Add custom domain in Cloudflare Pages dashboard
# Then update URLs again:
# python scripts/update_widget_urls.py https://widgets.mercuryinsurance.com

# 5. Fix tool flow
# Remove or deprecate submit-carrier-estimates tool

# 6. Switch to production domain
# Update all stg-api.mercuryinsurance.com → api.mercuryinsurance.com

# 7. Submit to App Store with:
# - widgetDomain: YOUR-DEPLOYED-URL
# - widgetCSP: (from widgets-deploy/_headers file)
```

## 📚 Documentation

- **WIDGET_DEPLOYMENT_QUICKSTART.md** - Quick deployment guide
- **WIDGET_HOSTING_PLAN.md** - Complete hosting options and architecture
- **widgets-deploy/README.md** - Deployment instructions (after extracting)

## 🔧 Tools Provided

- **scripts/extract_widget.py** - Extract widgets to deployable files
- **scripts/update_widget_urls.py** - Update widget URLs in code

## ❓ Decision Points

You need to decide:

1. **Widget Hosting:**
   - Cloudflare Pages with generated URL? (fastest)
   - Cloudflare Pages with custom domain? (professional)
   - Your own API server? (consolidated)

2. **Tool Flow:**
   - Remove `submit-carrier-estimates`? (recommended)
   - Update descriptions to clarify? (alternative)

3. **Domain:**
   - Ready to switch to production domain now?
   - Need staging environment too?

## 💬 Next Steps

Reply with:
1. Which hosting option you prefer
2. Do you have DNS access for custom domain?
3. Are you ready to switch to production domain?
4. Any questions about the deployment process?

I can provide specific commands and help with any step!
