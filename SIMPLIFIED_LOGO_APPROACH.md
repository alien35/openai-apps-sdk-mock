# Simplified Logo Rendering Approach

## Current Problem

The widget unnecessarily complicates logo rendering by:
1. Requiring a `server_url` from the backend
2. Dynamically setting `img.src` attributes in JavaScript
3. Making HTTP requests to load images
4. Falling back to text when `server_url` is missing

**This is overengineered.** Logos should be static; only the data should be dynamic.

## Proposed Solution

**Embed logos directly in the HTML as base64 data URIs.** Only update numbers and text dynamically.

### Benefits

✅ **Self-contained widget** - No external dependencies
✅ **No server_url needed** - Eliminates environment configuration issues
✅ **No HTTP requests** - Faster rendering, no CORS issues
✅ **Works offline** - Widget renders even without backend connection
✅ **Simpler debugging** - If logos don't show, it's a base64 encoding issue, not a network/path issue

### Architecture Change

#### Before (Current - Overcomplicated)
```
Backend → server_url → JavaScript → Construct image URL → HTTP request → Render logo
                                        ↓ (if fails)
                                     Text fallback
```

#### After (Simplified)
```
Backend → carrier data (name, costs) → JavaScript → Update text/numbers only
HTML already contains logos (base64)
```

## Implementation Steps

### Step 1: Generate Base64 Data URIs

```bash
python3 insurance_server_python/utils/image_to_base64.py insurance_server_python/assets/images/mercury-logo.png
python3 insurance_server_python/utils/image_to_base64.py insurance_server_python/assets/images/orion.png
python3 insurance_server_python/utils/image_to_base64.py insurance_server_python/assets/images/progressive.png
```

### Step 2: Update Widget HTML

Two approaches:

#### Approach A: Embed in HTML (Recommended for Fixed Logos)

For the Mercury navbar logo (always the same):

```html
<div class="header">
  <div class="logo-mercury">
    <!-- Embed base64 directly - no JavaScript needed -->
    <img src="data:image/png;base64,iVBORw0KG..." alt="Mercury Insurance">
  </div>
  <div class="powered-by">Powered by AIS</div>
</div>
```

For carrier logos, create a lookup object in JavaScript:

```javascript
const CARRIER_LOGOS = {
  "Mercury Auto Insurance": "data:image/png;base64,iVBORw0KG...",
  "Orion Indemnity": "data:image/png;base64,iVBORw0KG...",
  "Progressive Insurance": "data:image/png;base64,iVBORw0KG...",
  // Add more as needed
};

function getCarrierLogo(carrierName) {
  const normalized = carrierName.toLowerCase();
  for (const [key, logo] of Object.entries(CARRIER_LOGOS)) {
    if (key.toLowerCase().includes(normalized) || normalized.includes(key.toLowerCase())) {
      return logo;
    }
  }
  return null; // Fallback to text
}
```

#### Approach B: Pass Base64 from Backend

Update the backend to include logos in carrier data:

```python
# tool_handlers.py
from .carrier_logos import get_carrier_logo

carriers = []
for carrier_name in carrier_names:
    carriers.append({
        "name": carrier_name,
        "logo": get_carrier_logo(carrier_name),  # Returns base64 data URI
        "annual_cost": annual_cost,
        "monthly_cost": monthly_cost,
    })
```

Then in the widget, just use the logo directly:

```javascript
row.innerHTML = `
  <div class="carrier-left">
    ${carrier.logo
      ? `<img class="carrier-logo" src="${carrier.logo}" alt="${carrier.name}">`
      : `<div style="font-weight: 600; font-size: 16px;">${carrier.name}</div>`
    }
  </div>
  <!-- ... rest of row -->
`;
```

**No `server_url` needed at all.**

### Step 3: Populate carrier_logos.py

Currently it's empty. Populate it with base64 constants:

```python
# carrier_logos.py

# Generated with: python utils/image_to_base64.py assets/images/mercury-logo.png
MERCURY_LOGO = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAA1wAAA..."

ORION_LOGO = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAPoAAABkCAYAAA..."

PROGRESSIVE_LOGO = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAf..."

# Mapping
CARRIER_LOGOS = {
    "Mercury Auto Insurance": MERCURY_LOGO,
    "Mercury Insurance": MERCURY_LOGO,
    "Orion Indemnity": ORION_LOGO,
    "Orion": ORION_LOGO,
    "Progressive Insurance": PROGRESSIVE_LOGO,
    "Progressive": PROGRESSIVE_LOGO,
}

def get_carrier_logo(carrier_name: str) -> str:
    """Get base64 data URI for a carrier logo."""
    # Try exact match first
    if carrier_name in CARRIER_LOGOS:
        return CARRIER_LOGOS[carrier_name]

    # Try fuzzy match
    normalized = carrier_name.lower()
    for key, logo in CARRIER_LOGOS.items():
        if key.lower() in normalized or normalized in key.lower():
            return logo

    # Return empty string (widget will show text fallback)
    return ""
```

### Step 4: Remove server_url Logic

1. **Remove from backend:**
   ```python
   # tool_handlers.py - DELETE THIS
   server_base_url = os.getenv("SERVER_BASE_URL", "http://localhost:8000")

   # DELETE from structured_content
   structured_content = {
       # "server_url": server_base_url,  # ← REMOVE THIS LINE
       "carriers": carriers,
       # ...
   }
   ```

2. **Simplify widget JavaScript:**
   ```javascript
   // DELETE ENTIRE FUNCTION
   function getLogoPath(carrierName, serverUrl) { ... }

   // SIMPLIFY updateWidget
   function updateWidget(data) {
     // Remove this line:
     // const serverUrl = data.server_url || data.serverUrl || "";

     // Use carrier.logo directly (if passed from backend)
     // OR use CARRIER_LOGOS lookup (if embedded in JS)
   }
   ```

## Comparison: Before vs After

### Before - Complex Flow
```
1. Set SERVER_BASE_URL environment variable
2. Backend reads env var
3. Backend passes server_url in structured_content
4. MCP sends to ChatGPT
5. ChatGPT passes to widget via openai globals
6. Widget JavaScript extracts server_url
7. Widget constructs image paths
8. Browser makes HTTP requests for images
9. Server serves images (CORS must be configured)
10. Images render

Any failure in steps 1-9 → Text fallback
```

### After - Simple Flow
```
1. Backend passes carrier data (name, logo as base64, costs)
2. Widget renders HTML with embedded logos
3. Widget updates dynamic text/numbers

No network requests, no environment config, no failure points
```

## File Size Considerations

Base64 encoding increases file size by ~33%. For your logos:
- `mercury-logo.png`: 75KB → ~100KB base64
- `orion.png`: 8.7KB → ~12KB base64
- `progressive.png`: 54KB → ~72KB base64

**Total overhead:** ~184KB for all three logos embedded.

This is acceptable because:
- Logos are cached by the browser once loaded
- No additional HTTP requests needed
- Modern networks handle this easily
- Eliminates complexity worth the tradeoff

If size is a concern, optimize the PNGs first:
```bash
# Install optipng or imagemagick
optipng -o7 insurance_server_python/assets/images/*.png
```

## Migration Path

1. **Keep current implementation working** (don't break anything)
2. **Add base64 logos** to `carrier_logos.py`
3. **Update backend** to pass `logo` field in carrier data
4. **Update widget** to use `carrier.logo` if present, fallback to `server_url` method
5. **Test** - verify logos render with base64
6. **Remove server_url logic** once base64 approach is confirmed working
7. **Clean up** - delete unused code

## Recommended Approach

**Use Approach B** (pass base64 from backend) because:
- Backend already has `carrier_logos.py` infrastructure
- Keeps widget HTML smaller
- Backend controls which logo to use for each carrier
- Easy to add new carriers without touching widget code
- Widget remains data-driven (receives everything it needs in the data payload)

## Code Changes Required

### 1. Populate carrier_logos.py (Run Once)
```bash
python3 insurance_server_python/utils/image_to_base64.py insurance_server_python/assets/images/mercury-logo.png >> /tmp/logos.txt
python3 insurance_server_python/utils/image_to_base64.py insurance_server_python/assets/images/orion.png >> /tmp/logos.txt
python3 insurance_server_python/utils/image_to_base64.py insurance_server_python/assets/images/progressive.png >> /tmp/logos.txt
```

Then copy the data URIs into `carrier_logos.py` constants.

### 2. Update tool_handlers.py
```python
# Around line 560 in _get_enhanced_quick_quote
carriers.append({
    "name": carrier_name,
    "logo": get_carrier_logo(carrier_name),  # ADD THIS LINE
    "annual_cost": annual_cost,
    "monthly_cost": monthly_cost,
})

# REMOVE server_url from structured_content (line 585)
structured_content = {
    # "server_url": server_base_url,  # DELETE THIS
    "carriers": carriers,
    # ... rest
}
```

### 3. Update quick_quote_results_widget.py
```javascript
// Around line 242 - DELETE Mercury header logo setting code
// DELETE this entire block:
if (mercuryHeaderLogoEl && serverUrl) {
  mercuryHeaderLogoEl.src = `${serverUrl}/assets/images/mercury-logo.png`;
}

// Around line 153 - EMBED Mercury logo directly in HTML
<div class="logo-mercury">
  <img src="data:image/png;base64,iVBORw0KG..." alt="Mercury Insurance">
</div>

// Around line 255 - SIMPLIFY carrier logo rendering
// DELETE getLogoPath function entirely
// REPLACE with:
const logoSrc = carrier.logo || "";  // Use logo from backend

row.innerHTML = `
  <div class="carrier-left">
    ${logoSrc
      ? `<img class="carrier-logo" src="${logoSrc}" alt="${carrier.name}">`
      : `<div style="font-weight: 600; font-size: 16px;">${carrier.name}</div>`
    }
  </div>
  <!-- ... -->
`;
```

## Testing the Fix

1. **Generate base64 logos** and add to `carrier_logos.py`
2. **Update backend** to include `logo` field
3. **Update widget** to use `carrier.logo`
4. **Test standalone:**
   ```bash
   python3 -c "from insurance_server_python.carrier_logos import get_carrier_logo; print(get_carrier_logo('Mercury')[:50])"
   ```
   Should print: `data:image/png;base64,iVBORw0KG...`

5. **Test in ChatGPT:**
   - Start server (no need for SERVER_BASE_URL env var anymore)
   - Trigger quote flow
   - Check DevTools - should see no 404s for images
   - Logos should render immediately

## Summary

**Current approach:** Dynamic image loading via server URLs
**Problem:** Complex, fragile, requires environment config
**Solution:** Embed logos as base64 data URIs
**Result:** Simpler, faster, more reliable

**Change only the data (costs, names), leave the UI (logos) static.**
