# Vaşak Linux 🐾

**Vaşak Linux** is an independent, Arch-based Linux distribution with its own package repository, a graphical installer, and a custom boot experience. The name comes from the Turkish word for *lynx*.

> ⚠️ **Status: early development.** Things will break, change, and break again. Artwork is currently placeholder. Not recommended for production use yet.

---

## Features

- **Arch-based**: built on `archiso` and `pacman`, so you get rolling-release packages
- **Custom `[vasak]` repository**: distro-specific packages live in their own repo
- **Graphical installer**: Calamares-based, with a custom bootloader selection step
- **Bootloader choice**: pick systemd-boot, GRUB, or both during installation
- **Optional boot animation**: a custom Plymouth theme you can enable at install time
- **Multiple ISO variants**: `base`, `tty`, and `xfce`
- **VM-friendly**: `open-vm-tools` support for clipboard sharing and auto-resize in VMware

## ISO Variants

| Variant | Description |
|---------|-------------|
| `base`  | Minimal live environment |
| `tty`   | Text-mode only, for advanced users |
| `xfce`  | Live environment with the Xfce desktop |

## Custom Packages

| Package | Purpose |
|---------|---------|
| `vasak-keyring` | Package signing keys |
| `vasak-mirrorlist` | Mirror list for the `[vasak]` repo |
| `vasak-installer` | Installation scripts |
| `vasak-calamares` | Calamares configuration and custom modules |
| `vasak-desktop-settings` | Default desktop configuration |
| `vasak-artwork` | Logos, wallpapers, and boot themes |

## Building the ISO

The ISO must be built in an **Arch Linux environment** (native Arch, an Arch container, or WSL with Arch). Building on plain Windows is not supported.

```bash
# Install build dependencies
sudo pacman -S archiso

# Clone the repository
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>/iso-profiles/base

# Build
sudo ./build.sh -p base -v
```

### Build options

| Flag | Description |
|------|-------------|
| `-v`, `--verbose` | Verbose output |
| `-c`, `--clean` | Clean the work directory before building |
| `-o`, `--out-dir` | Output directory (default: `./out`) |
| `-p`, `--profile` | Profile to build (default: `base`) |
| `-h`, `--help` | Show help |

The finished `.iso` will be in the output directory.

## Testing in a Virtual Machine

1. Create a new VM (VMware Workstation, VirtualBox, etc.)
2. Guest OS: **Linux → Other Linux 6.x 64-bit**
3. Give it at least **2 GB RAM** (the live ISO runs from memory)
4. Attach the ISO and boot, trying **both UEFI and BIOS** modes
5. Run the installer from the live session

## Installation

Boot the live ISO and follow the installer:

- **GUI variants**: launch the Calamares installer from the live desktop
- **Text-mode**: run `sudo vasak-install` from the live prompt

See [`docs/INSTALL.md`](docs/INSTALL.md) for the full guide.

## Project Structure

```
.
├── iso-profiles/     # archiso profiles (base, tty, xfce)
├── packages/core/    # PKGBUILDs for [vasak] packages
└── docs/             # Documentation
```

## Roadmap

- [ ] Replace placeholder artwork with final logo and wallpapers
- [ ] Package signing with a proper `vasak-keyring`
- [ ] Hosted `[vasak]` repository
- [ ] First public ISO release
- [ ] Custom desktop environment

## Contributing

Issues and pull requests are welcome. For big changes, please open an issue first to discuss what you'd like to change.

## License

<!-- Choose a license, e.g. GPL-3.0 or MIT -->
TBD

## Acknowledgments

- [Arch Linux](https://archlinux.org/) and the `archiso` project
- [Calamares](https://calamares.io/) installer framework
- [Plymouth](https://www.freedesktop.org/wiki/Software/Plymouth/) boot splash
