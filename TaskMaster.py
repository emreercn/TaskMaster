import sqlite3

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QListWidgetItem, QMessageBox
from PyQt5.uic import loadUi
import sys
from PyQt5 import QtCore

class TaskMaster(QMainWindow):
    def __init__(self):
        super(TaskMaster, self).__init__()
        loadUi("main.ui", self)

        self.calendarWidget.selectionChanged.connect(self.calendarDateChanged)  # Takvim üzerinde hareket etmek için
        self.calendarDateChanged() # program açılınca hersey çalıssın
        self.saveButton.clicked.connect(self.saveChanges)
        self.addButton.clicked.connect(self.addNewTask)
        self.silButton.clicked.connect(self.deleteTask)
        self.setWindowTitle('TaskMaster')
        self.setWindowIcon(QIcon("TaskMasterLogo.PNG"))


    def calendarDateChanged(self):
        dateSelected = self.calendarWidget.selectedDate().toPyDate()
        self.updateTaskList(dateSelected)
        

    def updateTaskList(self,date):
        self.tasksListWidget.clear()
        db = sqlite3.connect("data.db")
        cursor = db.cursor()

        query = "SELECT task, completed FROM tasks WHERE date = ?"
        row = (date,)
        results = cursor.execute(query, row).fetchall()
        for result in results:
            item = QListWidgetItem(str(result[0]))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            if result[1] == "YES":
                item.setCheckState(QtCore.Qt.Checked)
            elif result[1] == "NO":
                item.setCheckState(QtCore.Qt.Unchecked)
            self.tasksListWidget.addItem(item)

    def saveChanges(self):
        db = sqlite3.connect("data.db")
        cursor = db.cursor()
        date = self.calendarWidget.selectedDate().toPyDate()

        for i in range(self.tasksListWidget.count()):
            item = self.tasksListWidget.item(i)
            task = item.text()
            if item.checkState() == QtCore.Qt.Checked:
                query = "UPDATE tasks SET completed = 'YES' WHERE task = ? AND date = ?"
            else:
                query = "UPDATE tasks SET completed = 'NO' WHERE task = ? AND date = ?"
            row = (task, date,)
            cursor.execute(query, row)
        db.commit()

        messageBox = QMessageBox()
        messageBox.setText("Değişiklikler Kaydedildi.. ")
        messageBox.setStandardButtons(QMessageBox.Ok)
        messageBox.exec()

    def addNewTask(self):
        db = sqlite3.connect("data.db")
        cursor = db.cursor()

        newTask = str(self.taskLineEdit.text())
        date = self.calendarWidget.selectedDate().toPyDate()

        query = "INSERT INTO tasks(task, completed, date) VALUES (?,?,?)"
        row = (newTask, "NO", date,)

        cursor.execute(query, row)
        db.commit()
        self.updateTaskList(date)
        self.taskLineEdit.clear()

    def deleteTask(self):
        # Seçili öğeyi al
        selected_item = self.tasksListWidget.currentItem()
        if selected_item is not None:
            conn = sqlite3.connect('data.db')
            c = conn.cursor()
            # Seçili öğeyi veritabanından sil
            c.execute("DELETE FROM tasks WHERE task = ?", (selected_item.text(),))
            conn.commit()
            conn.close()
            # ListWidget'dan öğeyi kaldır
            self.tasksListWidget.takeItem(self.tasksListWidget.row(selected_item))
        elif self.silButton.clicked:
            # Seçili öğe yoksa mesaj kutusu göster
            QMessageBox.warning(None, "Uyarı", "Lütfen bir öğe seçin.")


def main():
    uygulama = QApplication(sys.argv)
    window = TaskMaster()
    window.show()
    sys.exit(uygulama.exec())

if __name__ == "__main__":
    main()

    


