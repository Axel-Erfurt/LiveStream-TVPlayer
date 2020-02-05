#!/usr/bin/python3
# -*- coding: utf-8 -*-
#############################################################################

from PyQt5.QtCore import (QPoint, QRect, Qt, QUrl, QProcess, QFile, QDir, QTimer, QSize, QEvent, 
                                                    QStandardPaths, QFileInfo, QCoreApplication)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QMainWindow, QMessageBox, 
                                                    QMenu, QWidget, QInputDialog, QLineEdit, QFileDialog, QLabel, 
                                                    QFormLayout, QSlider, QPushButton, QDialog)
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget

import os
from time import sleep
import subprocess
import sys
from requests import get as getURL

mytv = "tv-symbolic"
mybrowser = "video-television"
ratio = 1.777777778

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.colorDialog = None
        self.urlList = []
        self.link = ""
        self.menulist = []
        self.recording_enabled = False
        self.is_recording = False
        self.recname = ""
        self.timeout = "60"
        self.tout = 60
        self.outfile = "/tmp/TV.mp4"
        self.myARD = ""
        self.channelname = ""

        self.channels_menu = QMenu()
        self.c_menu = self.channels_menu.addMenu(QIcon.fromTheme(mytv), "Channels")

        self.process = QProcess()
        self.process.started.connect(self.getPID)
        self.process.finished.connect(self.timer_finished)
        self.process.finished.connect(self.recfinished)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.StreamPlayback)
        self.mediaPlayer.setVolume(90)
        print("Volume:", self.mediaPlayer.volume())
        self.mediaPlayer.error.connect(self.handleError)
        self.setAcceptDrops(True)

        self.videoWidget = QVideoWidget(self)
        self.videoWidget.setStyleSheet("background: black;")
        self.videoWidget.setAcceptDrops(True)
        self.videoWidget.setAspectRatioMode(1)
        self.videoWidget.setContextMenuPolicy(Qt.CustomContextMenu);
        self.videoWidget.customContextMenuRequested[QPoint].connect(self.contextMenuRequested)
        self.setCentralWidget(self.videoWidget)
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        self.lbl = QLabel(self.videoWidget)
        self.lbl.setGeometry(3, 3, 11, 11)
        self.lbl.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.lbl.setStyleSheet("background: #2e3436; color: #ef2929; font-size: 10pt;")
        self.lbl.setText("®")
        self.lbl.hide()

        self.root = QFileInfo.path(QFileInfo(QCoreApplication.arguments()[0]))
        print("Programmordner ist: " + self.root)

        self.fullscreen = False

        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setMinimumSize(320, 180)
        self.setGeometry(0, 0, 480, 480 / ratio)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        screen = QApplication.primaryScreen()
        screenGeometry = QRect(screen.geometry())
        screensize = QPoint(screenGeometry.width(), screenGeometry.height())
        p = QPoint(self.mapToGlobal(QPoint(screensize)) -
                    QPoint(self.size().width() + 2, self.size().height() + 2))
        self.move(p)
    
        screenGeometry = QApplication.desktop().availableGeometry()
        screenGeo = screenGeometry.bottomRight()
        self.move(screenGeo)

        self.setWindowTitle("TV Player & Recorder")
        self.setWindowIcon(QIcon.fromTheme("multimedia-video-player"))

        self.myinfo = "<h1>TVPlayer2</h1>©2018<br><a href='https://goodoldsongs.jimdofree.com/'>Axel Schneider</a>\
                        <br>\
                        <h3>Shortcuts:</h3>q = Exit<br>f = toggle Fullscreen<br>\
                        u = play Url from Clipboard <br>\
                        mouse wheel = resize Window<br>\
                        ↑ = more volume<br>\
                        ↓ = less volume<br>\
                        m = mute on / off<br>\
                        h = mouse pointer on / off<br>\
                        r = record with Timer<br>\
                        w = record without Timer<br>s = stop recording"
        print("Welcome to TV Player & Recorder")
        if self.is_tool("streamlink"):
            print("streamlink found\nrecording enabled")
            self.recording_enabled = True
        else:
            self.msgbox("streamlink not found\nno recording available")
        self.getLists()
        self.makeMenu()
        if not self.myARD == "":
            self.play_ARD()
        
    def getMenu(self):
        chFolder = self.root + "/tv_listen/"
        pList = [f for f in os.listdir(chFolder) if os.path.isfile(os.path.join(chFolder, f))]
        menuList = []
        
        for x in range(len(pList)):
            ft = f"{chFolder}{pList[x]}"
            name = os.path.splitext(os.path.basename(ft))[0]
            text = open(ft, 'r').read()
            
            mlist = text.splitlines()
            for x in range(len(mlist)):
                if "RESOLUTION=640" in mlist[x]:
                    menuList.append(f"{name.upper()},{mlist[x+1]}")
                    if name.upper() == "ARD":
                        self.myARD = (f"{name.upper()},{mlist[x+1]}")
                    if name.upper() == "ZDF":
                        self.myZDF = (f"{name.upper()},{mlist[x+1]}")
                    if name.upper() == "MDR THÜRINGEN":
                        self.myMDR = (f"{name.upper()},{mlist[x+1]}")
                    if name.upper() == "PHOENIX":
                        self.myPhoenix = (f"{name.upper()},{mlist[x+1]}")
                    if name.upper() == "ZDF INFO":
                        self.myZDFInfo = (f"{name.upper()},{mlist[x+1]}")
                    break
            for x in range(len(mlist)):
                if "RESOLUTION=1280" in mlist[x]:
                    menuList.append(f"{name.upper()} HD,{mlist[x+1]}")
                    break
                elif "RESOLUTION=852" in mlist[x]:
                    menuList.append(f"{name.upper()} HD,{mlist[x+1]}")
                    break
        menuList.sort(key=lambda x:x.partition(",")[0].upper()[:5])
        return menuList


    def makeMenu(self):
        pList = self.getMenu()
        hdm = self.c_menu.addMenu(QIcon.fromTheme("computer"), "HD")
        for playlist in pList:
            name = playlist.partition(",")[0]
            url = playlist.partition(",")[2]
            if not "HD" in name:
                a = QAction(name, self, triggered=self.playTV)
                a.setIcon(QIcon.fromTheme(mybrowser))
                a.setData(url)
                rm = self.c_menu.addAction(a)
            else:
                a = QAction(name, self, triggered=self.playTV)
                a.setIcon(QIcon.fromTheme(mybrowser))
                a.setData(url)
                rm = hdm.addAction(a)

        a = QAction(QIcon.fromTheme(mybrowser), "Sport1 Live", self, triggered=self.play_Sport1)
        self.c_menu.addAction(a)
    
    def dragEnterEvent(self, event):
        if (event.mimeData().hasUrls()):
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0].toString()
            print("url = ", url)
            self.mediaPlayer.stop()
            self.mediaPlayer.setMedia(QMediaContent(QUrl(url)))
            self.mediaPlayer.play()
        elif event.mimeData().hasText():
            mydrop =  event.mimeData().text()
            if "http" in mydrop:
                print("stream url = ", mydrop)
                self.mediaPlayer.setMedia(QMediaContent(QUrl(mydrop)))
                self.mediaPlayer.play()
        event.acceptProposedAction()
        

    def recfinished(self):
        print("recording finished 1")

    def is_tool(self, name):
        tool = QStandardPaths.findExecutable(name)
        if tool is not "":
            print(tool)
            return True
        else:
            return False

    def getPID(self):
        print(self.process.pid(), self.process.processId() )

    def recordNow2(self):
        if not self.recording_enabled == False:
            if QFile(self.outfile).exists:
                print("deleting file " + self.outfile) 
                QFile(self.outfile).remove
            else:
                print("the file " + self.outfile + " does not exist") 
            self.recname = self.channelname
            self.showLabel()
            print("recording to /tmp")
            self.is_recording = True
            cmd = 'streamlink --force ' + self.link.replace("?sd=10&rebase=on", "") + ' best -o ' + self.outfile
            print(cmd)
            self.process.startDetached(cmd)

    def recordNow(self):
        if not self.recording_enabled == False:
            if QFile(self.outfile).exists:
                print("deleting file " + self.outfile) 
                QFile(self.outfile).remove
            else:
                print("the file " + self.outfile + " does not exist") 
            #self.showLabel()
            infotext = '<i>temporary Recording to file: /tmp/TV.mp4</i> \
                            <br><b><font color="#a40000";>save folder and filename will be asked \
                            after recording finished</font></b> \
                            <br><br><b>Example:</b><br>60s (60 seconds)<br>120m (120 minutes)'
            dlg = QInputDialog()
            tout, ok = dlg.getText(self, 'Recording duration', infotext, \
                                    QLineEdit.Normal, "90m", Qt.Dialog)
            if ok:
                self.tout = str(tout)
                self.recordChannel()
            else:
                self.lbl.hide()
                print("recording cancelled")

    def recordChannel(self):
        self.recname = self.channelname
        self.showLabel()
        cmd =  'timeout ' + str(self.tout) + ' streamlink --force ' + self.link.replace("?sd=10&rebase=on", "") + ' best -o ' + self.outfile
        print(cmd)
        print("recording to /tmp with timeout: " + str(self.tout))
        self.lbl.update()
        self.is_recording = True
        self.process.start(cmd)
################################################################

    def saveMovie(self):
        #self.msgbox("recording finished")
        self.fileSave()

    def fileSave(self):
        infile = QFile(self.outfile)
        path, _ = QFileDialog.getSaveFileName(self, "Save as...", QDir.homePath() + "/Videos/" + self.recname + ".mp4",
            "Video (*.mp4)")
        #path = QDir.homePath() + "/Videos/TVRecording.mp4"
        if os.path.exists(path):
            os.remove(path)
        if (path != ""):
            savefile = path
            if QFile(savefile).exists:
                QFile(savefile).remove()
            print("saving " + savefile)
            if not infile.copy(savefile):
                QMessageBox.warning(self, "Error",
                    "cannot write file %s:\n%s." % (path, infile.errorString()))
            if infile.exists:
                infile.remove()
            self.lbl.hide()
        else:
            self.lbl.hide()

    def stop_recording(self):
        print(self.process.state())
        if self.is_recording == True:
            print("recording stopped")
            QProcess().execute("killall streamlink")
            self.process.kill()
            self.is_recording = False
            if self.process.exitStatus() == 0:
                self.saveMovie()
        else:
            print("no recording task")
            self.lbl.hide()
 
    def rec_finished(self):
        print("finished recording")
        self.process.kill()
#        self.timer_finished()

    def timer_finished(self):
        print("Timer ended")
        self.is_recording = False
        self.process.kill()
        print("finished recording")

        self.lbl.hide()
        self.saveMovie()

    def playURL(self):
        clip = QApplication.clipboard()
        self.link = clip.text()
        if not self.link.startswith("http"):
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.link)))
        else:
            self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
        self.mediaPlayer.play()

    def handleError(self):
        if not str(self.mediaPlayer.errorString()) == "QWidget::paintEngine: Should no longer be called":
            print("Fehler: " + self.mediaPlayer.errorString())
            self.msgbox("Fehler: " + self.mediaPlayer.errorString())

    def handleMute(self):
        if not self.mediaPlayer.isMuted():
            self.mediaPlayer.setMuted(True)
        else:
            self.mediaPlayer.setMuted(False)

    def handleAbout(self):
        msg = QMessageBox.about(self, "TVPlayer2", self.myinfo)

    def handleFullscreen(self):
        if self.fullscreen == True:
            self.fullscreen = False
            print("Fullscreen off")
        else:
            self.rect = self.geometry()
            self.showMaximized()
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.fullscreen = True
            print("Fullscreen on")
        if self.fullscreen == False:
            self.showNormal()
            self.setGeometry(self.rect)
            QApplication.setOverrideCursor(Qt.BlankCursor)
        self.handleCursor()

    def handleCursor(self):
        if  QApplication.overrideCursor() ==  Qt.ArrowCursor:
            QApplication.setOverrideCursor(Qt.BlankCursor)
        else:
            QApplication.setOverrideCursor(Qt.ArrowCursor)
    
    def handleQuit(self):
        self.mediaPlayer.stop()
        print("Goodbye ...")
        app.quit()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Q:
            self.handleQuit()
        elif e.key() == Qt.Key_H:
            self.handleCursor()
        elif e.key() == Qt.Key_F:
            self.handleFullscreen()
        elif e.key() == Qt.Key_M:
            self.handleMute()
        elif e.key() == Qt.Key_I:
            self.handleAbout()
        elif e.key() == Qt.Key_U:
            self.playURL()
        elif e.key() == Qt.Key_R:
            self.recordNow()
        elif e.key() == Qt.Key_S:
            self.stop_recording()
        elif e.key() == Qt.Key_W:
            self.recordNow2()
        elif e.key() == Qt.Key_C:
            self.showColorDialog()
        elif e.key() == Qt.Key_1:
            self.play_ARD()
        elif e.key() == Qt.Key_2:
            self.play_ZDF()
        elif e.key() == Qt.Key_3:
            self.play_MDR()
        elif e.key() == Qt.Key_4:
            self.play_Phoenix()
        elif e.key() == Qt.Key_5:
            self.play_Sport1()
        elif e.key() == Qt.Key_Z:
            self.play_Info()
        elif e.key() == Qt.Key_Up:
            if self.mediaPlayer.volume() < 100:
                self.mediaPlayer.setVolume(self.mediaPlayer.volume() + 5)
                print("Volume:", self.mediaPlayer.volume())
        elif e.key() == Qt.Key_Down:
            if self.mediaPlayer.volume() > 5:
                self.mediaPlayer.setVolume(self.mediaPlayer.volume() - 5)
                print("Volume:", self.mediaPlayer.volume())
        else:
            e.accept()

    def getLists(self):
        the_folder = self.root + "/tv_listen"
        for entry in os.listdir(the_folder):
            if str(entry).endswith(".m3u8"):
                self.urlList.append(the_folder + "/" + str(entry))
        self.urlList.sort()

    def contextMenuRequested(self, point):
        self.channels_menu.clear()
        self.channels_menu.addMenu(self.c_menu)
        if not self.recording_enabled == False:
            self.channels_menu.addSection("Recording")
    
            tv_record = QAction(QIcon.fromTheme("media-record"), "record with Timer (r)", triggered = self.recordNow)
            self.channels_menu.addAction(tv_record)

            tv_record2 = QAction(QIcon.fromTheme("media-record"), "record without Timer (w)", triggered = self.recordNow2)
            self.channels_menu.addAction(tv_record2)

            tv_record_stop = QAction(QIcon.fromTheme("media-playback-stop"), "stop recording (s)", triggered = self.stop_recording)
            self.channels_menu.addAction(tv_record_stop)
    
            self.channels_menu.addSeparator()

        self.channels_menu.addSeparator()

        about_action = QAction(QIcon.fromTheme("help-about"), "Info (i)", triggered = self.handleAbout, shortcut = "i")
        self.channels_menu.addAction(about_action)

        self.channels_menu.addSeparator()

        url_action = QAction(QIcon.fromTheme(mybrowser), "play URL from Clipboard (u)", triggered = self.playURL)
        self.channels_menu.addAction(url_action)

        self.channels_menu.addSection("Einstellungen")

        color_action = QAction(QIcon.fromTheme("preferences-color"), "Color Settings (c)", triggered = self.showColorDialog)
        self.channels_menu.addAction(color_action)

        self.channels_menu.addSeparator()
        
        self.updateAction = QAction(QIcon.fromTheme("download"), "update Channels", triggered = self.updateChannels)
        self.channels_menu.addAction(self.updateAction)
        
        self.channels_menu.addSeparator()

        quit_action = QAction(QIcon.fromTheme("application-exit"), "Exit (q)", triggered = self.handleQuit)
        self.channels_menu.addAction(quit_action)

        self.channels_menu.exec_(self.mapToGlobal(point))
        
    def updateChannels(self):
        update_script = f"{os.path.join(self.root, 'query_mv.py')}"
        print(update_script)
        if os.path.isfile(update_script):
            print("starting", update_script)
            subprocess.call(["python3", update_script, self.root])
            self.c_menu.clear()
            self.makeMenu()
            self.msgbox("updated channels available")

    def play_ARD(self):
        if not self.is_recording:
            self.lbl.hide()
        self.link = self.myARD.partition(",")[2].replace("\n", "")
        self.channelname = "ARD"
        self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
        print("current channel:", self.channelname, "\nURL:", self.link)
        self.mediaPlayer.play()

    def play_ZDF(self):
        if not self.is_recording:
            self.lbl.hide()
        self.link = self.myZDF.partition(",")[2].replace("\n", "")
        self.channelname = "ZDF"
        self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
        print("current channel:", self.channelname, "\nURL:", self.link)
        self.mediaPlayer.play()

    def play_MDR(self):
        if not self.is_recording:
            self.lbl.hide()
        self.link = self.myMDR.partition(",")[2].replace("\n", "")
        self.channelname = "MDR"
        self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
        print("current channel:", self.channelname, "\nURL:", self.link)
        self.mediaPlayer.play()

    def play_Info(self):
        if not self.is_recording:
            self.lbl.hide()
        self.link = self.myZDFInfo.partition(",")[2].replace("\n", "")
        self.channelname = "ZDF Info"
        self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
        print("current channel:", self.channelname, "\nURL:", self.link)
        self.mediaPlayer.play()

    def play_Phoenix(self):
        if not self.is_recording:
            self.lbl.hide()
        self.link = self.myPhoenix.partition(",")[2].replace("\n", "")
        self.channelname = "Phoenix"
        self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
        print("current channel:", self.channelname, "\nURL:", self.link)
        self.mediaPlayer.play()

    def play_Sport1(self):
        if not self.is_recording:
            self.lbl.hide()
        url = "https://tv.sport1.de/sport1/"
        r = getURL(url)
        myurl = r.text.partition('file: "')[2].partition('"')[0].replace("\n", "")
        print("grabbed url Sport1:", myurl)
        if not myurl =="":
            self.channelname = "Sport1"
            self.mediaPlayer.setMedia(QMediaContent(QUrl(myurl)))
            self.link = myurl
            print("current channel:", self.channelname, "\nURL:", self.link)
            self.mediaPlayer.play()

    def showLabel(self):
        self.lbl.show()

    def playTV(self):
        if not self.is_recording:
            self.lbl.hide()
        action = self.sender()
        self.link = action.data().replace("\n", "")
        self.channelname = action.text()
        print("current channel:", self.channelname, "\nURL:", self.link)
        self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
        self.mediaPlayer.play()

    def closeEvent(self, event):
        event.accept()

    def msgbox(self, message):
        QMessageBox.warning(self, "Message", message)

    def wheelEvent(self, event):
        mwidth = self.frameGeometry().width()
        mheight = self.frameGeometry().height()
        #ratio = 1.777777778
        mleft = self.frameGeometry().left()
        mtop = self.frameGeometry().top()
        mscale = event.angleDelta().y() / 6
        self.resize(mwidth + mscale, (mwidth + mscale) / ratio)
        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() \
                      - QPoint(self.frameGeometry().width() / 2, \
                               self.frameGeometry().height() / 2))
            event.accept()

    def showColorDialog(self):
        if self.colorDialog is None:
            self.brightnessSlider = QSlider(Qt.Horizontal)
            self.brightnessSlider.setRange(-100, 100)
            self.brightnessSlider.setValue(self.videoWidget.brightness())
            self.brightnessSlider.sliderMoved.connect(
                    self.videoWidget.setBrightness)
            self.videoWidget.brightnessChanged.connect(
                    self.brightnessSlider.setValue)

            self.contrastSlider = QSlider(Qt.Horizontal)
            self.contrastSlider.setRange(-100, 100)
            self.contrastSlider.setValue(self.videoWidget.contrast())
            self.contrastSlider.sliderMoved.connect(self.videoWidget.setContrast)
            self.videoWidget.contrastChanged.connect(self.contrastSlider.setValue)

            self.hueSlider = QSlider(Qt.Horizontal)
            self.hueSlider.setRange(-100, 100)
            self.hueSlider.setValue(self.videoWidget.hue())
            self.hueSlider.sliderMoved.connect(self.videoWidget.setHue)
            self.videoWidget.hueChanged.connect(self.hueSlider.setValue)

            self.saturationSlider = QSlider(Qt.Horizontal)
            self.saturationSlider.setRange(-100, 100)
            self.saturationSlider.setValue(self.videoWidget.saturation())
            self.saturationSlider.sliderMoved.connect(
                    self.videoWidget.setSaturation)
            self.videoWidget.saturationChanged.connect(
                    self.saturationSlider.setValue)

            layout = QFormLayout()
            layout.addRow("Brightness", self.brightnessSlider)
            layout.addRow("Contrast", self.contrastSlider)
            layout.addRow("Hue", self.hueSlider)
            layout.addRow("Color", self.saturationSlider)

            btn = QPushButton("Reset")
            btn.setIcon(QIcon.fromTheme("preferences-color"))
            layout.addRow(btn)

            button = QPushButton("Close")
            button.setIcon(QIcon.fromTheme("ok"))
            layout.addRow(button)

            self.colorDialog = QDialog(self)
            self.colorDialog.setWindowTitle("Color Settings")
            self.colorDialog.setLayout(layout)

            btn.clicked.connect(self.resetColors)
            button.clicked.connect(self.colorDialog.close)

        self.colorDialog.resize(300, 180)
        self.colorDialog.show()

    def resetColors(self):
        self.brightnessSlider.setValue(0)
        self.videoWidget.setBrightness(0)

        self.contrastSlider.setValue(0)
        self.videoWidget.setContrast(0)

        self.saturationSlider.setValue(0)
        self.videoWidget.setSaturation(0)

        self.hueSlider.setValue(0)
        self.videoWidget.setHue(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
