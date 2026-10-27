"""About page."""

from gi.repository import Gtk, Adw


class AboutPage(Adw.NavigationPage):
    def __init__(self):
        super().__init__()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(24)
        box.set_margin_start(24)
        box.set_margin_end(24)
        box.set_margin_bottom(24)

        about = Gtk.AboutDialog()
        about.set_program_name("Vaşak Settings")
        about.set_version("0.1.0")
        about.set_comments("Vaşak DE settings application")
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_website("https://github.com/Furkan-Tech26/Vasak-Linux-Pre-Alpha")

        btn = Gtk.Button(label="About Vaşak Linux")
        btn.add_css_class("flat")
        btn.connect("clicked", lambda *_: about.present())
        box.append(btn)

        self.set_child(box)
