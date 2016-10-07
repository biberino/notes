# -*- coding: iso-8859-1 -*-

import connection
import ConfigParser
from dialogs import createNote
from dialogs import createNotebook
from dialogs import connectServer
from dialogs import showMsg
import os
import note


class User():

    def __init__(self):
        self.conn = connection.Connection("https://a.febijo.de/node")
        self.autologin = False
        # key: index in combobox, value: id
        self.notebookDict = {}

        # key: title of note, value: noteobject
        self.notesDict = {}
        self.currentNID = -1
        self.selectedTitle = "Willkommen"
        self.welcome = "Melde dich an und wähle ein Notizbuch um loszulegen :)"

    def update_selected_note(self, selection, lblTitle, lblBeschreibung):
        model, treeiter = selection.get_selected()
        self.selectedTitle = "Willkommen"
        self.notesDict["Willkommen"] = note.Note(
            "Willkommen", self.welcome, "1", 999)

        if treeiter != None:
            self.selectedTitle = model[treeiter][0]  # name
            # self.test()

        lblTitle.set_markup(
            "<span size='22800' color='grey'> " + self.selectedTitle + "</span>")
        lblBeschreibung.set_markup(
            "<span size='12800'>" + self.notesDict[self.selectedTitle].beschreibung + "</span>")

    def update_note(self):
        if self.currentNID is -1:
            showMsg.MessageBox(
                "Wähle ein Notizbuch aus bevor du Notizen änderst")
            return 1
        if self.selectedTitle is "Willkommen":
            showMsg.MessageBox(
                "Wähle eine Notiz aus, die du ändern möchtest")
            return 1

        # set the currentNID and notizID here, before calling the window
        notebookID = self.currentNID
        notizIDlocal = self.notesDict[self.selectedTitle].notizID
        beschr = self.notesDict[self.selectedTitle].beschreibung
        n = createNote.CreateNoteDialog(self.selectedTitle, beschr)

        if not n.valid:
            return 1

        res = self.conn.update_note(
            notebookID, n.titel, n.beschreibung, "1", notizIDlocal)
        if res is -100:
            print ("Fehler beim Verbinden mitm Sever")
            showMsg.MessageBox(
                "Es konnte keine Verbindung zum Server hergestellt werden")
            return 1
        if res < 0:
            print (res)
            return 1
        return 0

    def create_new_note(self):
        if self.currentNID is -1:
            showMsg.MessageBox(
                "Wähle ein Notizbuch aus bevor du eine Notiz erstellst")
            return 1
        n = createNote.CreateNoteDialog("", "")
        # TODO add custom priority
        prio = 1

        if not n.valid:
            return 1

        res = self.conn.save_note(
            self.currentNID, n.titel, n.beschreibung, prio)
        if res is 0:
            print ("Erfolgreich")
            return 0
        else:
            print (res)
            return 1

    def get_notes(self, combo, spinner, store):
        self.currentNID = self.notebookDict[(combo.get_active())]
        res = self.conn.get_notes(self.currentNID)
        if res is -100:
            print ("No Server connection possible")
            showMsg.MessageBox(
                "Es konnte keine Verbindung zum Server hergestellt werden")
            spinner.stop()
            return 1
        if res < 0:
            print (res)
            print ("Error")
            spinner.stop()
            return 1
        # alles ok

        store.clear()
        self.notesDict.clear()
        for i in range(0, len(res)):
            # construct new object
            a = note.Note(res[i]["titel"], res[i]["beschreibung"], str(
                res[i][u'priorit\xe4t']), res[i]["id"])
            #format date from database
            created = res[i]["angelegt"]
            created = created.split("T")[0]
            store.append([res[i]["titel"], str(
                res[i][u'priorit\xe4t']), created])
            # self.notesDict[res[i]["titel"]] = res[i]["beschreibung"]
            self.notesDict[res[i]["titel"]] = a
        # self.say("Alle Notizen aus <span color='red'>" +
        #         self.comboNotebooks.get_active_text() + "</span> geladen!")
        return 0

    def get_notebooks(self, combo):
        res = self.conn.get_notebooks()
        print (res)
        if res < 0:
            print ("Problem")
            return 1

        combo.remove_all()
        self.notebookDict.clear()
        for i in range(0, len(res)):
            print (res[i]["name"])
            combo.append_text(res[i]["name"])
            self.notebookDict[i] = res[i]["id"]
        #self.say("Alle Notizbücher heruntergeladen!")
        return 0

    def add_notebook():
        n = createNotebook.CreateNotebookDialog()
        if not n.valid:
            return 1
        print (n.titel)
        res = self.conn.create_notebook(n.titel)
        if res is 0:
            print("Erfolgreich")
            return 0
        else:
            print (res)

    def authenticate(self):
        c = connectServer.ConnectDialog()
        if c.valid:
            res = self.conn.get_token(c.user, c.passwd)
            if res is -100:
                print ("Verbindung ging schief")
                showMsg.MessageBox(
                    "Es konnte keine Verbindung zum Server hergestellt werden")
                return 1
            if res < 0:
                print (res)
                print("Vielleicht falsche Anmeldeinfos?")
                return 1
            self.name = c.user
            return 0
        return 1

    def readConfig(self):
        self.autologin = False
        if not os.path.isfile('default.cfg'):
            return
        config = ConfigParser.ConfigParser()
        config.read("default.cfg")
        self.conn.auth = config.get("a", "auth")
        self.name = config.get("a", "name")
        self.autologin = True

    def writeConfig(self):
        cfgfile = open("default.cfg", 'w')
        #self.name = username
        conf = ConfigParser.ConfigParser()
        conf.add_section("a")
        conf.set("a", "auth", self.conn.auth)
        conf.set("a", "name", self.name)
        conf.write(cfgfile)
        cfgfile.close()
