# Logo Setup Instructions

## Overview

The insurance widget now uses base64-encoded logos that are embedded directly in the carrier data. This eliminates the need for:
- Setting up `SERVER_BASE_URL` environment variable
- Serving static assets via HTTP
- Dealing with CORS issues
- External HTTP requests for images

## Quick Start (Automated)

### One Command Setup

Simply place all your logo images in `insurance_server_python/assets/images/` and run:

```bash
python3 insurance_server_python/utils/generate_carrier_logos.py
```

**That's it!** The script will:
1. 🔍 Scan the images directory for all logo files
2. 🔄 Convert each to base64 data URI
3. 📝 Generate constant names from filenames
4. 🗺️ Create carrier name mappings automatically
5. ✍️ Write the complete `carrier_logos.py` file

### Supported File Formats

The script supports:
- `.png` (recommended)
- `.jpg` / `.jpeg`
- `.svg`
- `.webp`

### File Naming Convention

The script intelligently generates mappings from your filenames:

| Filename | Generated Constant | Auto-Generated Mappings |
|----------|-------------------|------------------------|
| `mercury-logo.png` | `MERCURY_LOGO` | "Mercury", "Mercury Insurance", "Mercury Auto Insurance" |
| `progressive.png` | `PROGRESSIVE_LOGO` | "Progressive", "Progressive Insurance" |
| `state-farm.png` | `STATE_FARM_LOGO` | "State Farm", "State Farm Insurance" |
| `geico.png` | `GEICO_LOGO` | "Geico", "Geico Insurance", "Geico Auto Insurance" |

**Tips:**
- Use descriptive filenames (e.g., `mercury-logo.png` not `img1.png`)
- Hyphens and underscores are converted to spaces
- The script automatically adds common variations

### Example Workflow

```bash
# 1. Add all your carrier logos
cp ~/Downloads/*.png insurance_server_python/assets/images/

# 2. Run the generator
python3 insurance_server_python/utils/generate_carrier_logos.py

# Output:
# 🔍 Scanning for logo files...
# Found 50 logo files:
#   • mercury-logo.png (75.0 KB) → MERCURY_LOGO
#   • progressive.png (54.0 KB) → PROGRESSIVE_LOGO
#   • state-farm.png (42.3 KB) → STATE_FARM_LOGO
#   ...
#
# 🔄 Converting images to base64...
# Converting mercury-logo.png → MERCURY_LOGO...
# Converting progressive.png → PROGRESSIVE_LOGO...
# ...
#
# ✅ Generated carrier_logos.py
#    - 50 logo files processed
#    - 125 carrier name mappings created
#
# ✨ Done!

# 3. That's it! Your logos are ready to use.
```

## Adding New Carriers

To add a new carrier logo:

1. Drop the logo file in `insurance_server_python/assets/images/`
2. Re-run the generator:
   ```bash
   python3 insurance_server_python/utils/generate_carrier_logos.py
   ```
3. Done! The new logo is automatically included with smart name mappings.

**Example:**
```bash
# Add a new logo
cp ~/new-carrier-logo.png insurance_server_python/assets/images/

# Regenerate (takes seconds even with 50+ logos)
python3 insurance_server_python/utils/generate_carrier_logos.py

# The script will automatically add:
# NEW_CARRIER_LOGO = "data:image/png;base64,..."
#
# CARRIER_LOGOS = {
#     ...
#     "New Carrier": NEW_CARRIER_LOGO,
#     "New Carrier Insurance": NEW_CARRIER_LOGO,
# }
```

## Manual Fine-Tuning (Optional)

If the auto-generated carrier name mappings don't match your API's exact naming, you can manually edit `carrier_logos.py` after generation:

```python
# After running the generator, you can add custom mappings:
CARRIER_LOGOS = {
    # ... auto-generated mappings ...

    # Custom mappings (add these manually if needed):
    "Mercury General": MERCURY_LOGO,  # Custom variation
    "Progressive Direct": PROGRESSIVE_LOGO,  # Custom variation
}
```

Just remember: if you regenerate, you'll need to re-add custom mappings. Consider keeping them in a separate comment block for easy copy-paste.

## Benefits of This Approach

✅ **Self-contained widget** - No external dependencies
✅ **No server_url needed** - Eliminates environment configuration
✅ **No HTTP requests** - Faster rendering, no CORS issues
✅ **Works offline** - Widget renders without backend connection
✅ **Simpler debugging** - Logo issues are encoding issues, not network issues

## File Size Considerations

Base64 encoding increases file size by ~33%. For example:
- `mercury-logo.png`: 75KB → ~100KB base64
- `orion.png`: 8.7KB → ~12KB base64
- `progressive.png`: 54KB → ~72KB base64

**Total overhead:** ~184KB for all three logos

This is acceptable because:
- Logos are cached by the browser
- No additional HTTP requests
- Modern networks handle this easily
- Complexity reduction is worth the tradeoff

### Optimizing Logo File Sizes

If size is a concern, optimize PNGs before converting:

```bash
# Using optipng
optipng -o7 insurance_server_python/assets/images/*.png

# Using ImageMagick
mogrify -strip -quality 85 insurance_server_python/assets/images/*.png
```

## Testing

After setting up logos:

1. Start the server:
   ```bash
   uvicorn insurance_server_python.main:app --port 8000
   ```

2. Test the quick quote flow in ChatGPT

3. Check browser DevTools:
   - Should see no 404 errors for image files
   - Logos should render immediately
   - No network requests for logo images

## Troubleshooting

### Logos not showing

**Problem**: Carrier logos show as text instead of images

**Solution**: Check that:
1. You ran the conversion script and copied the output
2. The base64 string is not empty (`""`)
3. The carrier name matches the keys in `CARRIER_LOGOS`

### Logo appears broken

**Problem**: Logo renders but appears broken or corrupted

**Solution**:
1. Verify the base64 string starts with `data:image/png;base64,`
2. Ensure the full string was copied (no truncation)
3. Try regenerating the base64 from the original image

### Wrong logo showing

**Problem**: Wrong carrier logo is displayed

**Solution**: Check the `CARRIER_LOGOS` mappings and ensure carrier names match exactly (or use fuzzy matching in `get_carrier_logo()`)

## Migration from Old Approach

If you were using the old `server_url` approach:

1. **No environment variable needed**: Remove `SERVER_BASE_URL` from `.env`
2. **No static file serving**: The server doesn't need to serve images anymore
3. **Frontend simplification**: The widget no longer constructs image URLs

The widget will automatically fall back to text display if a carrier has no logo defined.
