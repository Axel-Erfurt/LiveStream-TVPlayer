#!/usr/bin/python3
# -*- coding: utf-8 -*-
#############################################################################
from PyQt5.QtCore import (QPoint, Qt, QUrl, QProcess, QFile, QDir, QSettings, 
                          QStandardPaths, QFileInfo, QCoreApplication, QRect)
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import (QAction, QApplication, QMainWindow, QMessageBox, 
                             QMenu, QInputDialog, QLineEdit, QFileDialog, QLabel, 
                             QFormLayout, QSlider, QPushButton, QDialog)
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget

import os
import sys
from requests import get, post, request
import time

mytv = "tv-symbolic"
mybrowser = "browser"
ratio = 1.777777778

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.settings = QSettings("TVPlayer3", "settings")
        self.colorDialog = None
        self.own_list = []
        self.own_key = 0
        self.default_key = 0
        self.default_list = []
        self.urlList = []
        self.channel_list = []
        self.link = ""
        self.menulist = []
        self.recording_enabled = False
        self.is_recording = False
        self.recname = ""
        self.timeout = "60"
        self.tout = 60
        self.outfile = "/tmp/TV.mp4"
        self.channelname = ""
        self.mychannels = []
        self.channels_menu = QMenu()

        self.process = QProcess()
        self.process.started.connect(self.getPID)
        self.process.finished.connect(self.timer_finished)
        self.process.finished.connect(self.recfinished)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.StreamPlayback)
        self.mediaPlayer.service().requestControl('org.qt-project.qt.mediastreamscontrol/5.0')
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
        
        self.own_file = f"{os.path.dirname(sys.argv[0])}/tv_channels.txt"
        print(self.own_file)
        if os.path.isfile(self.own_file):
            self.mychannels = open(self.own_file).read()
            ### remove empty lines
            self.mychannels = os.linesep.join([s for s in self.mychannels.splitlines() if s])
            with open(self.own_file, 'w') as f:
                f.write(self.mychannels)

        self.fullscreen = False
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setMinimumSize(320, 180)
        self.setGeometry(100, 100, 480, round(480 / ratio))

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.setWindowTitle("TV Player & Recorder")
        self.setWindowIcon(QIcon.fromTheme("multimedia-video-player"))

        self.myinfo = """<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><!--StartFragment--><span style=" font-size:xx-large; font-weight:600;">TVPlayer3</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:xx-large; font-weight:600;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">©2020<br /><a href="https://github.com/Axel-Erfurt"><span style=" text-decoration: underline; color:#0000ff;">Axel Schneider</span></a></p>
<h3 style=" margin-top:14px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:large; font-weight:600;">Shortcuts:</span></h3>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">q = Exit<br />f = toggle Fullscreen</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">u = play Url from Clipboard</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">wheel = change screen size</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">↑ = more volume</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">↓ = less volume</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">m = mute / unmute</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">h = show / hide mouse pointer</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">r = record with timer</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">w = record without timer<br />s = stop recording</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">--------------------------------------</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">1 bis 0 = channels (1 bis 10)</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">→ = channel +</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">+ = channel +</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">← = channel -</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">- = channel -"""
        print("Welcome")
        if self.is_tool("streamlink"):
            print("found streamlink \nrecording available")
            self.recording_enabled = True
        else:
            self.msgbox("streamlink not found\nno recording available")
            
        self.createMenu()
        self.readSettings()
        self.show()

        
    def editOwnChannels(self):
        QDesktopServices.openUrl(QUrl(f"file://{self.own_file}"))
        
    def addToOwnChannels(self):
        k = "Name"
        dlg = QInputDialog()
        myname, ok = dlg.getText(self, 'Dialog', 'insert name', QLineEdit.Normal, k, Qt.Dialog)
        if ok:
            if os.path.isfile(self.own_file):
                with open(self.own_file, 'a') as f:
                    f.write(f"\n{myname},{self.link}")
                    self.channelname = myname
            else:
                self.msgbox(f"{self.own_file} existiert nicht!")
            
    def readSettings(self):
        print("reading config file ...")
        if self.settings.contains("geometry"):
            self.setGeometry(self.settings.value("geometry", QRect(26, 26, 200, 200)))
        else:
            self.setGeometry(100, 100, 480, 480 / ratio)
        if self.settings.contains("lastUrl") and self.settings.contains("lastName"):
            self.link = self.settings.value("lastUrl")
            self.channelname = self.settings.value("lastName")
            if not self.link.startswith("http"):
                self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.link)))
            else:
                self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
            self.mediaPlayer.play()
            print("aktueller Sender:", self.channelname, "\nURL:", self.link)
        else:
            if len(self.own_list) > 0:
                self.play_own(0)

        if self.settings.contains("volume"):
            vol = self.settings.value("volume")
            print("volume set to", vol)
            self.mediaPlayer.setVolume(int(vol))

                
    def writeSettings(self):
        print("writing config file ...")
        self.settings.setValue("geometry", self.geometry())
        self.settings.setValue("lastUrl", self.link)
        self.settings.setValue("lastName", self.channelname)
        self.settings.setValue("volume", self.mediaPlayer.volume())
        self.settings.sync()
        
    def mouseDoubleClickEvent(self, event):
        self.handleFullscreen()
        event.accept()
            
    def getBufferStatus(self):
        print(self.mediaPlayer.bufferStatus())

    def createMenu(self):
        myMenu = self.channels_menu.addMenu("Channels")
        myMenu.setIcon(QIcon.fromTheme(mytv))
        if len(self.mychannels) > 0:
            for ch in self.mychannels.splitlines():
                name = ch.partition(",")[0]
                url = ch.partition(",")[2]
                self.own_list.append(f"{name},{url}")
                a = QAction(name, self, triggered=self.playTV)
                a.setIcon(QIcon.fromTheme(mybrowser))
                a.setData(url)
                myMenu.addAction(a)
        
        #############################
        
        if self.recording_enabled:
            self.channels_menu.addSection("Recording")
    
            self.tv_record = QAction(QIcon.fromTheme("media-record"), "record with timer (r)", triggered = self.record_with_timer)
            self.channels_menu.addAction(self.tv_record)

            self.tv_record2 = QAction(QIcon.fromTheme("media-record"), "record without timer (w)", triggered = self.record_without_timer)
            self.channels_menu.addAction(self.tv_record2)

            self.tv_record_stop = QAction(QIcon.fromTheme("media-playback-stop"), "stop recording (s)", triggered = self.stop_recording)
            self.channels_menu.addAction(self.tv_record_stop)
    
            self.channels_menu.addSeparator()

        self.about_action = QAction(QIcon.fromTheme("help-about"), "Info (i)", triggered = self.handleAbout, shortcut = "i")
        self.channels_menu.addAction(self.about_action)

        self.channels_menu.addSeparator()

        self.url_action = QAction(QIcon.fromTheme("browser"), "play URL from Clipboard (u)", triggered = self.playURL)
        self.channels_menu.addAction(self.url_action)

        self.channels_menu.addSection("Settings")

        self.color_action = QAction(QIcon.fromTheme("preferences-color"), "Color Settings (c)", triggered = self.showColorDialog)
        self.channels_menu.addAction(self.color_action)

        self.channels_menu.addSeparator()

        self.channels_menu.addSection("Channel Editor")        
        self.addChannelAction = QAction(QIcon.fromTheme("add"), "add current channel", triggered = self.addToOwnChannels)
        self.channels_menu.addAction(self.addChannelAction)
        
        self.editChannelAction = QAction(QIcon.fromTheme("text-editor"), "edit channels", triggered = self.editOwnChannels)
        self.channels_menu.addAction(self.editChannelAction)
        
        self.channels_menu.addSeparator()
        
        self.quit_action = QAction(QIcon.fromTheme("application-exit"), "Exit (q)", triggered = self.handleQuit)
        self.channels_menu.addAction(self.quit_action)
         
    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0].toString().replace("https", "http")
            print("neue URL abgelegt = ", url)
            self.link = url
            self.mediaPlayer.stop()
            self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
            self.mediaPlayer.play()
        elif event.mimeData().hasText():
            mydrop =  event.mimeData().text()
            if mydrop.startswith("http"):
                print("new link was filed:", mydrop)
                self.link = mydrop.replace("https", "http")
                self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
                self.mediaPlayer.play()
        event.acceptProposedAction()
        

    def recfinished(self):
        print("recording finished")

    def is_tool(self, name):
        tool = QStandardPaths.findExecutable(name)
        if tool != "":
            return True
        else:
            return False

    def getPID(self):
        print(self.process.pid(), self.process.processId() )

    def record_without_timer(self):
        if not self.recording_enabled == False:
            if QFile(self.outfile).exists:
                print("deleting file " + self.outfile) 
                QFile(self.outfile).remove
            else:
                print("file " + self.outfile + " does not exist") 
            self.recname = self.channelname
            self.showLabel()
            print("recording to /tmp")
            self.is_recording = True
            cmd = 'streamlink --force ' + self.link.replace("?sd=10&rebase=on", "") + ' best -o ' + self.outfile
            print(cmd)
            self.process.startDetached(cmd)

    def record_with_timer(self):
        if not self.recording_enabled == False:
            if QFile(self.outfile).exists:
                print("deleting file " + self.outfile) 
                QFile(self.outfile).remove
            else:
                print("the file " + self.outfile + " does not exist") 
            infotext = '<i>temporary recording to file: /tmp/TV.mp4</i> \
                            <br><b><font color="#a40000";>The storage location and file name are set after the recording is finished.</font></b> \
                            <br><br><b>Example:</b><br>60s (60 seconds)<br>120m (120 minutes)'
            dlg = QInputDialog()
            tout, ok = dlg.getText(self, 'Länge der Aufnahme', infotext, \
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
        self.fileSave()

    def fileSave(self):
        infile = QFile(self.outfile)
        path, _ = QFileDialog.getSaveFileName(self, "Save as...", QDir.homePath() + "/Videos/" + self.recname + ".mp4",
            "Video (*.mp4)")
        if os.path.exists(path):
            os.remove(path)
        if (path != ""):
            savefile = path
            if QFile(savefile).exists:
                QFile(savefile).remove()
            print("saving " + savefile)
            if not infile.copy(savefile):
                QMessageBox.warning(self, "Error",
                    "can not write %s:\n%s." % (path, infile.errorString()))
            if infile.exists:
                infile.remove()
            self.lbl.hide()
        else:
            self.lbl.hide()

    def stop_recording(self):
        print(self.process.state())
        if self.is_recording == True:
            print("stopping recording")
            QProcess().execute("killall streamlink")
            self.process.kill()
            self.is_recording = False
            if self.process.exitStatus() == 0:
                self.saveMovie()
        else:
            print("nothing is being recorded at the moment")
            self.lbl.hide()
 
    def rec_finished(self):
        print("Recording ended")
        self.process.kill()

    def timer_finished(self):
        print("timer ended")
        self.is_recording = False
        self.process.kill()
        print("Recording ended")

        self.lbl.hide()
        self.saveMovie()

    def playURL(self):
        clip = QApplication.clipboard()
        self.link = clip.text().replace("https", "http")
        if not self.link.startswith("http"):
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.link)))
        else:
            self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
        self.mediaPlayer.play()

    def handleError(self):
        if not "Should no longer be called" in self.mediaPlayer.errorString():
            print("Error: " + self.mediaPlayer.errorString())
            self.msgbox("Error: " + self.mediaPlayer.errorString())

    def handleMute(self):
        if not self.mediaPlayer.isMuted():
            self.mediaPlayer.setMuted(True)
        else:
            self.mediaPlayer.setMuted(False)

    def handleAbout(self):
        QMessageBox.about(self, "TVPlayer3", self.myinfo)

    def handleFullscreen(self):
        if self.fullscreen == True:
            self.fullscreen = False
            print("no fullscreen")
        else:
            self.rect = self.geometry()
            self.showMaximized()
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.fullscreen = True
            print("fullscreen on")
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
        self.writeSettings()
        print("Goodbye ...")
        app.quit()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Q:
            self.handleQuit()
        elif e.key() == Qt.Key_H:
            self.handleCursor()
        elif e.key() == Qt.Key_P:
            self.tv_programm_tag()
        elif e.key() == Qt.Key_J:
            self.tv_programm_now()
        elif e.key() == Qt.Key_D:
            self.tv_programm_later()
        elif e.key() == Qt.Key_F:
            self.handleFullscreen()
        elif e.key() == Qt.Key_M:
            self.handleMute()
        elif e.key() == Qt.Key_I:
            self.handleAbout()
        elif e.key() == Qt.Key_U:
            self.playURL()
        elif e.key() == Qt.Key_R:
            self.record_with_timer()
        elif e.key() == Qt.Key_S:
            self.stop_recording()
        elif e.key() == Qt.Key_W:
            self.record_without_timer()
        elif e.key() == Qt.Key_C:
            self.showColorDialog()
        elif e.key() == Qt.Key_1:
            self.play_own(0)
        elif e.key() == Qt.Key_2:
            self.play_own(1)
        elif e.key() == Qt.Key_3:
            self.play_own(2)
        elif e.key() == Qt.Key_4:
            self.play_own(3)
        elif e.key() == Qt.Key_5:
            self.play_own(4)
        elif e.key() == Qt.Key_6:
            self.play_own(5)
        elif e.key() == Qt.Key_7:
            self.play_own(6)
        elif e.key() == Qt.Key_8:
            self.play_own(7)
        elif e.key() == Qt.Key_9:
            self.play_own(8)
        elif e.key() == Qt.Key_0:
            self.play_own(9)
        elif e.key() == Qt.Key_A:
            self.playARD()
        elif e.key() == Qt.Key_Z:
            self.playZDF()
        elif e.key() == Qt.Key_T:
            self.playTagesschau()
        elif e.key() == Qt.Key_Right:
            self.play_own(self.own_key + 1)
        elif e.key() == Qt.Key_Plus:
            self.play_own(self.own_key + 1)
        elif e.key() == Qt.Key_Left:
            if not self.own_key == 0:
                self.play_own(self.own_key - 1)
        elif e.key() == Qt.Key_Minus:
            if not self.own_key == 0:
                self.play_own(self.own_key - 1)
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

    def contextMenuRequested(self, point):
        self.channels_menu.exec_(self.mapToGlobal(point))
        
    def playFromKey(self, url):
        self.mediaPlayer.setMedia(QMediaContent(QUrl(url)))
        self.mediaPlayer.play()

    def showLabel(self):
        self.lbl.show()

    def playTV(self):
        if not self.is_recording:
            self.lbl.hide()
        action = self.sender()
        self.link = action.data().replace("\n", "")
        self.channelname = action.text()
        if self.channelname in self.channel_list:
            self.default_key = self.channel_list.index(self.channelname)
        else:
            self.own_key = self.own_list.index(f"{self.channelname},{self.link}")
        print("current channel:", self.channelname, "\nURL:", self.link)
        if not self.link.startswith("http"):
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.link)))
        else:
            self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
        self.mediaPlayer.play()
        

    def play_own(self, channel):
        if not channel > len(self.own_list) - 1:
            if not self.is_recording:
                self.lbl.hide()
            self.own_key = channel
            self.link = self.own_list[channel].split(",")[1]
            self.channelname = self.own_list[channel].split(",")[0]
            print("channel:", self.channelname, "\nURL:", self.link)
            if not self.link.startswith("http"):
                self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.link)))
            else:
                self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
            self.mediaPlayer.play()
        else:
            print(f"Kanal {channel} ist nicht vorhanden")
            
            
    def play_next(self, channel):
        if not channel > len(self.default_list) - 1:
            if not self.is_recording:
                self.lbl.hide()
            self.default_key = channel
            self.link = self.default_list[channel].split(",")[1]
            self.channelname = self.default_list[channel].split(",")[0]
            print("current channel:", self.channelname, "\nURL:", self.link)
            self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
            self.mediaPlayer.play()
        else:
            self.play_next(0)
            
    def play_previous(self, channel):
        if not channel == 0:
            if not self.is_recording:
                self.lbl.hide()
            self.default_key = channel
            self.link = self.default_list[channel].split(",")[1]
            self.channelname = self.default_list[channel].split(",")[0]
            print("current channel:", self.channelname, "\nURL:", self.link)
            self.mediaPlayer.setMedia(QMediaContent(QUrl(self.link)))
            self.mediaPlayer.play()
        else:
            self.play_next(len(self.default_list))

    def closeEvent(self, event):
        event.accept()

    def msgbox(self, message):
        QMessageBox.warning(self, "Message", message)
        
    def programmbox(self, title, message):
        m = QMessageBox(QMessageBox.NoIcon, title, message)
        m.exec()
        
    def wheelEvent(self, event):
        mwidth = self.frameGeometry().width()
        mscale = event.angleDelta().y() / 6
        self.resize(mwidth + mscale, round((mwidth + mscale) / ratio))
        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() \
                      - QPoint(round(self.frameGeometry().width() / 2), \
                               round(self.frameGeometry().height() / 2)))
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

            btn = QPushButton("reset")
            btn.setIcon(QIcon.fromTheme("preferences-color"))
            layout.addRow(btn)

            button = QPushButton("close")
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
    sys.exit(app.exec_())
