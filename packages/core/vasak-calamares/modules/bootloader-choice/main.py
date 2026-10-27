#!/usr/bin/env python3
#
# Vaşak Linux - Custom Calamares Module: Bootloader Choice
# Provides UI for selecting bootloader (systemd-boot, GRUB, both) and plymouth
#

from utils.installer import install_package
from utils.target_env import call_in_target
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton,
    QButtonGroup, QCheckBox, QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt

def pretty_name():
    return "Bootloader Choice"

def is_next_enabled():
    return True

def create_ui(widget):
    """Create the UI for bootloader selection"""
    layout = QVBoxLayout(widget)
    widget.setLayout(layout)

    # Title
    title = QLabel("<h2>Bootloader & Boot Animation</h2>")
    title.setWordWrap(True)
    layout.addWidget(title)

    desc = QLabel(
        "Choose your bootloader. GRUB supports both UEFI and BIOS with a "
        "glassmorphism theme. systemd-boot is simpler and UEFI-only. "
        "You can also install both (systemd-boot primary, GRUB as fallback)."
    )
    desc.setWordWrap(True)
    layout.addWidget(desc)

    # Bootloader choice group
    bootloader_group = QGroupBox("Bootloader")
    bootloader_layout = QVBoxLayout(bootloader_group)

    # Radio buttons
    bg = QButtonGroup(widget)
    options = [
        ("systemd-boot", "Simple, fast, UEFI-only. Minimal boot menu."),
        ("GRUB", "Featureful, UEFI + BIOS, glassmorphism theme, dual-boot detection."),
        ("Both", "systemd-boot as primary, GRUB as fallback entry.")
    ]

    for i, (name, tooltip) in enumerate(options):
        rb = QRadioButton(name)
        rb.setToolTip(tooltip)
        bg.addButton(rb, i)
        bootloader_layout.addWidget(rb)
        if i == 2:  # Default: Both
            rb.setChecked(True)

    layout.addWidget(bootloader_group)

    # Plymouth checkbox
    plymouth_check = QCheckBox("Add Plymouth boot animation")
    plymouth_check.setToolTip(
        "Enable graphical boot splash (requires plymouth theme). "
        "Vaşak glassmorphism theme will be used."
    )
    plymouth_check.setChecked(True)
    layout.addWidget(plymouth_check)

    # Store references for later access
    widget.bg = bg
    widget.plymouth_check = plymouth_check

    layout.addStretch()

def store_config(widget):
    """Store the user's choices for later modules to use"""
    # Get selected bootloader (0=systemd-boot, 1=GRUB, 2=Both)
    selected_id = widget.bg.checkedId()
    bootloaders = ["systemd-boot", "grub", "both"]
    selected = bootloaders[selected_id]

    plymouth = widget.plymouth_check.isChecked()

    # Store in Calamares global storage (accessible to other modules)
    from utils import globalstorage
    globalstorage.setValue("vasakBootloader", selected)
    globalstorage.setValue("vasakPlymouth", plymouth)

    return True