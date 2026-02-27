# MCP Apps Metadata Implementation

## Summary

Widgets now include proper MCP Apps metadata in their resource registration. This metadata tells ChatGPT where widgets are hosted and what security policies to enforce.

## Changes Made

### 1. Added UI Metadata to Resource Registration

**File:** `insurance_server_python/widget_registry.py`

**What Changed:**
Updated the `_tool_meta()` function to include MCP Apps `ui` metadata:

```python
def _tool_meta(widget: WidgetDefinition) -> Dict[str, Any]:
    """Generate tool metadata for a widget."""
    return {
        "openai/outputTemplate": widget.template_uri,
        "openai/toolInvocation/invoking": widget.invoking,
        "openai/toolInvocation/invoked": widget.invoked,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
        "annotations": {
            "destructiveHint": False,
            "openWorldHint": False,
            "readOnlyHint": True,
        },
        "ui": {
            "domain": "https://stg-api.mercuryinsurance.com/assets/images",
            "prefersBorder": False,
            "csp": {
                "connectDomains": [
                    "https://stg-api.mercuryinsurance.com",
                    "https://api.mercuryinsurance.com"
                ],
            },
        }
    }
```

**What It Does:**
- `ui.domain`: Tells ChatGPT where widget HTML files are hosted
- `ui.prefersBorder`: Controls whether ChatGPT draws a border around the widget
- `ui.csp.connectDomains`: Lists domains the widget can make API calls to
- This metadata is included in both resource and tool registrations

### 2. Updated MIME Type

**File:** `insurance_server_python/constants.py`

**What Changed:**
```python
# Before
MIME_TYPE = "text/html+skybridge"

# After
MIME_TYPE = "text/html;profile=mcp-app"
```

**Why:**
- `text/html;profile=mcp-app` is the official MCP Apps MIME type
- Required for ChatGPT to recognize resources as widget templates
- Follows the MCP Apps SDK specification

## How It Works

### Resource Registration Flow

1. **Tool is called** by ChatGPT
2. **Tool handler returns** response with `_meta` containing widget metadata
3. **ChatGPT reads** `_meta.ui.domain` to determine widget domain
4. **ChatGPT constructs** CSP policy from `_meta.ui.csp.connectDomains`
5. **ChatGPT fetches** widget HTML from the specified domain
6. **Widget loads** in sandboxed iframe with CSP restrictions

### Metadata Structure

```json
{
  "_meta": {
    "ui": {
      "domain": "https://stg-api.mercuryinsurance.com/assets/images",
      "prefersBorder": false,
      "csp": {
        "connectDomains": [
          "https://stg-api.mercuryinsurance.com",
          "https://api.mercuryinsurance.com"
        ]
      }
    }
  }
}
```

### CSP Policy Construction

ChatGPT uses the metadata to build a Content Security Policy:

**From metadata:**
- `connectDomains` → `connect-src` directive

**ChatGPT adds:**
- `default-src 'none'` - Block everything by default
- `script-src 'self' 'unsafe-inline'` - Allow widget scripts
- `style-src 'self' 'unsafe-inline'` - Allow widget styles
- `img-src 'self' data:` - Allow base64 images
- `font-src 'self'` - Allow fonts
- `frame-ancestors https://chatgpt.com https://chat.openai.com` - Only embed in ChatGPT

**Final CSP:**
```
default-src 'none';
script-src 'self' 'unsafe-inline';
style-src 'self' 'unsafe-inline';
img-src 'self' data:;
font-src 'self';
connect-src 'self' https://stg-api.mercuryinsurance.com https://api.mercuryinsurance.com;
frame-ancestors https://chatgpt.com https://chat.openai.com;
```

## Verification

### Check Metadata is Present

```bash
python -c "
import sys
sys.path.insert(0, '.')
from insurance_server_python.widget_registry import _tool_meta, WIDGETS_BY_ID, QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER
import json

widget = WIDGETS_BY_ID[QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER]
meta = _tool_meta(widget)
print(json.dumps(meta, indent=2))
"
```

Should show:
```json
{
  "ui": {
    "domain": "https://stg-api.mercuryinsurance.com/assets/images",
    "prefersBorder": false,
    "csp": {
      "connectDomains": [
        "https://stg-api.mercuryinsurance.com",
        "https://api.mercuryinsurance.com"
      ]
    }
  }
}
```

### Test in ChatGPT

1. Request a quote in ChatGPT
2. Check browser DevTools → Network tab
3. Look for request to `quick-quote-results.html`
4. Verify it loads from the configured domain
5. Check no CSP violations in console

## MCP Apps SDK Reference

This implementation follows the [MCP Apps SDK specification](https://modelcontextprotocol.io/docs/apps/quickstart):

### Resource Template Registration

```typescript
_meta: {
  ui: {
    prefersBorder: boolean,
    domain: string,
    csp: {
      connectDomains: string[],
      resourceDomains?: string[],
      frameDomains?: string[],
    },
  },
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `ui.domain` | string | Widget hosting domain (HTTPS required) |
| `ui.prefersBorder` | boolean | Whether to show border around widget |
| `ui.csp.connectDomains` | string[] | Domains for API calls (`connect-src`) |
| `ui.csp.resourceDomains` | string[] | Domains for loading resources (optional) |
| `ui.csp.frameDomains` | string[] | Domains that can be iframed (optional) |

## For Production Deployment

When switching to production, update the domain in `widget_registry.py`:

```python
"ui": {
    "domain": "https://api.mercuryinsurance.com/assets/images",  # Production domain
    "prefersBorder": False,
    "csp": {
        "connectDomains": [
            "https://api.mercuryinsurance.com"  # Production only
        ],
    },
}
```

### Making Domain Configurable

For easy environment switching, use environment variables:

```python
import os

# At top of widget_registry.py
WIDGET_DOMAIN = os.getenv(
    "WIDGET_DOMAIN",
    "https://stg-api.mercuryinsurance.com/assets/images"
)
API_DOMAIN = os.getenv(
    "API_DOMAIN",
    "https://stg-api.mercuryinsurance.com"
)

# In _tool_meta function
"ui": {
    "domain": WIDGET_DOMAIN,
    "prefersBorder": False,
    "csp": {
        "connectDomains": [API_DOMAIN],
    },
}
```

Then switch environments:
```bash
# Staging
export WIDGET_DOMAIN=https://stg-api.mercuryinsurance.com/assets/images
export API_DOMAIN=https://stg-api.mercuryinsurance.com

# Production
export WIDGET_DOMAIN=https://api.mercuryinsurance.com/assets/images
export API_DOMAIN=https://api.mercuryinsurance.com
```

## Advanced CSP Configuration

### Adding Resource Domains

If you need to load resources from a CDN:

```python
"csp": {
    "connectDomains": [
        "https://api.mercuryinsurance.com"
    ],
    "resourceDomains": [
        "https://cdn.mercuryinsurance.com"
    ],
}
```

### Enabling Iframe Embedding

If your widget needs to embed iframes (requires extra scrutiny):

```python
"csp": {
    "connectDomains": [
        "https://api.mercuryinsurance.com"
    ],
    "frameDomains": [
        "https://trusted-provider.com"
    ],
}
```

**Note:** Widgets that enable subframes are reviewed more strictly and may not be approved for directory distribution.

## Troubleshooting

### Widget Not Loading

**Check metadata is returned:**
```bash
# Call tool and check response metadata includes ui.domain
```

**Verify domain matches:**
- Widget URI: `https://stg-api.mercuryinsurance.com/assets/images/quick-quote-results.html`
- Must start with `ui.domain`: `https://stg-api.mercuryinsurance.com/assets/images`

### CSP Errors in Console

**"Refused to connect to..."**
- Add domain to `csp.connectDomains`

**"Refused to load the script..."**
- Widget scripts should be inline or served from same domain
- Check `script-src` in final CSP policy

**"Refused to frame..."**
- Check `frame-ancestors` includes ChatGPT domains
- This is handled automatically by ChatGPT

### Widget Shows "No CSP Set" Error

This error means:
- `_meta.ui.csp` is missing in metadata
- `csp.connectDomains` is empty
- Metadata format is incorrect

Verify metadata structure matches the example above.

## Files Modified

1. `insurance_server_python/widget_registry.py`
   - Added `ui` metadata to `_tool_meta()` function

2. `insurance_server_python/constants.py`
   - Updated `MIME_TYPE` from `text/html+skybridge` to `text/html;profile=mcp-app`

## Related Documentation

- `ASSETS_WIDGET_HOSTING.md` - How widgets are hosted in assets directory
- `CHATGPT_APP_STORE_CONFIG.md` - ChatGPT App Store configuration (may still be needed)
- [MCP Apps SDK Documentation](https://modelcontextprotocol.io/docs/apps/quickstart)

## Testing Checklist

- [ ] Metadata includes `ui.domain`
- [ ] Metadata includes `ui.csp.connectDomains`
- [ ] MIME type is `text/html;profile=mcp-app`
- [ ] Widget URIs match `ui.domain` prefix
- [ ] Server imports without errors
- [ ] Widget loads in ChatGPT
- [ ] No CSP violations in console
- [ ] Widget hydrates with data correctly
