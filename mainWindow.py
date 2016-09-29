# -*- coding: iso-8859-1 -*-
from gi.repository import Gtk, Gdk
from dialogs import createNote
from dialogs import createNotebook
from dialogs import connectServer
import connection


class MainWindow:



    def __init__(self):

        self.conn = connection.Connection("https://a.febijo.de/node")

        self.builder = Gtk.Builder()
        self.builder.add_from_file("mainWindow.glade")
        self.builder.connect_signals(self)

        self.treeview = self.builder.get_object("treeview1")
        self.comboNotebooks = self.builder.get_object("comboNotebooks")
        select = self.treeview.get_selection()
        select.connect("changed", self.on_tree_selection_changed)

        self.store = Gtk.ListStore(str,str,str)

        self.treeview.set_model(self.store)

        self.combo_store = Gtk.ListStore(str)
        #self.comboNotebooks.set_model=self.combo_store


        column = Gtk.TreeViewColumn("Notizen")
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



    def get_notebooks_from_server(self):
        res = self.conn.get_notebooks()
        print (res)
        if res < 0:
            print ("Problem")
            return

        self.comboNotebooks.remove_all()
        for i in range(0,len(res)):
            print (res[i]["name"])
            self.comboNotebooks.append_text(res[i]["name"])



    #------ callbacks

    def on_comboboxtextentry_changed(self, *args):
        print (self.comboNotebooks.get_active_text())


    def on_buttonServer_clicked(self,*args):
        c = connectServer.ConnectDialog()
        if c.valid:
            res = self.conn.get_token(c.user, c.passwd)
            if res is -100:
                print ("Verbindung ging schief")
                return
            if res < 0:
                print (res)
                print("Vielleicht falsche Anmeldeinfos?")
                return
            #ab hier müsste das token da sein
            self.get_notebooks_from_server()



    def on_buttonNotebook_clicked(self,*args):
        n = createNotebook.CreateNotebookDialog()
        print (n.valid)
        print (n.titel)


    def on_buttonNoteNew_clicked(self,*args):
        n = createNote.CreateNoteDialog("","")
        print (n.valid)
        print (n.titel)
        print (n.beschreibung)

    def on_buttonNoteUpdate_clicked(self,*args):
        n = createNote.CreateNoteDialog("","")
        print (n.valid)
        print (n.titel)
        print (n.beschreibung)




    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter != None:
            self.selecetedNID = model[treeiter][2]

    def on_mainWindow_destroy(self, *args):
        Gtk.main_quit()
