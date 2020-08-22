import os
from mutagen.id3 import ID3, TIT2, TALB, TPE1, COMM, TDRC, TRCK
from mutagen.id3 import ID3NoHeaderError

import track as t


def expandPath(folderPath: str):
    fileList = []
    for file in os.scandir(folderPath):
        if file.is_file() and file.name.endswith(".mp3"):
            fileList.append(folderPath+"/"+file.name)
    return fileList

def writeID3(track: t.Track):
    f = ID3(track.path)
    f["TIT2"] = TIT2(text=track.data["title"])
    f["TPE1"] = TPE1(text=track.data["artist"])
    f["TALB"] = TALB(text=track.data["album"])
    f["TDRC"] = TDRC(text=track.data["date"])
    f["TRCK"] = TRCK(text=track.data["track"])
    f["COMM::XXX"] = COMM(text=track.data["comment"])
    f.save()

def readID3(path: str):
    try:
        tags = ID3(path)
    except ID3NoHeaderError:
        print("Adding ID3 header")
        tags = ID3()

    dataDict = {"title": u"", "artist": u"", "album": u"", "date": u"", "track": u"", "comment": u""}
    if "TIT2" in tags.keys():
        dataDict["title"] = str(tags["TIT2"])
    if "TALB" in tags.keys():
        dataDict["album"] = str(tags["TALB"])
    if "TPE1" in tags.keys():
        dataDict["artist"] = str(tags["TPE1"])
    if "TRCK" in tags.keys():
        dataDict["track"] = str(tags["TRCK"])
    if "COMM::XXX" in tags.keys():
        dataDict["comment"] = str(tags["COMM::XXX"])
    if "TDRC" in tags.keys():
        dataDict["date"] = str(tags["TDRC"])
    return dataDict

def readFiles(paths: list):
    tracks = []
    for item in paths:
        dataDict = readID3(item)
        dataDict["path"] = item
        tracks.append(t.Track(dataDict))
    return tracks

def writeFiles(trackList: list):
    for track in trackList:
        writeID3(track)
