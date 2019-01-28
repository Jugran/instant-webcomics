import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

from ComicManager import ComicManager
from SourceManager import Comic


class ComicBox(Gtk.Box):
    comicManager = ComicManager()

    def __init__(self):
        super().__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_homogeneous(False)

        self.set_view()
        self.update_comic(self.comicManager.get_next())

    def set_view(self):
        # set comic view elements
        controls = Gtk.Box()

        next_button = Gtk.Button("Next")
        next_button.connect("clicked", self.next)

        prev_button = Gtk.Button("Prev")
        prev_button.connect("clicked", self.prev)

        resize_button = Gtk.Button("Resize")
        resize_button.connect("clicked", self.resize)

        controls.pack_start(prev_button, False, False, 5)
        controls.pack_start(next_button, False, False, 5)
        controls.pack_end(resize_button, False, False, 5)

        comic_header = Gtk.Box()

        self.title = Gtk.Label()
        self.link = Gtk.Label()
        self.image = Gtk.Image()

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.add(self.image)

        comic_header.pack_start(self.title, False, True, 5)
        comic_header.pack_start(self.link, False, False, 5)

        self.pack_start(controls, False, True, 0)
        self.pack_start(comic_header, False, True, 0)
        self.pack_start(self.scrolled_window, True, True, 10)

    def update_comic(self, comic: Comic):

        # update Title Label
        self.title.set_markup("<span size=\"xx-large\"><b>" + comic.Title + "</b></span>")
        self.title.set_line_wrap(True)
        self.title.set_halign(Gtk.Align.START)
        # label.set_selectable(True)

        # update link
        self.link.set_markup("<a href=\"" + comic.ComicURL + "\">Link</a>")
        self.link.set_halign(Gtk.Align.START)

        # update Image
        self.image.set_from_file(comic.Filename)
        self.image.pixbuf = self.image.get_pixbuf()

        # self.resize()

    def next(self, button=None):
        next_comic = self.comicManager.get_next()
        if next_comic is not None:
            self.update_comic(next_comic)

    def prev(self, button=None):
        prev_comic = self.comicManager.get_prev()
        if prev_comic is not None:
            self.update_comic(prev_comic)

    def resize(self, button=None):

        rect = self.image.get_allocation()

        # skip if no pixbuf set
        if self.image.pixbuf is None:
            return

        pixbuf_aspect_ratio = float(self.image.pixbuf.props.height) / self.image.pixbuf.props.width
        rect_aspect_ratio = float(rect.height) / rect.width

        if pixbuf_aspect_ratio < rect_aspect_ratio:  # image is wider
            new_width = rect.width
            new_height = int(new_width * pixbuf_aspect_ratio)
        else:
            new_height = rect.height
            new_width = int(new_height / pixbuf_aspect_ratio)

        # scale image
        base_pixbuf = self.image.pixbuf.scale_simple(
            new_width,
            new_height,
            GdkPixbuf.InterpType.BILINEAR
        )

        # set internal image pixbuf to scaled image
        self.image.set_from_pixbuf(base_pixbuf)


class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        self.connect("destroy", Gtk.main_quit)
        self.set_border_width(10)
        self.set_default_size(800, 600)

        print("setting up main window...")
        self.setup_gui()

        self.show_all()

        print("Finished setting up main window!")

    def setup_gui(self):
        print("adding UI elements ...")

        header = Gtk.HeaderBar(title="Instant Comic")
        header.set_subtitle("web Comic viewer")
        header.props.show_close_button = True

        self.set_titlebar(header)

        self.main_box = Gtk.Box()
        self.main_box.set_orientation(Gtk.Orientation.VERTICAL)

        self.add(self.main_box)

        self.comic_box = ComicBox()

        toolbar = Gtk.Box()

        add_button = Gtk.Button("Add")

        toolbar.pack_start(add_button, False, False, 0)

        self.main_box.pack_start(toolbar, False, False, 0)
        self.main_box.pack_start(self.comic_box, True, True, 10)

        print("Finished adding UI elements ...")

    def quit_window(self):
        print("Quiting ...")
        Gtk.main_quit()


def start_gui():
    win = MainWindow()
    Gtk.main()

