# Vaşak Linux — root login shell on the live medium
#
# tty1 auto-logs in as root (see the getty@tty1 override) and this profile
# starts the Vaşak desktop straight away, so the live ISO boots into the DE
# instead of a bare prompt.
#
# The desktop is started as a child, never with exec: if labwc or vasak-shell
# fails, its output stays on the console and this shell remains available for
# recovery. Set VASAK_NO_DE=1 to skip the autostart at boot.

if [ -z "${VASAK_LIVE_TRIED:-}" ] &&
   [ -z "${VASAK_NO_DE:-}" ] &&
   [ -d /run/archiso/bootmnt ] &&
   [ "$(tty 2>/dev/null)" = "/dev/tty1" ] &&
   command -v vasak-session >/dev/null 2>&1; then
    export VASAK_LIVE_TRIED=1
    printf '\nStarting the Vaşak desktop (labwc)…\n\n'
    vasak-session
    status=$?
    printf '\nThe Vaşak desktop session has ended (status %s).\n' "$status"
    printf 'Start it again with:  vasak-session\n'
    printf 'Install the system with:  vasak-install\n\n'
fi

# Normal login-shell behaviour.
[ -f "$HOME/.bashrc" ] && . "$HOME/.bashrc"
