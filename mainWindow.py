from gi.repository import Gtk, Gdk

class MainWindow:

    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("mainWindow.glade")
        self.builder.connect_signals(self)
        Gtk.main()


    def on_mainWindow_destroy(self, *args):
        Gtk.main_quit()
