#!/bin/bash
# Verify the contents of the live root filesystem (airootfs.sfs).
# Usage: check-rootfs.sh <airootfs.sfs>
set -uo pipefail

SFS="${1:?usage: check-rootfs.sh <airootfs.sfs>}"

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

echo
echo "== offline repo =="
have "opt/vasak/repo/vasak.db.tar.zst"

echo
echo "== no bytecode shipped =="
if grep -q "__pycache__" "$LIST"; then
	printf '  FAIL __pycache__ present in the image\n'
	fail=$((fail + 1))
else
	printf '  ok   no __pycache__\n'
fi

# --- content spot checks ---------------------------------------------------
TMP=$(mktemp -d)
trap 'rm -f "$LIST"; rm -rf "$TMP"' EXIT

echo
echo "== file contents =="
for f in etc/systemd/system/getty@tty1.service.d/autologin.conf root/.bash_profile \
	 etc/xdg/vasak/labwc/rc.xml etc/xdg/vasak/labwc/autostart; do
	"$UNSQ" -q -d "$TMP" -e "$f" "$SFS" >/dev/null 2>&1
done

grep -q -- "--autologin root" "$TMP/etc/systemd/system/getty@tty1.service.d/autologin.conf" 2>/dev/null \
	&& echo "  ok   tty1 auto-logins root" \
	|| { echo "  FAIL tty1 autologin missing"; fail=$((fail + 1)); }

grep -q "vasak-session" "$TMP/root/.bash_profile" 2>/dev/null \
	&& echo "  ok   profile starts vasak-session" \
	|| { echo "  FAIL profile does not start the desktop"; fail=$((fail + 1)); }

grep -q "<labwc_config" "$TMP/etc/xdg/vasak/labwc/rc.xml" 2>/dev/null \
	&& echo "  ok   rc.xml is labwc XML" \
	|| { echo "  FAIL rc.xml is not labwc XML"; fail=$((fail + 1)); }

grep -q "vasak-shell" "$TMP/etc/xdg/vasak/labwc/autostart" 2>/dev/null \
	&& echo "  ok   autostart launches the shell" \
	|| { echo "  FAIL autostart does not launch the shell"; fail=$((fail + 1)); }

echo
if [ "$fail" -ne 0 ]; then
	echo "$fail checks FAILED"
	exit 1
fi
echo "live root filesystem OK"