#!/usr/bin/python3
# -*- coding: utf-8 -*-
#############################################################################

from PyQt5.QtCore import (QPoint, QRect, Qt, QUrl, QProcess, QFile, QDir, QTimer, QSize, 
                                                    QStandardPaths, QFileInfo, QCoreApplication)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QMainWindow, QMessageBox, 
                                                    QMenu, QWidget, QInputDialog, QLineEdit, QFileDialog, QLabel, 
                                                    QFormLayout, QSlider, QPushButton, QDialog)
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaMetaData
from PyQt5.QtMultimediaWidgets import QVideoWidget

import m3u8
import os
from time import sleep
import subprocess
import sys

mytv = "tv-symbolic"
mybrowser = "video-television"

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.colorDialog = None
        self.urlList = []
        self.link = ""
        self.menulist = []
        self.recording_enabled = False
        self.is_recording = False
        self.timeout = "60"
        self.tout = 60
        self.outfile = "/tmp/TV.mp4"

        self.channels_menu = QMenu()
        self.c_menu = self.channels_menu.addMenu(QIcon.fromTheme(mytv), "Channels")

        self.process = QProcess()
        self.process.started.connect(self.getPID)
        self.process.finished.connect(self.timer_finished)
        self.process.finished.connect(self.recfinished)


        self.resolutions = ["480", "640", "852",  "960", "1280"]
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.StreamPlayback)
        self.mediaPlayer.setVolume(100)
        self.mediaPlayer.error.connect(self.handleError)
        self.setAcceptDrops(True)

        self.videoWidget = QVideoWidget(self)
        self.videoWidget.setAspectRatioMode(1)
        self.videoWidget.setContextMenuPolicy(Qt.CustomContextMenu);
        self.videoWidget.customContextMenuRequested[QPoint].connect(self.contextMenuRequested)
        self.setCentralWidget(self.videoWidget)
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        self.lbl = QLabel(self.videoWidget)
        self.lbl.setGeometry(10,10, 16, 16)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setStyleSheet("background-color: red;")
        pixmap = QPixmap(QIcon.fromTheme("/home/brian/Dokumente/python_files/def_icons/16x16/actions/media-record.png").pixmap(QSize(16, 16)))
        self.lbl.setPixmap(pixmap)
        self.lbl.hide()

        self.root = QFileInfo.path(QFileInfo(QCoreApplication.arguments()[0]))
        print("root is: " + self.root)

        self.fullscreen = False

        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setMinimumSize(320, 180)
        self.setGeometry(0, 0, 480, 480 / 1.778)

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

        self.myinfo = "<h2>TV-Player</h2>©2018<br>Axel Schneider<h3>Shortcuts:</h3>q = Exit<br>f = toggle Fullscreen<br>u = play url from clipboard<br>h = toggle mouse cursor visible<br>r = record with timer<br>w = record without timer<br>s = stop recording"
        print("Welcome to TV Player & Recorder")
        if self.is_tool("streamlink"):
            print("found streamlink\nrecording enabled")
            self.recording_enabled = True
        else:
            self.msgbox("streamlink not found\nNo recording available")
        self.getLists()
        self.makeMenu()
        self.play_ARD()

    def makeMenu(self):
        ## menu ##
        for url in self.urlList:
            res = ""
            kanal = url.rpartition(".")[0].rpartition("/")[2].upper()
            m = self.c_menu.addMenu(QIcon.fromTheme("video-display"),kanal)
            m.setObjectName(kanal)
            self.menulist.append(kanal)
            variant_m3u8 = m3u8.load(url)
            variant_m3u8.is_variant

            for playlist in variant_m3u8.playlists:
                if not playlist.stream_info.resolution == None:
                    res = str(playlist.stream_info.resolution[0])
                    if res in self.resolutions:
                        a = QAction(res + "p", self, triggered=self.playTV)
                        a.setIcon(QIcon.fromTheme(mybrowser))
                        a.setData(playlist.uri)
                        rm = m.addAction(a)

        a = QAction(QIcon.fromTheme(mybrowser), "Sport1 Live", self, triggered=self.play_Sport1)
        self.c_menu.addAction(a)
        ### end menu
    
    def dragEnterEvent(self, event):
        if (event.mimeData().hasUrls()):
            event.acceptProposedAction()

    def dropEvent(self, event):
        print("drop")
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0].toString()
            print("url = ", url)
            self.mediaPlayer.stop()
            self.mediaPlayer.setMedia(QMediaContent(QUrl(url)))
            self.mediaPlayer.play()
        elif event.mimeData().hasText():
            mydrop =  event.mimeData().text()
            print("generic url = ", mydrop)
            self.mediaPlayer.setMedia(QMediaContent(QUrl(mydrop)))
            self.mediaPlayer.play()
            self.hideSlider()

    def recfinished(self):
        print("recording finished 1")

    def is_tool(self, name):
        tool = QStandardPaths.findExecutable(name)
        if tool is not None:
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
                print("The file " + self.outfile + " does not exist") 
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
                print("The file " + self.outfile + " does not exist") 
            self.showLabel()
            dlg = QInputDialog()
            tout, ok = dlg.getText(self, 'insert timeout', "recording to /tmp/TV.mp4\n\nExample:\n60s (60 seconds)\n120m (120 minutes)", QLineEdit.Normal, "90m", Qt.Dialog)
            if ok:
                self.tout = str(tout)
                self.recordChannel()
            else:
                self.lbl.hide()
                print("recording cancelled")

    def recordChannel(self):
        cmd =  'timeout ' + str(self.tout) + ' streamlink --force ' + self.link.replace("?sd=10&rebase=on", "") + ' best -o ' + self.outfile
        print(cmd)
        print("recording to /tmp with tiimeout: " + str(self.tout))
        self.lbl.update()
        self.is_recording = True
        self.process.start(cmd)
################################################################

    def saveMovie(self):
        self.msgbox("recording finished")
        self.fileSave()

    def fileSave(self):
        infile = QFile(self.outfile)
        path, _ = QFileDialog.getSaveFileName(self, "Save as...", QDir.homePath() + "/Videos/TVRecording.mp4",
            "Video (*.mp4)")
        if (path != ""):
            savefile = path
            if QFile(savefile).exists:
                QFile(savefile).remove()
            print("saving " + savefile)
            if not infile.copy(savefile):
                QMessageBox.warning(self, "Error",
                    "Cannot write file %s:\n%s." % (path, infile.errorString()))
            if infile.exists:
                infile.remove()
        self.lbl.hide()

    def stop_recording(self):
        print(self.process.state())
        if self.is_recording == True:
            print("stop recording")
            QProcess().execute("killall streamlink")
            self.process.kill()
            self.is_recording = False
            if self.process.exitStatus() == 0:
                self.saveMovie()
        else:
            print("no recording process running")
 
    def rec_finished(self):
        print("rec_finished")
        self.process.kill()
#        self.timer_finished()

    def timer_finished(self):
        print("timer_finished")
        self.is_recording = False
        self.process.kill()
        print("recording finished")

        self.lbl.hide()
        self.saveMovie()

    def playURL(self):
        clip = QApplication.clipboard()
        self.link = clip.text()
        self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
        self.mediaPlayer.play()

    def handleError(self):
        if not str(self.mediaPlayer.errorString()) == "QWidget::paintEngine: Should no longer be called":
            print("Error: " + self.mediaPlayer.errorString())
            self.msgbox("Error: " + self.mediaPlayer.errorString())

    def handleMute(self):
        if not self.mediaPlayer.isMuted():
            self.mediaPlayer.setMuted(True)
        else:
            self.mediaPlayer.setMuted(False)

    def handleAbout(self):
        msg = QMessageBox.about(self, "QT5 Player", self.myinfo)

    def handleFullscreen(self):
        if self.fullscreen == True:
            self.fullscreen = False
            print("no Fullscreen")
        else:
            self.rect = self.geometry()
            self.showFullScreen()
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.fullscreen = True
            print("Fullscreen entered")
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
    
            tv_record = QAction(QIcon.fromTheme("media-record"), "record (r)", triggered = self.recordNow)
            self.channels_menu.addAction(tv_record)

            tv_record2 = QAction(QIcon.fromTheme("media-record"), "record without timer (w)", triggered = self.recordNow2)
            self.channels_menu.addAction(tv_record2)

            tv_record_stop = QAction(QIcon.fromTheme("media-playback-stop"), "stop recording (s)", triggered = self.stop_recording)
            self.channels_menu.addAction(tv_record_stop)
    
            self.channels_menu.addSeparator()

        self.channels_menu.addSeparator()

        about_action = QAction(QIcon.fromTheme("help-about"), "Info (i)", triggered = self.handleAbout, shortcut = "i")
        self.channels_menu.addAction(about_action)

        self.channels_menu.addSeparator()

        url_action = QAction(QIcon.fromTheme(mybrowser), "play URL from clipboard (u)", triggered = self.playURL)
        self.channels_menu.addAction(url_action)

        self.channels_menu.addSection("Settings")

        color_action = QAction(QIcon.fromTheme("preferences-color"), "Color Options (c)", triggered = self.showColorDialog)
        self.channels_menu.addAction(color_action)

        self.channels_menu.addSeparator()

        quit_action = QAction(QIcon.fromTheme("application-exit"), "Quit (q)", triggered = self.handleQuit)
        self.channels_menu.addAction(quit_action)

        self.channels_menu.exec_(self.mapToGlobal(point))

    def play_ARD(self):
        self.link = "https://derste247livede.akamaized.net/hls/live/658317/daserste_de/master_1184.m3u8"
        self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
        self.mediaPlayer.play()

    def play_ZDF(self):
        self.link = "https://zdf-hls-01.akamaized.net/hls/live/2002460/de/ea2c86283bee25eee11b3b449370a64c/2/2.m3u8"
        self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
        self.mediaPlayer.play()

    def play_MDR(self):
        self.link = "http://mdrthuhls-lh.akamaihd.net/i/livetvmdrthueringen_de@514027/index_1216_av-p.m3u8?sd=10&rebase=on"
        self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
        self.mediaPlayer.play()

    def play_Info(self):
        self.link = "https://zdfhls17-i.akamaihd.net/hls/live/744750/de/2/2.m3u8"
        self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
        self.mediaPlayer.play()

    def play_Phoenix(self):
        self.link = "https://zdfhls19-i.akamaihd.net/hls/live/744752-b/de/2/2.m3u8"
        self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
        self.mediaPlayer.play()

    def play_Sport1(self):
        if not QStandardPaths.findExecutable("youtube-dl") == "":
            cmd = "youtube-dl -g https://tv.sport1.de/sport1/"
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
            (link, err) = proc.communicate()
            print(link)
            myurl = str(link).partition('\n')[0] #.partition("b'")[2].replace("\n", "")
            if not myurl =="":
                self.mediaPlayer.setMedia(QMediaContent(QUrl(myurl)))
                self.link = myurl
                self.mediaPlayer.play()
            else:
                msg = QMessageBox.about(self, "TVLive", "URL not found")
        else:
                msg = QMessageBox.about(self, "TVLive", "youtube-dl not found")

    def showLabel(self):
        self.lbl.show()

    def playTV(self):
        action = self.sender()
#        channel = self.sender().parent()
        self.link = action.data()
        self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
        self.mediaPlayer.play()
#        self.setWindowTitle(channel)

    def closeEvent(self, event):
        event.accept()

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def msgbox(self, message):
        QMessageBox.warning(self, "Message", message)

    def wheelEvent(self, event):
#        return
        mwidth = self.frameGeometry().width()
        mheight = self.frameGeometry().height()
        ratio = 1.778
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
            layout.addRow("Saturation", self.saturationSlider)

            btn = QPushButton("Reset Colors")
            btn.setIcon(QIcon.fromTheme("preferences-color"))
            layout.addRow(btn)

            button = QPushButton("Close")
            button.setIcon(QIcon.fromTheme("ok"))
            layout.addRow(button)

            self.colorDialog = QDialog(self)
            self.colorDialog.setWindowTitle("Color Options")
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
