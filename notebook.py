import note

class NoteBook(object):
    """docstring for NoteBook."""
    def __init__(self, titel):
        self.titel = titel
        # key: noteID , value: note objekt
        self.noteDict = {}

    def add_note(self,note):
        #check if note is not in dict


        #add note
        self.noteDict[note.notizID] = note
        
