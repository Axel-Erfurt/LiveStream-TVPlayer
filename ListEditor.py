#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import pandas as pd
from PyQt5.QtCore import Qt, QDir, QAbstractTableModel, QModelIndex, QVariant, QSize
from PyQt5.QtWidgets import (QMainWindow, QTableView, QApplication, QLineEdit,  
                             QFileDialog, QAbstractItemView, QMessageBox, QToolButton)
from PyQt5.QtGui import QIcon, QKeySequence

class PandasModel(QAbstractTableModel):
    def __init__(self, df = pd.DataFrame(), parent=None): 
        QAbstractTableModel.__init__(self, parent=None)
        self._df = df
        self.setChanged = False
        self.dataChanged.connect(self.setModified)

    def setModified(self):
        self.setChanged = True
        print(self.setChanged)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError, ):
                return QVariant()
        elif orientation == Qt.Vertical:
            try:
                return self._df.index.tolist()[section]
            except (IndexError, ):
                return QVariant()

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if (role == Qt.EditRole):
                return self._df.values[index.row()][index.column()]
            elif (role == Qt.DisplayRole):
                return self._df.values[index.row()][index.column()]
        return None

    def setData(self, index, value, role):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        self._df.values[row][col] = value
        self.dataChanged.emit(index, index)
        return True

    def rowCount(self, parent=QModelIndex()): 
        return len(self._df.index)

    def columnCount(self, parent=QModelIndex()): 
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(colname, ascending= order == Qt.AscendingOrder, inplace=True)
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()

class Viewer(QMainWindow):
    def __init__(self, parent=None):
      super(Viewer, self).__init__(parent)
      self.df = None
      self.filename = ""
      self.fname = ""
      self.csv_file = ''
      self.mychannels_file = ""
      self.setGeometry(0, 0, 1000, 600)
      self.lb = QTableView()
      self.lb.horizontalHeader().hide()
      self.model =  PandasModel()
      self.lb.setModel(self.model)
      self.lb.setEditTriggers(QAbstractItemView.DoubleClicked)
      self.lb.setSelectionBehavior(self.lb.SelectRows)
      self.lb.setSelectionMode(self.lb.SingleSelection)
      self.lb.setDragDropMode(self.lb.InternalMove)
      self.setStyleSheet(stylesheet(self))
      self.lb.setAcceptDrops(True)
      self.setCentralWidget(self.lb)
      self.setContentsMargins(10, 10, 10, 10)
      self.statusBar().showMessage("Ready", 0)
      self.setWindowTitle("TVPlayer2 List Editor")
      self.setWindowIcon(QIcon.fromTheme("multimedia-playlist"))
      self.createMenuBar()
      self.createToolBar()
      self.lb.setFocus()
      

    def closeEvent(self, event):
        print(self.model.setChanged)
        if  self.model.setChanged == True:
            quit_msg = "<b>The document was changed.<br>Do you want to save the changes?</ b>"
            reply = QMessageBox.question(self, 'Save Confirmation', 
                     quit_msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                event.accept()
                self.writeCSV()
        else:
            print("nothing changed. goodbye")

    def createMenuBar(self):
        bar=self.menuBar()
        self.filemenu=bar.addMenu("File")
        self.separatorAct = self.filemenu.addSeparator()
        self.filemenu.addAction(QIcon.fromTheme("document-open"), "Load Channels File",  self.load_channels_file, QKeySequence.Open) 
        self.filemenu.addAction(QIcon.fromTheme("document-save-as"), "Save as ...",  self.writeCSV, QKeySequence.SaveAs) 

    def createToolBar(self):
        tb = self.addToolBar("Tools")
        tb.setIconSize(QSize(16, 16))
        
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
        add_btn.setIcon(QIcon.fromTheme("add"))
        add_btn.setToolTip("add row")
        add_btn.clicked.connect(self.add_row)
        tb.addWidget(add_btn)

        move_down_btn = QToolButton()
        move_down_btn.setIcon(QIcon.fromTheme("down"))
        move_down_btn.setToolTip("move down")
        move_down_btn.clicked.connect(self.move_down)
        tb.addWidget(move_down_btn)
        
        move_up_up = QToolButton()
        move_up_up.setIcon(QIcon.fromTheme("up"))
        move_up_up.setToolTip("move up")
        move_up_up.clicked.connect(self.move_up)
        tb.addWidget(move_up_up)
        
        tb.addSeparator()
        
        self.filter_field = QLineEdit(placeholderText = "filter group (press Enter)")
        self.filter_field.setClearButtonEnabled(True)
        self.filter_field.setToolTip("insert search term and press enter\n use Selector → to choose column to search")
        self.filter_field.setFixedWidth(200)
        self.filter_field.returnPressed.connect(self.filter_table)
        self.filter_field.textChanged.connect(self.update_filter)
        tb.addWidget(self.filter_field)
        
        
    def move_down(self):
        if self.model.rowCount() < 1:
            return
        i = self.lb.selectionModel().selection().indexes()[0].row()
        b, c = self.df.iloc[i].copy(), self.df.iloc[i+1].copy()
        self.df.iloc[i],self.df.iloc[i+1] = c,b
        self.model.setChanged = True
        self.lb.selectRow(i+1)
        
    def move_up(self):
        if self.model.rowCount() < 1:
            return
        i = self.lb.selectionModel().selection().indexes()[0].row()
        b, c = self.df.iloc[i].copy(), self.df.iloc[i-1].copy()
        self.df.iloc[i],self.df.iloc[i-1] = c,b
        self.model.setChanged = True
        self.lb.selectRow(i-1)
        
    def del_row(self): 
        if self.model.rowCount() < 1:
            return
        i = self.lb.selectionModel().selection().indexes()[0].row()
        if len(self.df.index) > 0:
            self.df = self.df.drop(self.df.index[i])
            self.model = PandasModel(self.df)
            self.lb.setModel(self.model)
            self.model.setChanged = True
            self.lb.selectRow(i)
            
    def add_row(self): 
        if self.model.rowCount() < 1:
            return
        print("adding row")
        newrow = {0:'name', 1:'url'}       
        self.df = self.df.append(newrow, ignore_index=True)
        self.model = PandasModel(self.df)
        self.lb.setModel(self.model)
        self.model.setChanged = True
        self.lb.selectRow(self.model.rowCount() - 1)
                

    def load_channels_file(self):
        if self.model.setChanged == True:
            save_msg = "<b>The document was changed.<br>Do you want to save the changes?</ b>"
            reply = QMessageBox.question(self, 'Save Confirmation', 
                     save_msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.writeCSV()
                self.open_channels()
            else:
                self.model.setChanged = False
                self.open_channels()
        else:
            self.model.setChanged = False
            self.open_channels()
            
    def openFile(self, path=None):
        tvplayer_folder = f'{QDir.homePath()}/.local/share/LiveStream-TVPlayer-master'
        path, _ = QFileDialog.getOpenFileName(self, "Open File", tvplayer_folder,"TVPlayer2 List (*.txt)")
        if path:
            return path
        
    def open_channels(self):
        fileName = self.openFile()
        if fileName:
            self.mychannels_file = fileName
            self.convert_to_csv()
            print(fileName + " loaded")
            f = open(self.csv_file, 'r+b')
            with f:
                self.filename = fileName
                self.df = pd.read_csv(f, delimiter = '\t', keep_default_na = False, low_memory=False, header=None)
                self.model = PandasModel(self.df)
                self.lb.setModel(self.model)
                self.lb.resizeColumnsToContents()
                self.lb.selectRow(0)
                self.statusBar().showMessage(f"{fileName} loaded", 0)
                self.model.setChanged = False
                self.lb.verticalHeader().setMinimumWidth(24)
             
    def convert_to_csv(self):
        mylist = open(self.mychannels_file, 'r').read().splitlines()
        ch = ""
        url = ""
        csv_content = ""
        for x in range(len(mylist)):
            line = mylist[x]
            ch = line.partition(',')[0]
            url = line.partition(',')[2]
            csv_content += (f'{ch}\t{url}\n')
        self.csv_file = '/tmp/mychannels.csv'
        with open(self.csv_file, 'w') as f:        
            f.write(csv_content)
            
    def writeCSV(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", self.mychannels_file,"TVPlayer2 List (*.txt)")
        if fileName:
            # save temporary csv
            f = open(self.csv_file, 'w')
            newModel = self.model
            dataFrame = newModel._df.copy()
            dataFrame.to_csv(f, sep='\t', index = False, header = False)  
            f.close()
            
            # convert to txt
            mylist = open(self.csv_file, 'r').read().splitlines()
            ch = ""
            url = ""
            m3u_content = ""

            for x in range(len(mylist)):
                line = mylist[x].split('\t')
                ch = line[0]
                url = line[1]
                
                m3u_content += f'{ch},{url}\n'

            with open(fileName, 'w') as f:        
                f.write(m3u_content)

            print(fileName + " saved")
            self.model.setChanged = False


    def replace_in_table(self):
        if self.model.rowCount() < 1:
            return
        searchterm = self.findfield.text()
        replaceterm = self.replacefield.text()
        if searchterm == "":
            return
        else:
            if len(self.df.index) > 0:
                self.df.replace(searchterm, replaceterm, inplace=True, regex=True)
                self.lb.resizeColumnsToContents()
                self.model.setChanged = True
                
    def filter_table(self):
        if self.model.rowCount() < 1:
            return
        index = 0
        searchterm = self.filter_field.text()
        df_filtered = self.df[self.df[index].str.contains(searchterm, case=False)]
        self.model = PandasModel(df_filtered)
        self.lb.setModel(self.model)
        self.lb.resizeColumnsToContents()       
       
    def update_filter(self):
        if self.filter_field.text() == "":
            self.filter_table()

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
 
if __name__ == "__main__":
 
    app = QApplication(sys.argv)
    main = Viewer()
    main.show()
sys.exit(app.exec_())