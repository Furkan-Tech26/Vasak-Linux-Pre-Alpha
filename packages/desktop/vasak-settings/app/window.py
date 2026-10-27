"""Vaşak Settings main window — sidebar + page stack."""

from gi.repository import Gtk, Adw

from pages.appearance import AppearancePage
from pages.wallpaper import WallpaperPage
from pages.panel import PanelPage
from pages.startmenu import StartMenuPage
from pages.display import DisplayPage
from pages.keyboard import KeyboardPage
from pages.sound import SoundPage
from pages.bluetooth import BluetoothPage
from pages.network import NetworkPage
from pages.power import PowerPage
from pages.about import AboutPage


class SettingsWindow(Adw.ApplicationWindow):
    """Vaşak Settings — glassmorphism preferences window."""

    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Vaşak Settings")
        self.set_default_size(900, 600)

        # Header bar + content
        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(Adw.HeaderBar())

        split = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        # Sidebar
        sidebar = Gtk.ListBox()
        sidebar.set_selection_mode(Gtk.SelectionMode.SINGLE)
        sidebar.set_activate_on_single_click(True)
        sidebar.add_css_class("settings-sidebar")
        sidebar.set_margin_top(8)
        sidebar.set_margin_bottom(8)
        sidebar.set_margin_start(8)
        sidebar.set_margin_end(8)

        sidebar_scroll = Gtk.ScrolledWindow()
        sidebar_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sidebar_scroll.set_size_request(230, -1)
        sidebar_scroll.set_child(sidebar)
        split.append(sidebar_scroll)

        # Page stack
        self.stack = Gtk.Stack()
        self.stack.set_hexpand(True)
        self.stack.set_vexpand(True)
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(150)
        split.append(self.stack)

        pages = [
            ("Appearance", "preferences-desktop-theme-symbolic", AppearancePage),
            ("Wallpaper", "preferences-desktop-wallpaper-symbolic", WallpaperPage),
            ("Panel", "preferences-desktop-panel-symbolic", PanelPage),
            ("Start Menu", "preferences-desktop-menu-symbolic", StartMenuPage),
            ("Display", "preferences-desktop-display-symbolic", DisplayPage),
            ("Keyboard", "preferences-desktop-keyboard-symbolic", KeyboardPage),
            ("Sound", "audio-volume-high-symbolic", SoundPage),
            ("Bluetooth", "bluetooth-symbolic", BluetoothPage),
            ("Network", "network-wired-symbolic", NetworkPage),
            ("Power", "xfpm-battery-100-symbolic", PowerPage),
            ("About", "help-about-symbolic", AboutPage),
        ]

        first_row = None
        for label, icon_name, page_cls in pages:
            page = page_cls()
            self.stack.add_titled(page, label, label)

            row = Gtk.ListBoxRow()
            row.add_css_class("settings-sidebar-row")
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            hbox.set_margin_start(12)
            hbox.set_margin_end(12)
            hbox.set_margin_top(8)
            hbox.set_margin_bottom(8)
            icon = Gtk.Image.new_from_icon_name(icon_name)
            icon.set_pixel_size(20)
            hbox.append(icon)
            lbl = Gtk.Label(label=label)
            lbl.set_hexpand(True)
            lbl.set_xalign(0.0)
            hbox.append(lbl)
            row.set_child(hbox)

            row.connect("activated", lambda *_, name=label: self.stack.set_visible_child_name(name))
            sidebar.append(row)
            if first_row is None:
                first_row = row

        if first_row is not None:
            sidebar.select_row(first_row)

        toolbar.set_content(split)
        self.set_content(toolbar)
        self.stack.set_visible_child_name("Appearance")
