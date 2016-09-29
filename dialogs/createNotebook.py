# -*- coding: iso-8859-1 -*-
from gi.repository import Gtk, Gdk

class CreateNotebookDialog:


    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("createNotebook.glade")
        self.builder.connect_signals(self)
        self.txtTitel = self.builder.get_object("txtTitel")

        Gtk.main()


    #------ callbacks
    def on_accept(self, *args):
        self.valid = True
        self.titel = self.txtTitel.get_text()
        Gtk.main_quit()

    def on_window1_destroy(self, *args):
        self.valid = False
        Gtk.main_quit()
