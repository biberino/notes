# -*- coding: iso-8859-1 -*-
from gi.repository import Gtk, Gdk
from dialogs import createNote
from dialogs import createNotebook
from dialogs import connectServer
from dialogs import showMsg
from user import user
import ConfigParser
import os
#import connection
import note
import json

from thread import start_new_thread


class MainWindow:

    def __init__(self):
        self.user = user.User()
        #self.conn = connection.Connection("https://a.febijo.de/node")
        # parse config file
        self.currentUser = ""
        self.user.readConfig()

        # welcome message
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

        if self.user.autologin:
            self.get_notebooks_from_server()
            self.display_current_user(self.user.name)
        Gtk.main()

    def readConfig(self):
        # TODO remove
        pass
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
        res = self.user.get_notebooks(self.comboNotebooks)
        if res is 0:
            self.say("Alle Notizbücher heruntergeladen!")
        self.spinnerServer.stop()
    #------ callbacks

    def on_comboboxtextentry_changed(self, *args):
        start_new_thread(self.get_notes_thread, (None,))

    def test(self):
        with open('test.txt', 'w') as outfile:
            json.dump(self.notesDict[self.selectedTitle].__dict__, outfile)

    def get_notes_thread(self, *args):
        # print (self.comboNotebooks.get_active_text())
        # print (self.comboNotebooks.get_active())
        self.spinnerServer.start()
        res = self.user.get_notes(self.comboNotebooks,
                             self.spinnerServer, self.store)
        if res is 0:
            self.say("Alle Notizen aus <span color='red'>" +
                     self.comboNotebooks.get_active_text() + "</span> geladen!")
        self.spinnerServer.stop()

    def on_buttonServer_clicked(self, *args):
        res = self.user.authenticate()
        if res is 1:
            return
        self.get_notebooks_from_server()
        # speichere auth token ab

        self.user.writeConfig()
        #print (self.conn.auth)
        # create file
        #cfgfile = open("default.cfg", 'w')

        #conf = ConfigParser.ConfigParser()
        # conf.add_section("a")
        #conf.set("a", "auth", self.conn.auth)
        #conf.set("a", "name", c.user)
        # conf.write(cfgfile)
        # cfgfile.close()
        self.display_current_user(user.name)
        #self.currentUser = c.user

    def display_current_user(self, user):
        s = "Angemeldet: <span color='green'>" + user + "</span>"
        self.lblUser.set_markup(s)

    def say(self, msg):
        message = "<span size='10000' color='blue'>" + msg + "</span>"
        self.lblBottom.set_markup(message)

    def on_buttonNotebook_clicked(self, *args):
        res = self.user.add_notebook()
        if res is 0:
            self.get_notebooks_from_server()

    def on_buttonNoteNew_clicked(self, *args):
        res = self.user.create_new_note()
        if res is 0:
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
        res = self.user.update_note()
        if res is 0:
            # alles ok
            print ("Erfolgreich")
            self.on_comboboxtextentry_changed()

    def on_tree_selection_changed(self, selection):
        self.user.update_selected_note(selection, self.lblTitle, self.lblBeschreibung)


    def on_mainWindow_destroy(self, *args):
        Gtk.main_quit()
