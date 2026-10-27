#!/usr/bin/env bash
#
# Vaşak Linux DE profile definition for archiso
# Full Vaşak DE (labwc + GTK4 shell) — composes on top of the base profile
#

profile_name="vasak-de"
profile_description="Vaşak Linux with the in-house Vaşak DE (Wayland, Win 8.1 start menu)"

arch="x86_64"

iso_name="vasak-de"
iso_label="VASAK_DE_$(date +%Y%m)"
iso_publisher="Vaşak Linux <https://github.com/Furkan-Tech26/Vasak-Linux-Pre-Alpha>"
iso_application="Vaşak Linux DE Live/Install ISO"
iso_version="$(date +%Y.%m.%d)"

install_dir="vasak"

buildmodes=('iso')
bootmodes=('bios.syslinux' 'uefi.systemd-boot')

pacman_conf="pacman.conf"

airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd' '-Xcompression-level' '15' '-b' '1M')

file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/etc/gshadow"]="0:0:400"
)

# vim: set ft=sh:
