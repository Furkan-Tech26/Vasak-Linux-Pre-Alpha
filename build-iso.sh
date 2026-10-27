#!/usr/bin/env bash
#
# build-iso.sh — Master build script for Vaşak Linux ISOs
# Run in Arch VM AFTER running build-repo.sh
#
# Usage (in VM):
#   cd ~/vasak-linux
#   sudo ./build-iso.sh [base|tty|xfce|vasak]
#   sudo ./build-iso.sh [base|tty|xfce|vasak] --clean
#
# How it works:
#   archiso has no profile inheritance, so this script composes a staging
#   profile: base airootfs/efiboot/syslinux + variant packages & overlays.
#   A build-time pacman.conf points [vasak] at the local repo built by
#   build-repo.sh, so mkarchiso can install the custom packages.
#

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${VASAK_REPO_DIR:-$HOME/vasak-repo}"
PROFILE="${1:-base}"
CLEAN=false

shift 2>/dev/null || true
while [[ $# -gt 0 ]]; do
	case "$1" in
		--clean|-c) CLEAN=true; shift ;;
		*) echo "Unknown option: $1"; exit 1 ;;
	esac
done

case "$PROFILE" in
	base|tty|xfce|vasak) ;;
	*) echo "Usage: $0 [base|tty|xfce|vasak] [--clean]"; exit 1 ;;
esac

BASE_DIR="$PROJECT_DIR/iso-profiles/base"
VARIANT_DIR="$PROJECT_DIR/iso-profiles/$PROFILE"
BUILD_ROOT="$PROJECT_DIR/build"
STAGE_DIR="$BUILD_ROOT/profile-$PROFILE"
WORK_DIR="$BUILD_ROOT/work-$PROFILE"
OUT_DIR="$VARIANT_DIR/out"

echo "=== Vaşak Linux ISO Builder ==="
echo "Profile: $PROFILE"
echo "Project: $PROJECT_DIR"
echo "Repo:    $REPO_DIR"
echo "Stage:   $STAGE_DIR"
echo "Out:     $OUT_DIR"
echo "Clean:   $CLEAN"
echo ""

# --- Pre-flight checks -------------------------------------------------
[[ $EUID -eq 0 ]] || { echo "Must run as root (sudo)"; exit 1; }

command -v mkarchiso &>/dev/null || { echo "Install archiso: pacman -S archiso"; exit 1; }
command -v rsync &>/dev/null || { echo "Install rsync: pacman -S rsync"; exit 1; }

if [[ ! -f "$REPO_DIR/vasak.db.tar.zst" ]]; then
	echo "Local repo not found at $REPO_DIR"
	echo "Run ./build-repo.sh first (or set VASAK_REPO_DIR)."
	exit 1
fi

# --- Compose staging profile ------------------------------------------
echo "[1/5] Composing staging profile..."
rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR"

# Base files: airootfs + boot menus
rsync -a "$BASE_DIR/airootfs/" "$STAGE_DIR/airootfs/"
rsync -a "$BASE_DIR/efiboot/"  "$STAGE_DIR/efiboot/"
rsync -a "$BASE_DIR/syslinux/" "$STAGE_DIR/syslinux/"

if [[ "$PROFILE" == "base" ]]; then
	cp "$BASE_DIR/profiledef.sh" "$STAGE_DIR/profiledef.sh"
	cp "$BASE_DIR/packages.x86_64" "$STAGE_DIR/packages.x86_64"
else
	cp "$VARIANT_DIR/profiledef.sh" "$STAGE_DIR/profiledef.sh"

	# Merge base packages + variant extras (dedupe, keep order)
	{
		cat "$BASE_DIR/packages.x86_64"
		echo
		cat "$VARIANT_DIR/packages.x86_64"
	} | awk '
		/^[[:space:]]*#/ { print; next }
		/^[[:space:]]*$/ { next }
		{
			name = $1
			if (!(name in seen)) {
				seen[name] = 1
				print name
			}
		}
	' > "$STAGE_DIR/packages.x86_64"

	# Variant airootfs overlay (if any)
	if [[ -d "$VARIANT_DIR/airootfs" ]]; then
		rsync -a "$VARIANT_DIR/airootfs/" "$STAGE_DIR/airootfs/"
	fi
fi

# --- Build-time pacman.conf with the local repo -----------------------
echo "[2/5] Writing build pacman.conf (local [vasak] repo)..."
cat > "$STAGE_DIR/pacman.conf" <<EOF
[options]
Architecture = auto
Color
ParallelDownloads = 8
CheckSpace
SigLevel    = Required DatabaseOptional
LocalFileSigLevel = Optional

[core]
Include = /etc/pacman.d/mirrorlist

[extra]
Include = /etc/pacman.d/mirrorlist

[multilib]
Include = /etc/pacman.d/mirrorlist

[vasak]
SigLevel = Optional TrustAll
Server = file://$REPO_DIR
EOF

# --- Ship the local packages inside the live ISO -----------------------
# mkarchiso wipes /var/cache/pacman/pkg, so use a dedicated persistent path.
# The live system (and the text installer) can then install [vasak] packages
# offline via file:///opt/vasak/repo.
echo "[3/5] Vendoring local [vasak] repo into the live ISO..."
LIVE_REPO="$STAGE_DIR/airootfs/opt/vasak/repo"
mkdir -p "$LIVE_REPO"
cp -a "$REPO_DIR"/vasak.db* "$REPO_DIR"/vasak.files* "$LIVE_REPO"/ 2>/dev/null || true
cp -a "$REPO_DIR"/*.pkg.tar.zst "$LIVE_REPO"/

cat > "$STAGE_DIR/airootfs/etc/pacman.d/mirrorlist-core" <<'EOF'
# Vaşak Linux [vasak] repository — bundled inside the live ISO
Server = file:///opt/vasak/repo
EOF

# --- Enable live services ---------------------------------------------
WANTS="$STAGE_DIR/airootfs/etc/systemd/system/multi-user.target.wants"
mkdir -p "$WANTS"
ln -sf /usr/lib/systemd/system/NetworkManager.service "$WANTS/NetworkManager.service"
# NOTE: lightdm is installed on desktop variants but not enabled on the live
# medium: there is no live user yet, so the ISO boots to a root TTY where you
# can run `vasak-install` (or `systemctl start lightdm` to poke the greeter).

# --- Build ------------------------------------------------------------
echo "[4/5] Building ISO with mkarchiso..."
rm -rf "$WORK_DIR"
mkdir -p "$OUT_DIR"
if [[ "$CLEAN" == true ]]; then
	rm -rf "$OUT_DIR"
	mkdir -p "$OUT_DIR"
fi

mkarchiso -v -w "$WORK_DIR" -o "$OUT_DIR" "$STAGE_DIR"

# --- Report -----------------------------------------------------------
echo "[5/5] Done."
ISO_FILE=$(ls "$OUT_DIR"/*.iso 2>/dev/null | head -1 || true)
if [[ -f "$ISO_FILE" ]]; then
	echo ""
	echo "ISO:  $ISO_FILE"
	echo "Size: $(du -h "$ISO_FILE" | cut -f1)"
	echo ""
	echo "Workdir: $WORK_DIR (safe to delete)"
	echo "Stage:   $STAGE_DIR (safe to delete)"
else
	echo "No ISO found (check the mkarchiso output above)"
	exit 1
fi
