#!/bin/bash
# Verify the contents of the live root filesystem (airootfs.sfs).
# Usage: check-rootfs.sh <airootfs.sfs> [profile]
#   profile: vasak (default), tty, base, xfce
set -uo pipefail

echo "check-rootfs.sh version: 20261028-1 (grep -F fix)"

SFS="${1:?usage: check-rootfs.sh <airootfs.sfs> [profile]}"
PROFILE="${2:-vasak}"

# Use the system unsquashfs (installed by archiso/mkarchiso)
UNSQ="unsquashfs"
LIST=$(mktemp)
trap 'rm -f "$LIST"' EXIT

echo "== listing =="
"$UNSQ" -l "$SFS" > "$LIST" 2>/dev/null || { echo "unsquashfs failed"; exit 1; }
echo "$(wc -l < "$LIST") entries"

fail=0
have() {
	if grep -qxF "squashfs-root/$1" "$LIST"; then
		printf '  ok   %s\n' "$1"
	else
		printf '  FAIL %s (missing)\n' "$1"
		fail=$((fail + 1))
	fi
}

# Profile-specific expected files
check_profile_files() {
	case "$PROFILE" in
		vasak|xfce)
			echo
			echo "== live session wiring =="
			have "etc/systemd/system/getty@tty1.service.d/autologin.conf"
			have "root/.bash_profile"
			have "usr/bin/vasak-session"
			have "usr/bin/vasak-shell"
			have "usr/bin/vasak-settings"
			have "usr/bin/labwc"
			have "usr/share/wayland-sessions/vasak-de.desktop"

			echo
			echo "== desktop config + assets =="
			have "etc/xdg/vasak/labwc/rc.xml"
			have "etc/xdg/vasak/labwc/menu.xml"
			have "etc/xdg/vasak/labwc/autostart"
			have "usr/share/vasak-shell/main.py"
			have "usr/share/vasak-shell/data/shell.css"
			have "usr/share/vasak-shell/ipc.py"
			have "usr/share/vasak-shell/startmenu/window.py"
			have "usr/share/backgrounds/vasak/glass.png"
			have "usr/share/themes/Vasak-Glass/gtk-4.0/gtk-dark.css"
			have "usr/share/pixmaps/vasak-logo.png"

			echo
			echo "== graphics stack (VMware needs vmwgfx) =="
			have "usr/lib/girepository-1.0/Gtk4LayerShell-1.0.typelib"
			have "usr/lib/dri/swrast_dri.so"
			have "usr/lib/dri/vmwgfx_dri.so"
			;;
		tty|base)
			echo
			echo "== base live session =="
			have "etc/systemd/system/getty@tty1.service.d/autologin.conf"
			have "root/.bash_profile"
			have "usr/bin/vasak-install"
			;;
	esac

	echo
	echo "== offline repo =="
	have "opt/vasak/repo/vasak.db.tar.zst"
}

check_profile_files

echo
echo "== no bytecode shipped =="
# System Python installs its own __pycache__ in /usr/lib/python3.*/ - that's expected.
# Only fail on __pycache__ in our own package directories.
PYCACHE_MATCHES=$(grep "__pycache__" "$LIST" | grep -v "usr/lib/python3\." || true)
if [ -n "$PYCACHE_MATCHES" ]; then
	printf '  FAIL __pycache__ present in our packages\n'
	echo "$PYCACHE_MATCHES" | head -20 | sed 's/^/    /'
	fail=$((fail + 1))
else
	printf '  ok   no __pycache__ in our packages (system python pycache ignored)\n'
fi

# --- content spot checks ---------------------------------------------------
TMP=$(mktemp -d)
trap 'rm -f "$LIST"; rm -rf "$TMP"' EXIT

echo
echo "== file contents =="

# Extract the whole squashfs to a temp dir for content checks
FULL_EXTRACT="$TMP/full"
mkdir -p "$FULL_EXTRACT"
echo "  Extracting $SFS to $FULL_EXTRACT"
"$UNSQ" -d "$FULL_EXTRACT" "$SFS"
EXTRACT_RC=$?
echo "  unsquashfs exit code: $EXTRACT_RC"
if [ $EXTRACT_RC -ne 0 ]; then
    echo "  FAIL full extraction failed (exit $EXTRACT_RC)"
    fail=$((fail + 1))
fi

SRC="$FULL_EXTRACT/squashfs-root"

# Some unsquashfs versions extract directly to dest dir, not dest/squashfs-root
if [ ! -d "$SRC" ]; then
    # Check if files were extracted directly to FULL_EXTRACT
    if [ -f "$FULL_EXTRACT/etc/systemd/system/getty@tty1.service.d/autologin.conf" ]; then
        echo "  Files extracted directly to $FULL_EXTRACT (no squashfs-root)"
        SRC="$FULL_EXTRACT"
    else
        echo "  FAIL extraction did not create squashfs-root"
        echo "  Contents of $FULL_EXTRACT:"
        ls -la "$FULL_EXTRACT" | sed 's/^/    /'
        fail=$((fail + 1))
    fi
else
    echo "  Extracted tree root: $SRC"
fi

check_file() {
    local file="$1"
    local pattern="$2"
    local msg_ok="$3"
    local msg_fail="$4"
    if [ -f "$SRC/$file" ] && fgrep -q "$pattern" "$SRC/$file"; then
        echo "  ok   $msg_ok"
    else
        echo "  FAIL $msg_fail"
        [ -f "$SRC/$file" ] && echo "       (file exists but pattern not found)" || echo "       (file not extracted)"
        fail=$((fail + 1))
    fi
}

check_file "etc/systemd/system/getty@tty1.service.d/autologin.conf" "--autologin root" "tty1 auto-logins root" "tty1 autologin missing"
check_file "root/.bash_profile" "vasak-session" "profile starts vasak-session" "profile does not start the desktop"

if [ "$PROFILE" = "vasak" ] || [ "$PROFILE" = "xfce" ]; then
    check_file "etc/xdg/vasak/labwc/rc.xml" "<labwc_config" "rc.xml is labwc XML" "rc.xml is not labwc XML"
    check_file "etc/xdg/vasak/labwc/autostart" "vasak-shell" "autostart launches the shell" "autostart does not launch the shell"
fi

echo
if [ "$fail" -ne 0 ]; then
	echo "$fail checks FAILED"
	exit 1
fi
echo "live root filesystem OK"