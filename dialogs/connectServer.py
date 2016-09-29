# -*- coding: iso-8859-1 -*-
from gi.repository import Gtk, Gdk

class ConnectDialog:


    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("connectServer.glade")
        self.builder.connect_signals(self)
        self.txtNutzer = self.builder.get_object("txtNutzer")
        self.txtPasswd = self.builder.get_object("txtPasswd")
        #für password
        self.txtPasswd.set_visibility(False)

        Gtk.main()


    #------ callbacks
    def on_accept(self, *args):
        self.valid = True
        self.user = self.txtNutzer.get_text()
        self.passwd = self.txtPasswd.get_text()
        Gtk.main_quit()

    def on_window1_destroy(self, *args):
        self.valid = False
        Gtk.main_quit()
