#!/usr/bin/env bash
#
# convert-branding.sh — Run in Arch VM to convert SVG branding to PNG
# for Calamares (requires librsvg)
#
# Usage (in VM):
#   cd ~/vasak-linux
#   ./convert-branding.sh
#

set -euo pipefail

BRANDING_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/packages/core/vasak-calamares/branding/vasak"

echo "=== Converting Vaşak Calamares Branding SVG → PNG ==="
echo "Dir: $BRANDING_DIR"

# Check for rsvg-convert
if ! command -v rsvg-convert &>/dev/null; then
    echo "Installing librsvg..."
    sudo pacman -S --needed --noconfirm librsvg
fi

cd "$BRANDING_DIR"

# Welcome screen (900x650)
echo "Converting welcome.svg → welcome.png"
rsvg-convert -w 900 -h 650 welcome.svg -o welcome.png

# Background (900x650)
echo "Converting background.svg → background.png"
rsvg-convert -w 900 -h 650 background.svg -o background.png

# Sidebar (280x650)
echo "Converting sidebar.svg → sidebar.png"
rsvg-convert -w 280 -h 650 sidebar.svg -o sidebar.png

# Logo (200x200)
echo "Converting logo.svg → logo.png"
rsvg-convert -w 200 -h 200 logo.svg -o logo.png

echo ""
echo "=== Done ==="
ls -lh *.png
echo ""
echo "Now rebuild vasak-calamares package to include PNGs:"
echo "  cd ~/vasak-linux/packages/core/vasak-calamares && makepkg -si"