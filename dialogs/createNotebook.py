# -*- coding: iso-8859-1 -*-
from gi.repository import Gtk, Gdk

class CreateNotebookDialog:


    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("dialogs/createNotebook.glade")
        self.window = self.builder.get_object("window1")
        self.builder.connect_signals(self)
        self.txtTitel = self.builder.get_object("txtTitel")
        self.valid = False
        self.titel = ""

        Gtk.main()


    #------ callbacks
    def on_accept(self, *args):
        self.valid = True
        self.titel = self.txtTitel.get_text()
        self.window.destroy()

    def on_window1_destroy(self, *args):
        self.window.destroy()
        Gtk.main_quit()
