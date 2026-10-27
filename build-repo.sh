#!/usr/bin/env bash
#
# build-repo.sh — Run ONCE in your Arch VM to build all custom packages
# and create a local [vasak] repo that the ISO build can use.
#
# Usage (in VM):
#   cp -r /mnt/hgfs/vasak-linux ~/vasak-linux
#   cd ~/vasak-linux
#   sudo ./build-repo.sh
#
# Environment:
#   VASAK_REPO_DIR — override the repo output directory (default: ~/vasak-repo)
#

set -euo pipefail

REPO_DIR="${VASAK_REPO_DIR:-$HOME/vasak-repo}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Core packages (from packages/core/)
CORE_PKGS=(
	"vasak-keyring"
	"vasak-mirrorlist"
	"vasak-installer"
	"vasak-desktop-settings"
	"vasak-artwork"
	"vasak-vpm"
)

# Desktop Environment packages (from packages/desktop/)
DESKTOP_PKGS=(
	"vasak-shell"
	"vasak-settings"
	"vasak-theme"
	"vasak-session"
	"vasak-de-meta"
)

echo "=== Vaşak Linux: Building Custom Package Repo ==="
echo "Project: $PROJECT_DIR"
echo "Repo dir: $REPO_DIR"
echo ""

# Install build dependencies (works both as root and as a sudo user)
echo "[1/4] Installing build dependencies..."
if [[ $EUID -eq 0 ]]; then
	pacman -S --needed --noconfirm base-devel git rsync namcap librsvg python-gobject gtk4 gnupg
else
	sudo pacman -S --needed --noconfirm base-devel git rsync namcap librsvg python-gobject gtk4 gnupg
fi

# Determine the (non-root) user that should run makepkg
BUILD_USER="${SUDO_USER:-}"
if [[ $EUID -ne 0 ]]; then
	BUILD_USER="$(id -un)"
elif [[ -z "$BUILD_USER" || "$BUILD_USER" == "root" ]]; then
	echo "Cannot build packages as root."
	echo "Run this script via sudo from a normal user account."
	exit 1
fi

mkdir -p "$REPO_DIR"
cd "$REPO_DIR"

# Start clean so removed/renamed packages don't linger in the DB
rm -f "$REPO_DIR"/*.pkg.tar.zst "$REPO_DIR"/vasak.db* "$REPO_DIR"/vasak.files*

# Build each package
echo "[2/4] Building packages..."
build_pkg() {
	local pkg_dir="$1"
	local pkg_name
	pkg_name="$(basename "$pkg_dir")"
	echo "  → $pkg_name"
	cd "$pkg_dir"

	# Drop stale build artifacts from previous runs. Package sources live in
	# app/ or top-level directories; src/ is always makepkg's working copy.
	rm -rf pkg src *.pkg.tar.zst

	if [[ $EUID -eq 0 ]]; then
		sudo -u "$BUILD_USER" makepkg -f --noconfirm --skippgpcheck --nodeps
	else
		makepkg -f --noconfirm --skippgpcheck --nodeps
	fi

	# Copy artifacts
	cp ./*.pkg.tar.zst "$REPO_DIR/"
}

for pkg in "${CORE_PKGS[@]}"; do
	pkg_path="$PROJECT_DIR/packages/core/$pkg"
	if [[ -d "$pkg_path" ]]; then
		build_pkg "$pkg_path"
	else
		echo "  → $pkg [SKIP - not found]"
	fi
done

for pkg in "${DESKTOP_PKGS[@]}"; do
	pkg_path="$PROJECT_DIR/packages/desktop/$pkg"
	if [[ -d "$pkg_path" ]]; then
		build_pkg "$pkg_path"
	else
		echo "  → $pkg [SKIP - not found]"
	fi
done

# Create repo database
echo "[3/4] Creating repo database..."
cd "$REPO_DIR"
repo-add vasak.db.tar.zst ./*.pkg.tar.zst

# Optional repo signing. Off by default: the ISO and the installed system use
# `SigLevel = Optional TrustAll` for [vasak], and an ephemeral CI key only adds
# failure modes. Enable with VASAK_SIGN_REPO=1 when publishing the repo.
echo "[4/4] Signing repo..."
if [[ "${VASAK_SIGN_REPO:-0}" == "1" ]]; then
	if ! gpg --batch --list-keys "Vaşak Linux Build" &>/dev/null; then
		cat > /tmp/vasak-key-gen <<'EOF'
%echo Generating Vaşak Linux Build Key
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: Vaşak Linux Build
Name-Email: build@vasak-linux.org
Expire-Date: 0
%no-protection
%commit
%echo Done
EOF
		gpg --batch --generate-key /tmp/vasak-key-gen
		rm -f /tmp/vasak-key-gen
	fi

	gpg --batch --yes --detach-sign --armor vasak.db.tar.zst
	gpg --batch --yes --detach-sign --armor vasak.files.tar.zst
else
	echo "  Signing skipped (set VASAK_SIGN_REPO=1 to enable)"
fi

echo ""
echo "=== Repo Ready ==="
echo "Location: $REPO_DIR"
echo "Packages:"
ls -1 ./*.pkg.tar.zst
echo ""
echo "Next: build an ISO with ./build-iso.sh [base|tty|xfce|vasak]"
