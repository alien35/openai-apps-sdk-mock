#!/usr/bin/env python3
"""
Update widget URLs in widget_registry.py to point to hosted widgets.

Usage:
    python scripts/update_widget_urls.py https://widgets.mercuryinsurance.com
"""

import re
import sys
from pathlib import Path


def update_widget_registry(widget_domain: str, dry_run: bool = False):
    """Update widget_registry.py with hosted widget URLs."""
    registry_path = Path("widget_registry.py")

    if not registry_path.exists():
        print(f"❌ Error: {registry_path} not found")
        print("   Make sure you run this from the project root or insurance_server_python directory")
        return False

    with open(registry_path, "r") as f:
        content = f.read()

    original_content = content

    # Update quick-quote-results widget
    content = re.sub(
        r'template_uri=["\']ui://widget/quick-quote-results\.html["\']',
        f'template_uri="{widget_domain}/quick-quote-results.html"',
        content
    )

    # Update phone-only widget
    content = re.sub(
        r'template_uri=["\']ui://widget/phone-only\.html["\']',
        f'template_uri="{widget_domain}/phone-only.html"',
        content
    )

    # Update insurance-state widget if present
    content = re.sub(
        r'template_uri=["\']ui://widget/insurance-state\.html["\']',
        f'template_uri="{widget_domain}/insurance-state.html"',
        content
    )

    if content == original_content:
        print("⚠️  No widget URIs found to update")
        print("    Check that widget_registry.py contains template_uri definitions")
        return False

    if dry_run:
        print("Dry run - showing changes that would be made:")
        print()
        # Show diff-like output
        for line_num, (old_line, new_line) in enumerate(zip(original_content.split('\n'), content.split('\n')), 1):
            if old_line != new_line:
                print(f"Line {line_num}:")
                print(f"  - {old_line}")
                print(f"  + {new_line}")
                print()
        return True

    # Write updated content
    with open(registry_path, "w") as f:
        f.write(content)

    print(f"✅ Updated {registry_path}")
    print()
    print("Changes made:")

    # Show what was changed
    if "quick-quote-results.html" in content:
        print(f"  ✓ Quick quote widget → {widget_domain}/quick-quote-results.html")
    if "phone-only.html" in content:
        print(f"  ✓ Phone-only widget → {widget_domain}/phone-only.html")
    if "insurance-state.html" in content:
        print(f"  ✓ Insurance state widget → {widget_domain}/insurance-state.html")

    return True


def main():
    """Main function."""
    print("Widget URL Updater")
    print("=" * 50)
    print()

    if len(sys.argv) < 2:
        print("Usage: python scripts/update_widget_urls.py <widget-domain>")
        print()
        print("Examples:")
        print("  python scripts/update_widget_urls.py https://widgets.mercuryinsurance.com")
        print("  python scripts/update_widget_urls.py https://mercury-widgets.pages.dev")
        print()
        print("Options:")
        print("  --dry-run    Show changes without modifying files")
        sys.exit(1)

    widget_domain = sys.argv[1].rstrip('/')
    dry_run = '--dry-run' in sys.argv

    # Validate URL
    if not widget_domain.startswith('https://'):
        print(f"❌ Error: Widget domain must start with https://")
        print(f"   Got: {widget_domain}")
        sys.exit(1)

    print(f"Widget domain: {widget_domain}")
    print(f"Mode: {'Dry run' if dry_run else 'Update files'}")
    print()

    success = update_widget_registry(widget_domain, dry_run)

    if success:
        if not dry_run:
            print()
            print("=" * 50)
            print("✅ Update complete!")
            print()
            print("Next steps:")
            print("1. Test your MCP server: uvicorn insurance_server_python.main:app --port 8000")
            print("2. Verify widgets load from the new domain")
            print("3. Test in ChatGPT")
            print("4. Configure widgetDomain and widgetCSP in App Store settings")
        else:
            print()
            print("To apply these changes, run without --dry-run")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
