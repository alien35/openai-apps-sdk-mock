# Widget Image Assets - Base64 Embedding Guide

## Overview

All images used in MCP widgets **must be embedded as base64 data URIs** instead of using external HTTP image URLs. This is because ChatGPT's widget rendering context does not support external HTTP requests for images.

## Why Base64 Encoding?

When a widget is rendered in ChatGPT:
- The HTML is sandboxed and cannot make external HTTP requests
- Image `src` attributes pointing to URLs like `/assets/images/foo.png` will result in 404 errors
- Base64-encoded images embedded directly in the HTML work perfectly

## How to Add New Images

### 1. Add the image file to the assets directory
```bash
cp your-image.png insurance_server_python/assets/images/
```

### 2. Convert to base64 and add to widget_assets.py

Run this Python code:

```python
import base64
from pathlib import Path

# Read and encode the image
image_path = Path("insurance_server_python/assets/images/your-image.png")
with open(image_path, "rb") as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Create data URI
data_uri = f"data:image/png;base64,{image_data}"

print(f"Add this to widget_assets.py:")
print(f'YOUR_IMAGE_BASE64 = "{data_uri}"')
```

### 3. Import and use in your widget

In your widget file (e.g., `quick_quote_results_widget.py`):

```python
from .widget_assets import YOUR_IMAGE_BASE64

WIDGET_HTML = f"""
<img src="{YOUR_IMAGE_BASE64}" alt="Your image">
"""
```

## Current Images

- **CAR_BACKGROUND_BASE64**: Full-width header image with car illustration (~69KB) - Used for normal quote display
- **POWERED_BY_LOGO_BASE64**: Mercury Insurance + AIS branding logo (~35KB) - Used in all states
- **PHONE_BACKGROUND_BASE64**: Full-width header image with phone illustration (~123KB) - Used for phone-only states (AK, HI, MA) or when zip lookup fails

## Image Optimization Tips

1. **Compress before encoding**: Use tools like ImageOptim, TinyPNG, or `pngquant` to reduce file size
2. **Use appropriate formats**:
   - PNG for logos and graphics with transparency
   - JPEG for photos (change mime type to `image/jpeg`)
   - SVG can be embedded directly without base64 (as `data:image/svg+xml,<svg>...</svg>`)
3. **Keep file sizes reasonable**: Large base64 strings increase HTML size
   - Target < 100KB per image when possible
   - Consider image dimensions - don't embed huge source images if they'll be displayed small

## Testing

To verify images work correctly:

1. Start the server: `uvicorn insurance_server_python.main:app --port 8000`
2. Open preview: `http://localhost:8000/preview`
3. Check browser console for any image loading errors
4. Verify images display correctly in the widget

## Troubleshooting

**404 errors for images?**
- Images are being referenced by URL instead of base64 data URI
- Check that you're using `{IMAGE_BASE64}` in an f-string, not `"/assets/images/..."`

**Images not displaying?**
- Verify the data URI format: `data:image/png;base64,iVBORw0KG...`
- Check for syntax errors in widget_assets.py
- Ensure imports are correct in the widget file

**Widget HTML too large?**
- Compress images before encoding
- Consider using SVG for vector graphics
- Remove unused images from widget_assets.py
