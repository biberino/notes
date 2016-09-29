# -*- coding: iso-8859-1 -*-
from gi.repository import Gtk, Gdk

class CreateNoteDialog:


    def __init__(self,titel,notiz):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("dialogs/createNote.glade")
        self.window = self.builder.get_object("window1")
        self.builder.connect_signals(self)
        self.txtTitel = self.builder.get_object("txtTitel")
        self.txtBeschreibung = self.builder.get_object("txtBeschreibung")
        self.txtBuffer = self.txtBeschreibung.get_buffer()

        self.txtTitel.set_text(titel)
        self.txtBuffer.set_text(notiz)
        self.valid = False
        self.titel = ""
        self.beschreibung = ""
        Gtk.main()


    #------ callbacks
    def on_accept(self, *args):
        self.valid = True
        self.titel = self.txtTitel.get_text()
        start_iter = self.txtBuffer.get_start_iter()
        end_iter = self.txtBuffer.get_end_iter()
        self.beschreibung = self.txtBuffer.get_text(start_iter, end_iter, True)
        self.window.destroy()

    def on_window1_destroy(self, *args):
        self.window.destroy()
        Gtk.main_quit()
