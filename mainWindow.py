# -*- coding: iso-8859-1 -*-
from gi.repository import Gtk, Gdk
from dialogs import createNote
from dialogs import createNotebook
from dialogs import connectServer
import ConfigParser
import os
import connection
import note


class MainWindow:

    def __init__(self):
        self.conn = connection.Connection("https://a.febijo.de/node")
        # parse config file
        self.readConfig()

        # key: index in combobox, value: id
        self.notebookDict = {}

        # key: title of note, value: noteobject
        self.notesDict = {}
        # welcome message
        self.welcome = "Melde dich an und wähle ein Notizbuch um loszulegen :)"
        # saves server responses for later use
        self.lastNotesResponse = ""

        self.currentNID = -1


        self.builder = Gtk.Builder()
        self.builder.add_from_file("mainWindow.glade")
        self.builder.connect_signals(self)

        self.treeview = self.builder.get_object("treeview1")
        self.comboNotebooks = self.builder.get_object("comboNotebooks")
        self.lblTitle = self.builder.get_object("lblTitle")
        self.lblBeschreibung = self.builder.get_object("lblBeschreibung")

        select = self.treeview.get_selection()
        select.connect("changed", self.on_tree_selection_changed)

        self.store = Gtk.ListStore(str, str)

        self.treeview.set_model(self.store)

        # self.comboNotebooks.set_model=self.combo_store

        column = Gtk.TreeViewColumn("Notizen")
        name = Gtk.CellRendererText()
        besitzer = Gtk.CellRendererText()
        #nID = Gtk.CellRendererText()

        column.pack_start(name, True)
        column.pack_start(besitzer, True)
        #column.pack_start(nID, True)

        column.add_attribute(name, "text", 0)
        column.add_attribute(besitzer, "text", 1)
        #column.add_attribute(nID, "text", 2)
        self.treeview.append_column(column)

        if self.autologin:
            self.get_notebooks_from_server()
        Gtk.main()

    def readConfig(self):
        self.autologin = False
        if not os.path.isfile('default.cfg'):
            return
        config = ConfigParser.ConfigParser()
        config.read("default.cfg")
        self.conn.auth = config.get("a", "auth")
        self.autologin = True


    def get_notebooks_from_server(self):
        res = self.conn.get_notebooks()
        print (res)
        if res < 0:
            print ("Problem")
            return

        self.comboNotebooks.remove_all()
        self.notebookDict.clear()
        for i in range(0, len(res)):
            print (res[i]["name"])
            self.comboNotebooks.append_text(res[i]["name"])
            self.notebookDict[i] = res[i]["id"]

    #------ callbacks

    def on_comboboxtextentry_changed(self, *args):
        #print (self.comboNotebooks.get_active_text())
        #print (self.comboNotebooks.get_active())
        nID = self.notebookDict[(self.comboNotebooks.get_active())]
        self.currentNID = nID
        res = self.conn.get_notes(nID)
        if res is -100:
            print ("No Server connection possible")
            return
        if res < 0:
            print (res)
            print ("Error")
            return
        # alles ok
        self.lastNotesResponse = res
        self.store.clear()
        self.notesDict.clear()
        for i in range(0, len(res)):
            # construct new object
            a = note.Note(res[i]["titel"], res[i]["beschreibung"], str(
                res[i][u'priorit\xe4t']), res[i]["id"])
            self.store.append([res[i]["titel"], str(res[i][u'priorit\xe4t'])])
            #self.notesDict[res[i]["titel"]] = res[i]["beschreibung"]
            self.notesDict[res[i]["titel"]] = a

    def on_buttonServer_clicked(self, *args):
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
            # ab hier müsste das token da sein
            self.get_notebooks_from_server()
            # speichere auth token ab

            print (self.conn.auth)
            # create file
            cfgfile = open("default.cfg", 'w')

            conf = ConfigParser.ConfigParser()
            conf.add_section("a")
            conf.set("a", "auth", self.conn.auth)
            conf.write(cfgfile)
            cfgfile.close()

    def on_buttonNotebook_clicked(self, *args):
        n = createNotebook.CreateNotebookDialog()
        if not n.valid:
            return
        print (n.titel)
        res = self.conn.create_notebook(n.titel)
        if res is 0:
            print("Erfolgreich")
        else:
            print (res)
        self.get_notebooks_from_server()

    def on_buttonNoteNew_clicked(self, *args):
        if self.currentNID is -1:
            return
        n = createNote.CreateNoteDialog("", "")
        # TODO add custom priority
        prio = 1

        if not n.valid:
            return

        res = self.conn.save_note(
            self.currentNID, n.titel, n.beschreibung, prio)
        if res is 0:
            print ("Erfolgreich")
        else:
            print (res)
        self.on_comboboxtextentry_changed()

    def on_buttonNoteUpdate_clicked(self, *args):
        if self.currentNID is -1:
            return
        if self.selecetedTitle is "Willkommen":
            return

        beschr = self.notesDict[self.selecetedTitle].beschreibung
        n = createNote.CreateNoteDialog(self.selecetedTitle, beschr)

        if not n.valid:
            return

        res = self.conn.update_note(self.currentNID, n.titel, n.beschreibung, "1", self.notesDict[
                                    self.selecetedTitle].notizID)
        if res is -100:
            print ("Fehler beim Verbinden mitm Sever")
            return
        if res < 0:
            print (res)
            return
        # alles ok
        print ("Erfolgreich")
        self.on_comboboxtextentry_changed()

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        self.selecetedTitle = "Wilkommen"
        self.notesDict["Wilkommen"] = note.Note(
            "Wilkommen", self.welcome, "1", 999)

        if treeiter != None:
            self.selecetedTitle = model[treeiter][0]  # name

        self.lblTitle.set_markup(
            "<span size='22800'> " + self.selecetedTitle + "</span>")
        self.lblBeschreibung.set_markup(
            "<span size='12800'>" + self.notesDict[self.selecetedTitle].beschreibung + "</span>")

    def on_mainWindow_destroy(self, *args):
        Gtk.main_quit()
