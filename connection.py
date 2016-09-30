import requests
import json


class Connection:



    def __init__(self, serverUrl):
        self.url = serverUrl
        self.auth = ""
        

    def get_token(self, nutzer, passwd):
        requestString = self.url + "/gettoken"
        r = requests.post(requestString,
                          data={'nutzer': nutzer, 'passwd': passwd})

        if r.status_code is not 200:
            return -100

        decoded = json.loads(r.text)
        # fehler?
        if 'ok' in decoded:
            return decoded["ok"]

        self.auth = decoded["token"]
        return 0

    def save_note(self, nID, titel, beschreibung, prio):
        requestString = self.url + "/savenotes"
        r = requests.post(requestString,
                          data={'auth': self.auth, 'nID': nID, 'titel': titel, 'beschreibung': beschreibung, 'prio': prio})

        if r.status_code is not 200:
            return -100

        decoded = json.loads(r.text)
        # fehler?
        if 'ok' in decoded:
            if decoded["ok"] == "ok":
                return 0
            else:
                return decoded["ok"]

    def create_notebook(self, titel):
        requestString = self.url + "/createnotebook"
        r = requests.post(requestString,
                          data={'auth': self.auth, 'titel': titel})

        if r.status_code is not 200:
            return -100

        decoded = json.loads(r.text)
        # fehler?
        if 'ok' in decoded:
            if decoded["ok"] == "ok":
                return 0
            else:
                return decoded["ok"]

    def add_user(self, name,passwd):
        requestString = self.url + "/adduser"
        r = requests.post(requestString,
                          data={'auth': self.auth, 'name': name, 'passwd': passwd})

        if r.status_code is not 200:
            return -100

        decoded = json.loads(r.text)
        # fehler?
        if 'ok' in decoded:
            if decoded["ok"] == "ok":
                return 0
            else:
                return decoded["ok"]

    def update_note(self, nID, titel, beschreibung, prio, notizID):
        requestString = self.url + "/savenotes"
        r = requests.post(requestString,
                          data={'auth': self.auth, 'nID': nID, 'titel': titel, 'beschreibung': beschreibung, 'prio': prio, 'notizID': notizID})

        if r.status_code is not 200:
            return -100

        decoded = json.loads(r.text)
        # fehler?
        if 'ok' in decoded:
            if decoded["ok"] == "ok":
                return 0
            else:
                return decoded["ok"]

    def get_notes(self, nID):
        requestString = self.url + "/notes"
        r = requests.post(requestString,
                          data={'auth':self.auth, 'nID':nID})

        if r.status_code is not 200:
            return -100

        decoded = json.loads(r.text)
        # fehler?
        if 'ok' in decoded:
            return decoded["ok"]

        return decoded

    def get_notebooks(self):
        requestString = self.url + "/notebooks"
        r = requests.post(requestString,
                          data={'auth':self.auth})

        if r.status_code is not 200:
            return -100

        decoded = json.loads(r.text)
        # fehler?
        if 'ok' in decoded:
            return decoded["ok"]

        return decoded
