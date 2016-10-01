# -*- coding: iso-8859-1 -*-
from gi.repository import Gtk, Gdk

class MessageBox:


    def __init__(self, msg):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("dialogs/message.glade")
        self.window = self.builder.get_object("window1")
        self.builder.connect_signals(self)
        self.lblMessage = self.builder.get_object("lblMessage")
        self.lblMessage.set_markup("<span size='10000' color='red'>"+msg+"</span>")
        Gtk.main()


    #------ callbacks
    def on_accept(self, *args):
        self.window.destroy()

    def on_window1_destroy(self, *args):
        self.window.destroy()
        Gtk.main_quit()
