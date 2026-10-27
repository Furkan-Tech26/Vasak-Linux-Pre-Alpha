#!/usr/bin/env bash
#
# Vaşak Linux XFCE profile definition for archiso
# Lightweight desktop variant — composes on top of the base profile
#

profile_name="vasak-xfce"
profile_description="Vaşak Linux XFCE - Lightweight GTK desktop"

arch="x86_64"

iso_name="vasak-xfce"
iso_label="VASAK_XFCE_$(date +%Y%m)"
iso_publisher="Vaşak Linux <https://github.com/Furkan-Tech26/Vasak-Linux-Pre-Alpha>"
iso_application="Vaşak Linux XFCE Live/Install ISO"
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
