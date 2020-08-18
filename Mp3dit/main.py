import random
import sys

import filenameRegex as rgx
import utils as u
from mainWindow import Ui_MainWindow


class NumericTableWidgetItem (QTableWidgetItem):
    def __init__(self, value):
        super(NumericTableWidgetItem, self).__init__(str(value))

    def __lt__(self, other):
        if isinstance(other, NumericTableWidgetItem):
            myData = self.data(Qt.EditRole)
            otherData = other.data(Qt.EditRole)
            if myData == "":
                return True
            elif otherData == "":
                return False
            else:
                return int(myData) < int(otherData)
        else:
            return Qt.QtGui.QTableWidgetItem.__lt__(self, other)


class MainWindow(QMainWindow):
    def __getFiles(self, fs: list, isDir: bool, append: bool):
        if isDir:
            if append:
                self.paths += u.expandPath(fs[0])
            else:
                self.paths = u.expandPath(fs[0])
        else:
            if append:
                self.paths += fs
            else:
                self.paths = fs

        self.__fillTable()

    def __fillTable(self, useLocal: bool = False):
        self.__setUiToDefault()

        if not useLocal:
            self.tracks.clear()
            self.tracks = u.readFiles(self.paths)

        count = 1
        for tr in self.tracks:
            self.ui.tableItems.insertRow(self.ui.tableItems.rowCount())
            row = self.ui.tableItems.rowCount()-1

            self.ui.tableItems.setItem(row, 0, NumericTableWidgetItem(count))
            self.ui.tableItems.setItem(row, 1, QTableWidgetItem(tr.filename))
            self.ui.tableItems.setItem(row, 2, QTableWidgetItem(tr.data["title"]))
            self.ui.tableItems.setItem(row, 3, QTableWidgetItem(tr.data["artist"]))
            self.ui.tableItems.setItem(row, 4, QTableWidgetItem(tr.data["album"]))
            self.ui.tableItems.setItem(row, 5, NumericTableWidgetItem(tr.data["track"]))
            self.ui.tableItems.setItem(row, 6, QTableWidgetItem(tr.data["date"]))
            self.ui.tableItems.setItem(row, 7, QTableWidgetItem(tr.data["comment"]))
            count += 1
        self.ui.tableItems.sortItems(0)

    def __moveItems(self, idx: int):
        model = self.ui.tableItems.model()
        for index in self.ui.tableItems.selectionModel().selectedRows():
            row = index.row()
            tr = int(model.data(model.index(row, 0)))-1
            self.tracks.insert(tr+idx, self.tracks.pop(tr))
        self.__fillTable(True)

    def __shuffle(self):
        random.shuffle(self.tracks)
        self.__fillTable(True)

    def __apply(self):
        date = ""
        if self.ui.checkSetDate.isChecked():
            date = self.ui.dateYear.text()

        track = ""
        if self.ui.checkSetTrack.isChecked():
            track = self.ui.spinTrack.text()

        userEntries = {
            "title": self.ui.lineTitle.text(),
            "artist": self.ui.lineArtist.text(),
            "album": self.ui.lineAlbum.text(),
            "date": date,
            "track": track,
            "comment": self.ui.lineComment.text()
        }

        preserve = self.ui.checkPreserve.isChecked()
        writeEmpty = self.ui.checkWriteEmpty.isChecked()
        model = self.ui.tableItems.model()
        selectionModel = self.ui.tableItems.selectionModel()
        useFilename = self.ui.checkUseFilename.isChecked()
        posToTrack = self.ui.checkNumtoTrack.isChecked()
        regexStr = self.ui.lineFilenameRegex.text()
        updateList = []

        if len(selectionModel.selectedRows(0)) == 0 or (useFilename and (not regexStr or regexStr == "")):
            return
        try:
            for row in range(0, model.rowCount(), 1):
                dataDict = {"title": u"", "artist": u"", "album": u"", "date": u"", "track": u"", "comment": u""}
                idx = int(model.index(row, 0).data())
                preserveTrack = False

                if selectionModel.isSelected(model.index(row, 0)):

                    if useFilename:
                        filename = model.index(row, 1).data()
                        regex = rgx.FilenameRegex(regexStr)
                        dataDict = regex.getData(filename)

                    if posToTrack:
                        self.tracks[idx-1].setTrack(str(idx))
                        preserveTrack = True

                    for key in dataDict.keys():
                        if dataDict[key] == "" and userEntries[key] != "":
                            dataDict[key] = userEntries[key]

                    self.tracks[idx-1].update(dataDict, preserve, writeEmpty, preserveTrack)
                    updateList.append(self.tracks[idx-1])

            u.writeFiles(updateList)
            self.__fillTable()
        except IndexError:
            self.ui.lineFilenameRegex.setText("Malformed regex!")

    def __setUiToDefault(self):
        self.ui.checkSetTrack.setChecked(False)
        self.ui.checkSetDate.setChecked(False)
        self.ui.checkUseFilename.setChecked(False)
        self.ui.spinTrack.setEnabled(False)
        self.ui.dateYear.setEnabled(False)
        self.ui.lineFilenameRegex.setEnabled(False)

        self.ui.lineAlbum.setText("")
        self.ui.lineTitle.setText("")
        self.ui.lineArtist.setText("")
        self.ui.lineComment.setText("")
        self.ui.lineFilenameRegex.setText("")

        self.ui.tableItems.setRowCount(0)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.paths = []
        self.tracks = []

        self.fileDialog = QFileDialog(self)
        self.folderDialog = QFileDialog(self)

        self.fileDialog.setFileMode(QFileDialog.ExistingFiles)
        self.fileDialog.setAcceptMode(QFileDialog.AcceptOpen)
        self.folderDialog.setFileMode(QFileDialog.Directory)
        self.folderDialog.setAcceptMode(QFileDialog.AcceptOpen)

        self.ui.actionFiles.triggered.connect(lambda: self.fileDialog.show())
        self.ui.actionFolder.triggered.connect(lambda: self.folderDialog.show())
        self.fileDialog.accepted.connect(lambda: self.__getFiles(self.fileDialog.selectedFiles(), False, False))
        self.folderDialog.accepted.connect(lambda: self.__getFiles(self.folderDialog.selectedFiles(), True, False))

        self.ui.btnSelectAll.pressed.connect(lambda: self.ui.tableItems.selectAll())
        self.ui.btnDeselect.pressed.connect(lambda: self.ui.tableItems.clearSelection())
        self.ui.btnMovUp.pressed.connect(lambda: self.__moveItems(1))
        self.ui.btnMovDwn.pressed.connect(lambda: self.__moveItems(-1))
        self.ui.btnShuffle.pressed.connect(lambda: self.__shuffle())

        self.ui.checkSetTrack.pressed.connect(lambda: self.ui.spinTrack.setEnabled(not self.ui.checkSetTrack.isChecked()))
        self.ui.checkSetDate.pressed.connect(lambda: self.ui.dateYear.setEnabled(not self.ui.checkSetDate.isChecked()))
        self.ui.checkUseFilename.pressed.connect(lambda: self.ui.lineFilenameRegex.setEnabled(not self.ui.checkUseFilename.isChecked()))

        # self.ui.tableItems.selectionModel().selectionChanged.connect(lambda: self.__updateInputFields())
        self.ui.btnApply.pressed.connect(lambda: self.__apply())

        self.__setUiToDefault()


def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
