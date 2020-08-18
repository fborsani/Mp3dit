import re

class FilenameRegex:
    def __init__(self, regexStr: str):
        self.tagOpen = "<:"
        self.tagClose = ":>"
        self.substrings = re.split("("+self.tagOpen+"|"+self.tagClose+")", regexStr)

    def getData(self, filename: str):
        try:
            dataDict = {"title": u"", "artist": u"", "album": u"", "date": u"", "track": u"", "comment": u""}
            fn = filename

            delimiter = False
            currTag = ""

            if self.substrings[0] != self.tagOpen:
                idx = fn.find(self.substrings[0])
                if idx != -1:
                    fn = fn[idx+len(self.substrings[0]):]
                    self.substrings.pop(0)
                else:
                    return dataDict

            if self.substrings[-1] != self.tagClose:
                idx = fn.rfind(self.substrings[-1])
                if idx != -1:
                    fn = fn[:idx]
                    self.substrings.pop(-1)
                else:
                    return dataDict

            for i in range(0, len(self.substrings), 1):
                if self.substrings[i] == self.tagOpen:
                    currTag = self.substrings[i+1]
                    delimiter = True
                elif self.substrings[i] == self.tagClose:
                    delimiter = False
                elif not delimiter and self.substrings[i] != "":
                    idx = fn.find(self.substrings[i])
                    if idx != -1 and currTag in dataDict.keys():
                        dataDict[currTag] = (fn[:idx])
                        fn = fn[idx+len(self.substrings[i]):]

            if not delimiter and fn != "" and dataDict[currTag] == "":
                dataDict[currTag] = fn

            return dataDict
        except IndexError:
            raise
