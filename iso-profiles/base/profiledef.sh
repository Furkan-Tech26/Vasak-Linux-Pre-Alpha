#!/usr/bin/env bash
#
# Vasak Linux base profile definition for archiso
# Independent distro using pacman + Arch repos + AUR
# "Vasak" = badger (Anatolian native), successor to Pardus (leopard)
#

# Profile name and description
profile_name="vasak-base"
profile_description="Vasak Linux - Minimal base using pacman, Arch repos & AUR"

# Architecture
arch="x86_64"

# ISO settings
iso_name="vasak"
iso_label="VASAK_$(date +%Y%m)"
iso_publisher="Vasak Linux <https://github.com/Furkan-Tech26/Vasak-Linux-Pre-Alpha>"
iso_application="Vasak Linux Live/Install ISO"
iso_version="$(date +%Y.%m.%d)"

# Installation settings
install_dir="vasak"

# Build modes and boot modes (modern archiso syntax)
buildmodes=('iso')
bootmodes=('bios.syslinux' 'uefi.systemd-boot')

# Pacman configuration for the live environment
pacman_conf="pacman.conf"

# Squashfs image settings
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd' '-Xcompression-level' '15' '-b' '1M')

# File permissions (archiso requires this array)
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/etc/gshadow"]="0:0:400"
)

# vim: set ft=sh:
