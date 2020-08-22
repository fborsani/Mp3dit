class Track:
    def __init__(self, dataDict):
        self.path = dataDict["path"]
        self.filename = self.path[self.path.rfind("/")+1:self.path.rfind(".")]
        self.data = dataDict
        del self.data["path"]

    def update(self, dataDict, preserve: bool, writeEmpty: bool, preserveTrack: bool):
        for key in self.data.keys():
            if (not preserve or (preserve and self.data[key] == "")) and \
                    (writeEmpty or (not writeEmpty and dataDict[key] != "")) and \
                    (not preserveTrack or (preserveTrack and dataDict[key] == "track")):
                self.data[key] = dataDict[key]

    def setTrack(self, tr: str):
        self.data["track"] = tr
