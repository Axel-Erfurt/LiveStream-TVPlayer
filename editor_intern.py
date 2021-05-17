#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import shutil
import csv
from PyQt5.QtCore import Qt, QDir, QModelIndex, QVariant, QSize, QFile
from PyQt5.QtWidgets import (QMainWindow, QTableWidget, QApplication, QLineEdit, QWidget, QTableWidgetItem,  
                             QFileDialog, QAbstractItemView, QMessageBox, QToolButton, QSizePolicy)
from PyQt5.QtGui import QIcon, QKeySequence


class Viewer(QMainWindow):
    def __init__(self, parent=None):
      super(Viewer, self).__init__(parent)
      self.filename = ""
      self.fname = ""
      self.csv_file = ''
      self.isChanged = False
      self.mychannels_file = 'mychannels.txt'
      self.mychannels_file_backup = 'mychannels.txt_backup'
      self.setGeometry(0, 0, 1000, 600)
      self.lb = QTableWidget()
      self.lb.horizontalHeader().hide()
      self.lb.setColumnCount(2)
      self.lb.setEditTriggers(QAbstractItemView.DoubleClicked)
      self.lb.setSelectionBehavior(self.lb.SelectRows)
      self.lb.setSelectionMode(self.lb.SingleSelection)
      self.lb.setDragDropMode(self.lb.InternalMove)
      self.setStyleSheet(stylesheet(self))
      self.lb.setAcceptDrops(True)
      self.setCentralWidget(self.lb)
      self.setContentsMargins(10, 10, 10, 10)
      self.statusBar().showMessage("welcome", 0)
      self.setWindowTitle("TVPlayer2 Editor")
      self.setWindowIcon(QIcon.fromTheme("multimedia-playlist"))
      self.createToolBar()
      self.create_backup()
      self.show()
      print("Hello")
      self.open_channels(self.mychannels_file)
      self.lb.setFocus()
      
    def setChanged(self):
        self.isChanged = True
      
    def msgbox(self, message):
        msg = QMessageBox(2, "Information", message, QMessageBox.Ok)
        msg.exec()

      
    def create_backup(self):
        if shutil.copyfile(self.mychannels_file, self.mychannels_file_backup):
            self.msgbox('mychannels.txt_backup created')

    def closeEvent(self, event):
        print(self.isChanged)
        if  self.isChanged == True:
            quit_msg = "<b>The document has been changed. <br> Do you want to save the changes?</ b>"
            reply = QMessageBox.question(self, 'Save', 
                     quit_msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                event.accept()
                self.save_file(self.filename)
        else:
            print("no changes.")

    def createToolBar(self):
        tb = self.addToolBar("Tools")
        tb.setIconSize(QSize(16, 16))
        tb.setMovable(False)
        
        self.findfield = QLineEdit(placeholderText = "find ...")
        self.findfield.setClearButtonEnabled(True)
        self.findfield.setFixedWidth(200)
        tb.addWidget(self.findfield)
        
        tb.addSeparator()
        
        self.replacefield = QLineEdit(placeholderText = "replace with ...")
        self.replacefield.setClearButtonEnabled(True)
        self.replacefield.setFixedWidth(200)
        tb.addWidget(self.replacefield)
        
        tb.addSeparator()
        
        btn = QToolButton()
        btn.setText("replace all")
        btn.setToolTip("replace all")
        btn.clicked.connect(self.replace_in_table)
        tb.addWidget(btn)
        
        tb.addSeparator()

        del_btn = QToolButton()
        del_btn.setIcon(QIcon.fromTheme("edit-delete"))
        del_btn.setToolTip("delete row")
        del_btn.clicked.connect(self.del_row)
        tb.addWidget(del_btn)
        
        tb.addSeparator()
        
        add_btn = QToolButton()
        add_btn.setIcon(QIcon.fromTheme("list-add"))
        add_btn.setToolTip("add row")
        add_btn.clicked.connect(self.add_row)
        tb.addWidget(add_btn)

        move_down_btn = QToolButton()
        move_down_btn.setIcon(QIcon.fromTheme("go-down"))
        move_down_btn.setToolTip("one row down")
        move_down_btn.clicked.connect(self.move_down)
        tb.addWidget(move_down_btn)
        
        move_up_up = QToolButton()
        move_up_up.setIcon(QIcon.fromTheme("go-up"))
        move_up_up.setToolTip("one row up")
        move_up_up.clicked.connect(self.move_up)
        tb.addWidget(move_up_up)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, 0)
        tb.addWidget(spacer)
        
        self.filter_field = QLineEdit(placeholderText = "Filter (press enter)")
        self.filter_field.setClearButtonEnabled(True)
        self.filter_field.setToolTip("Insert search term and press Enter")
        self.filter_field.setFixedWidth(200)
        self.filter_field.returnPressed.connect(self.filter_table)
        self.filter_field.textChanged.connect(self.update_filter)
        tb.addWidget(self.filter_field)
        
        
    def move_down(self): # ok
        if self.lb.rowCount() < 1:
            return
        row = self.lb.selectedItems()[0].row()
        if row > self.lb.rowCount() - 2:
            return
            
        nextrow = row + 1
        name_1 = self.lb.item(row, 0).text()
        url_1 = self.lb.item(row, 1).text()
        
        name_2 = self.lb.item(nextrow, 0).text()
        url_2 = self.lb.item(nextrow, 1).text()
        
        self.lb.removeRow(row)
        row = self.lb.selectedItems()[0].row() 
        self.lb.setItem(row, 0, QTableWidgetItem(name_2))
        self.lb.setItem(row, 1, QTableWidgetItem(url_2))
        
        self.lb.insertRow(nextrow)
        self.lb.selectRow(nextrow)
     
        self.lb.setItem(nextrow, 0, QTableWidgetItem(name_1))
        self.lb.setItem(nextrow, 1, QTableWidgetItem(url_1))

        self.isChanged = True
        
        
    def move_up(self): # ok
        if self.lb.rowCount() < 1:
            return
        row = self.lb.selectedItems()[0].row()
        if row < 1:
            return
        nextrow = row - 1
        name_1 = self.lb.item(nextrow, 0).text()
        url_1 = self.lb.item(nextrow, 1).text()
        
        name_2 = self.lb.item(row, 0).text()
        url_2 = self.lb.item(row, 1).text()
        
        self.lb.removeRow(row)
        row = self.lb.selectedItems()[0].row() 
        self.lb.setItem(row, 0, QTableWidgetItem(name_1))
        self.lb.setItem(row, 1, QTableWidgetItem(url_1))
        
        self.lb.insertRow(nextrow)
        self.lb.selectRow(nextrow)
     
        self.lb.setItem(nextrow, 0, QTableWidgetItem(name_2))
        self.lb.setItem(nextrow, 1, QTableWidgetItem(url_2))

        self.isChanged = True
        
    def del_row(self): # ok
        if self.lb.rowCount() < 1:
            return
        row = self.lb.selectionModel().selection().indexes()[0].row()
        self.lb.removeRow(row)
        self.isChanged = True
        self.lb.selectRow(row)
            
    def add_row(self): # ok
        if self.lb.rowCount() < 1:
            return
        print("add row")
        self.lb.insertRow(self.lb.rowCount())
        name = QTableWidgetItem("Name")
        url = QTableWidgetItem("url")
        self.lb.setItem(self.lb.rowCount()-1, 0, name)
        self.lb.setItem(self.lb.rowCount()-1, 1, url)
        self.isChanged = True
        self.lb.selectRow(self.lb.rowCount() - 1)
        
    def open_channels(self, fileName): # ok
        if fileName:
            print("loading" , fileName)
            with open(fileName, 'r') as f:
                i = 0
                reader = f.read().splitlines()
                for row in reader:
                    line = row.split(",")
                    name = QTableWidgetItem(line[0])
                    url = QTableWidgetItem(line[1])
                    self.lb.insertRow(i)
                    self.lb.setItem(i, 0, name)
                    self.lb.setItem(i, 1, url)
                    i = i + 1     
                self.lb.resizeColumnsToContents()           
                self.lb.selectRow(0)
                self.statusBar().showMessage(f"{fileName} loaded", 0)
                self.isChanged = False
                self.lb.verticalHeader().setMinimumWidth(24)
                self.filename = fileName
            
    def save_file(self, fileName): # ok
        content = ""
        
        for row in range(self.lb.model().rowCount()):
            itemlist = ""
            itemlist += f"{self.lb.item(row, 0).text()},{self.lb.item(row, 1).text()}"
            content += itemlist
            content += '\n'
        with open(self.mychannels_file, 'w') as f:
            f.write(content)

    def replace_in_table(self): # ok
        if self.lb.rowCount() < 1:
            return
        searchterm = self.findfield.text()
        replaceterm = self.replacefield.text()
        if searchterm == "":
            return
        else:
            for row in range(self.lb.rowCount()-1):
                item = self.lb.item(row, 0)
                item_text = item.text()
                if searchterm in item_text:                    
                    self.lb.setItem(row, 0, QTableWidgetItem(item_text.replace(searchterm, replaceterm)))
                self.lb.resizeColumnsToContents()
                self.isChanged = True
                
    def filter_table(self): # ok
        if self.lb.rowCount() < 1:
            return
        searchterm = self.filter_field.text()
        for rowIndex in range(self.lb.rowCount()):
            twItem = self.lb.item(rowIndex, 0)
            if not twItem.text().lower().find(searchterm.lower()):
                self.lb.setRowHidden(rowIndex, False)
            else:
                self.lb.setRowHidden(rowIndex, True)
       
    def update_filter(self): # ok
        if self.filter_field.text() == "":
            for x in range(self.lb.rowCount()):
                self.lb.showRow(x)

def stylesheet(self):
        return """
    QMenuBar
        {
            background: transparent;
            border: 0px;
        }
        
    QMenuBar:hover
        {
            background: #d3d7cf;
        }
        
    QTableView
        {
            border: 1px solid #d3d7cf;
            border-radius: 0px;
            font-size: 8pt;
            background: #eeeeec;
            selection-color: #ffffff
        }
    QTableView::item:hover
        {   
            color: black;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #729fcf, stop:1 #d3d7cf);           
        }
        
    QTableView::item:selected {
            color: #F4F4F4;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #6169e1, stop:1 #3465a4);
        } 

    QTableView QTableCornerButton::section {
            background: #D6D1D1;
            border: 0px outset black;
        }
        
    QHeaderView:section {
            background: #d3d7cf;
            color: #555753;
            font-size: 8pt;
        }
        
    QHeaderView:section:checked {
            background: #204a87;
            color: #ffffff;
        }
        
    QStatusBar
        {
        font-size: 7pt;
        color: #555753;
        }
        
    """
 
#if __name__ == "__main__":
# 
#    app = QApplication(sys.argv)
#    main = Viewer()
#    main.show()
#sys.exit(app.exec_())
