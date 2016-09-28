# -*- coding: iso-8859-1 -*-
from gi.repository import Gtk, Gdk

class MainWindow:


    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("mainWindow.glade")
        self.builder.connect_signals(self)

        self.treeview = self.builder.get_object("treeview1")
        select = self.treeview.get_selection()
        select.connect("changed", self.on_tree_selection_changed)

        self.store = Gtk.ListStore(str,str,str)

        self.treeview.set_model(self.store)


        column = Gtk.TreeViewColumn("Notizbücher")
        name = Gtk.CellRendererText()
        besitzer = Gtk.CellRendererText()
        nID = Gtk.CellRendererText()

        column.pack_start(name, True)
        column.pack_start(besitzer, True)
        column.pack_start(nID, True)

        column.add_attribute(name, "text", 0)
        column.add_attribute(besitzer, "text", 1)
        column.add_attribute(nID, "text", 2)
        self.treeview.append_column(column)

        self.store.append(["Testnotebook","biber","4"])
        self.store.append(["Wichtiges Notebook","biber","8"])

        Gtk.main()


    #------ callbacks
    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter != None:
            self.selectedNID = model[treeiter][2]

    def on_mainWindow_destroy(self, *args):
        Gtk.main_quit()
