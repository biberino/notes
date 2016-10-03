# -*- coding: iso-8859-1 -*-
from gi.repository import Gtk, Gdk
from dialogs import createNote
from dialogs import createNotebook
from dialogs import connectServer
from dialogs import showMsg
import ConfigParser
import os
import connection
import note

from thread import start_new_thread


class MainWindow:

    def __init__(self):
        self.conn = connection.Connection("https://a.febijo.de/node")
        # parse config file
        self.currentUser = ""
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
        self.lblUser = self.builder.get_object("lblUser")
        self.spinnerServer = self.builder.get_object("spinnerServer")
        self.lblBottom = self.builder.get_object("lblBottom")

        background_color_basic = '#FCFFA5'
        selected_color = '#3F3FFF'
        self.modifyBackgroundColor(
            self.lblBeschreibung, background_color_basic, Gtk.StateFlags.NORMAL)
        self.modifyBackgroundColor(
            self.treeview, background_color_basic, Gtk.StateFlags.NORMAL)
        self.modifyForegroundColor(
            self.treeview, selected_color, Gtk.StateFlags.SELECTED)
        self.modifyForegroundColor(
            self.lblBeschreibung, selected_color, Gtk.StateFlags.SELECTED)

        select = self.treeview.get_selection()
        select.connect("changed", self.on_tree_selection_changed)

        self.store = Gtk.ListStore(str, str)

        self.treeview.set_model(self.store)

        # self.comboNotebooks.set_model=self.combo_store

        columnN = Gtk.TreeViewColumn("Notiz")
        columnP = Gtk.TreeViewColumn("Priorität")
        name = Gtk.CellRendererText()
        prio = Gtk.CellRendererText()
        # nID = Gtk.CellRendererText()

        columnN.pack_start(name, True)
        columnP.pack_start(prio, True)
        # column.pack_start(nID, True)

        columnN.add_attribute(name, "text", 0)
        columnP.add_attribute(prio, "text", 1)
        # column.add_attribute(nID, "text", 2)
        self.treeview.append_column(columnN)
        self.treeview.append_column(columnP)

        if self.autologin:
            self.get_notebooks_from_server()
            self.display_current_user(self.currentUser)
        Gtk.main()

    def readConfig(self):
        self.autologin = False
        if not os.path.isfile('default.cfg'):
            return
        config = ConfigParser.ConfigParser()
        config.read("default.cfg")
        self.conn.auth = config.get("a", "auth")
        self.currentUser = config.get("a", "name")
        self.autologin = True

    def get_notebooks_from_server(self):
        start_new_thread(self.get_notebooks_thread_caller, (None,))

    def get_notebooks_thread_caller(self, *args):
        self.spinnerServer.start()
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
        self.say("Alle Notizbücher heruntergeladen!")
        self.spinnerServer.stop()
    #------ callbacks

    def on_comboboxtextentry_changed(self, *args):
        start_new_thread(self.get_notes_thread, (None,))

    def get_notes_thread(self, *args):
        # print (self.comboNotebooks.get_active_text())
        # print (self.comboNotebooks.get_active())
        self.spinnerServer.start()
        nID = self.notebookDict[(self.comboNotebooks.get_active())]
        self.currentNID = nID
        res = self.conn.get_notes(nID)
        if res is -100:
            print ("No Server connection possible")
            showMsg.MessageBox(
                "Es konnte keine Verbindung zum Server hergestellt werden")
            self.spinnerServer.stop()
            return
        if res < 0:
            print (res)
            print ("Error")
            self.spinnerServer.stop()
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
            # self.notesDict[res[i]["titel"]] = res[i]["beschreibung"]
            self.notesDict[res[i]["titel"]] = a
        self.say("Alle Notizen aus <span color='red'>" +
                 self.comboNotebooks.get_active_text() + "</span> geladen!")
        self.spinnerServer.stop()

    def on_buttonServer_clicked(self, *args):
        c = connectServer.ConnectDialog()
        if c.valid:
            res = self.conn.get_token(c.user, c.passwd)
            if res is -100:
                print ("Verbindung ging schief")
                showMsg.MessageBox(
                    "Es konnte keine Verbindung zum Server hergestellt werden")
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
            conf.set("a", "name", c.user)
            conf.write(cfgfile)
            cfgfile.close()
            self.display_current_user(c.user)
            self.currentUser = c.user

    def display_current_user(self, user):
        s = "Angemeldet: <span color='green'>" + user + "</span>"
        self.lblUser.set_markup(s)

    def say(self, msg):
        message = "<span size='10000' color='blue'>" + msg + "</span>"
        self.lblBottom.set_markup(message)

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
            showMsg.MessageBox(
                "Wähle ein Notizbuch aus bevor du eine Notiz erstellst")
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

    def modifyBackgroundColor(self, w, cHex, stateFlag):
        rgba = Gdk.RGBA()
        rgba.parse(cHex)
        w.override_background_color(stateFlag, rgba)

    def modifyForegroundColor(self, w, cHex, stateFlag):
        rgba = Gdk.RGBA()
        rgba.parse(cHex)
        w.override_color(stateFlag, rgba)

    def on_buttonNoteUpdate_clicked(self, *args):
        if self.currentNID is -1:
            showMsg.MessageBox(
                "Wähle ein Notizbuch aus bevor du Notizen änderst")
            return
        if self.selecetedTitle is "Willkommen":
            showMsg.MessageBox(
                "Wähle eine Notiz aus, die du ändern möchtest")
            return

        # set the currentNID and notizID here, before calling the window
        notebookID = self.currentNID
        notizIDlocal = self.notesDict[self.selecetedTitle].notizID
        beschr = self.notesDict[self.selecetedTitle].beschreibung
        n = createNote.CreateNoteDialog(self.selecetedTitle, beschr)

        if not n.valid:
            return

        res = self.conn.update_note(
            notebookID, n.titel, n.beschreibung, "1", notizIDlocal)
        if res is -100:
            print ("Fehler beim Verbinden mitm Sever")
            showMsg.MessageBox(
                "Es konnte keine Verbindung zum Server hergestellt werden")
            return
        if res < 0:
            print (res)
            return
        # alles ok
        print ("Erfolgreich")
        self.on_comboboxtextentry_changed()

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        self.selecetedTitle = "Willkommen"
        self.notesDict["Willkommen"] = note.Note(
            "Willkommen", self.welcome, "1", 999)

        if treeiter != None:
            self.selecetedTitle = model[treeiter][0]  # name

        self.lblTitle.set_markup(
            "<span size='22800' color='grey'> " + self.selecetedTitle + "</span>")
        self.lblBeschreibung.set_markup(
            "<span size='12800'>" + self.notesDict[self.selecetedTitle].beschreibung + "</span>")

    def on_mainWindow_destroy(self, *args):
        Gtk.main_quit()
