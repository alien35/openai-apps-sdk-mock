#!/usr/bin/env python3
"""
Extract widget HTML to standalone files for deployment.

This script extracts the widget HTML from Python modules
and creates standalone HTML files ready for hosting.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML
from phone_only_widget import PHONE_ONLY_WIDGET_HTML


def extract_widgets(output_dir: Path):
    """Extract widget HTML files to output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract quick quote results widget
    quick_quote_path = output_dir / "quick-quote-results.html"
    with open(quick_quote_path, "w", encoding="utf-8") as f:
        f.write(QUICK_QUOTE_RESULTS_WIDGET_HTML)
    print(f"✓ Extracted quick quote widget to: {quick_quote_path}")

    # Extract phone-only widget
    phone_only_path = output_dir / "phone-only.html"
    with open(phone_only_path, "w", encoding="utf-8") as f:
        f.write(PHONE_ONLY_WIDGET_HTML)
    print(f"✓ Extracted phone-only widget to: {phone_only_path}")

    return [quick_quote_path, phone_only_path]


def create_headers_file(output_dir: Path, api_domain: str = "https://api.mercuryinsurance.com"):
    """Create _headers file for Cloudflare Pages with CSP configuration."""
    headers_content = f"""# Content Security Policy and CORS headers for widgets

/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: ALLOW-FROM https://chatgpt.com
  Referrer-Policy: strict-origin-when-cross-origin

/quick-quote-results.html
  Content-Security-Policy: default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' {api_domain}; frame-ancestors https://chatgpt.com https://chat.openai.com;
  Access-Control-Allow-Origin: https://chatgpt.com
  Content-Type: text/html; charset=utf-8

/phone-only.html
  Content-Security-Policy: default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' {api_domain}; frame-ancestors https://chatgpt.com https://chat.openai.com;
  Access-Control-Allow-Origin: https://chatgpt.com
  Content-Type: text/html; charset=utf-8
"""

    headers_path = output_dir / "_headers"
    with open(headers_path, "w", encoding="utf-8") as f:
        f.write(headers_content)
    print(f"✓ Created _headers file at: {headers_path}")
    return headers_path


def create_readme(output_dir: Path, widget_domain: str = "https://widgets.mercuryinsurance.com"):
    """Create README with deployment instructions."""
    readme_content = f"""# Mercury Insurance Widgets

This directory contains the widget HTML files for the Mercury Insurance ChatGPT app.

## Files

- `quick-quote-results.html` - Main quote results widget
- `phone-only.html` - Phone-only state widget (AK, HI, MA)
- `_headers` - Cloudflare Pages headers configuration (CSP, CORS)

## Deployment

### Cloudflare Pages (Recommended)

1. Install Wrangler CLI:
   ```bash
   npm install -g wrangler
   ```

2. Deploy:
   ```bash
   wrangler pages deploy . --project-name mercury-insurance-widgets
   ```

3. Configure custom domain:
   - Go to Cloudflare Pages dashboard
   - Select project: mercury-insurance-widgets
   - Custom Domains → Add: `widgets.mercuryinsurance.com`

### Vercel

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Deploy:
   ```bash
   vercel --prod
   ```

3. Configure custom domain in Vercel dashboard

### AWS S3 + CloudFront

1. Upload files to S3 bucket
2. Enable static website hosting
3. Create CloudFront distribution
4. Configure custom domain
5. Add CSP headers in CloudFront response headers policy

## Widget URLs

After deployment, your widgets will be available at:

- Quick Quote: `{widget_domain}/quick-quote-results.html`
- Phone Only: `{widget_domain}/phone-only.html`

## Testing

Test that CSP headers are present:
```bash
curl -I {widget_domain}/quick-quote-results.html
```

Should see:
```
Content-Security-Policy: ...
Access-Control-Allow-Origin: https://chatgpt.com
```

## Update Code

After deployment, update your code to reference the hosted widgets:

In `widget_registry.py`:
```python
WidgetDefinition(
    identifier="quick-quote-results",
    title="Quick Quote Results",
    template_uri="{widget_domain}/quick-quote-results.html",  # ✅ Hosted URL
    # ...
)
```

## Security

The `_headers` file configures:
- Content Security Policy (CSP) - Required for App Store
- CORS headers - Allow ChatGPT to load widgets
- Frame ancestors - Restrict embedding to ChatGPT only

Do not modify the CSP without understanding the security implications.
"""

    readme_path = output_dir / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"✓ Created README at: {readme_path}")
    return readme_path


def main():
    """Main extraction function."""
    print("Mercury Insurance Widget Extractor")
    print("=" * 50)

    # Get output directory
    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])
    else:
        output_dir = Path(__file__).parent.parent / "widgets-deploy"

    print(f"Output directory: {output_dir}")
    print()

    # Extract widgets
    widget_files = extract_widgets(output_dir)

    # Create supporting files
    create_headers_file(output_dir)
    create_readme(output_dir)

    print()
    print("=" * 50)
    print("✅ Extraction complete!")
    print()
    print(f"📁 Files ready for deployment in: {output_dir}")
    print()
    print("Next steps:")
    print("1. Review the files in the output directory")
    print("2. Choose a hosting provider (Cloudflare Pages, Vercel, AWS)")
    print("3. Follow the deployment instructions in README.md")
    print("4. Update widget_registry.py with the hosted URLs")
    print()
    print(f"Quick deploy to Cloudflare Pages:")
    print(f"  cd {output_dir}")
    print(f"  wrangler pages deploy . --project-name mercury-insurance-widgets")


if __name__ == "__main__":
    main()
