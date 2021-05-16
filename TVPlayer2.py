#!/usr/bin/python3
# -*- coding: utf-8 -*-
#############################################################################
from PyQt5.QtCore import (QPoint, Qt, QUrl, QProcess, QFile, QDir, QSettings, 
                          QStandardPaths, QRect)
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import (QAction, QApplication, QMainWindow, QMessageBox, 
                             QMenu, QInputDialog, QLineEdit, QFileDialog, 
                             QFormLayout, QSlider, QPushButton, QDialog, QWidget)

import mpv
import os
import sys
from datetime import datetime
import locale
from subprocess import check_output, STDOUT, CalledProcessError

mytv = "tv-symbolic"
mybrowser = "video-television"
ratio = 1.777777778


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # lists
        self.file_list = []
        for entry in os.scandir(os.path.dirname(sys.argv[0])):
            if entry.is_file():
                if entry.name.endswith(".txt") and not entry.name == "mychannels.txt":
                    self.file_list.append(entry.name)
        self.file_list.sort(key=str.lower)
        flist = '\n'.join(self.file_list)
        print(f'found lists:\n{flist}')
        
        check = self.check_libmpv("libmpv")
        if not check:
            print("libmpv not found\n")
            self.msgbox("libmpv not found\nuse 'sudo apt-get install libmpv1'")
            sys.exit()
        else:
            print("found libmpv")
            
        self.check_mpv("mpv")
        
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setStyleSheet("QMainWindow {background-color: 'black';}")
        self.osd_font_size = 28
        self.colorDialog = None
        self.settings = QSettings("TVPlayer2", "settings")
        self.own_list = []
        self.own_key = 0
        self.default_key = 0
        self.default_list = []
        self.urlList = []
        self.channel_list = []
        self.channels_files_list = []
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
        self.mychannels = []
        self.channels_menu = QMenu()

        self.processR = QProcess()
        self.processR.started.connect(self.getPIDR)
        self.processR.finished.connect(self.timer_finished)
        self.processR.isRunning = False
        
        self.pid = None
        
        self.processW = QProcess()
        self.processW.started.connect(self.getPIDW)
        self.processW.finished.connect(self.recfinished)
        self.processW.isRunning = False
                         
        self.container = QWidget(self)
        self.setCentralWidget(self.container)
        self.container.setAttribute(Qt.WA_DontCreateNativeAncestors)
        self.container.setAttribute(Qt.WA_NativeWindow)
        self.container.setContextMenuPolicy(Qt.CustomContextMenu);
        self.container.customContextMenuRequested[QPoint].connect(self.contextMenuRequested)
        self.setAcceptDrops(True)
        
        self.mediaPlayer = mpv.MPV(log_handler=self.logger,
                           input_cursor=False,
                           osd_font_size=self.osd_font_size,
                           cursor_autohide=2000, 
                           cursor_autohide_fs_only=True,
                           osd_color='#d3d7cf',
                           osd_blur=2,
                           osd_bold=True,
                           wid=str(int(self.container.winId())), 
                           config=False, 
                           profile="libmpv",
                           hwdec=False,
                           vo="x11") 

                         
        self.mediaPlayer.set_loglevel('fatal')
        
        self.own_file = "mychannels.txt"
        if os.path.isfile(self.own_file):
            self.mychannels = open(self.own_file).read()
            ### remove empty lines
            self.mychannels = os.linesep.join([s for s in self.mychannels.splitlines() if s])
            with open(self.own_file, 'w') as f:
                f.write(self.mychannels)

        self.fullscreen = False

        self.setMinimumSize(320, 180)
        self.setGeometry(100, 100, 480, round(480 / ratio))

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.setWindowTitle("TV Player & Recorder")
        self.setWindowIcon(QIcon.fromTheme("multimedia-video-player"))

        self.myinfo = """<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><!--StartFragment--><span style=" font-size:xx-large; font-weight:600;">TVPlayer2</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">©2020<br /><a href="https://github.com/Axel-Erfurt"><span style=" color:#0000ff;">Axel Schneider</span></a></p>
<h3 style=" margin-top:14px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:large; font-weight:600;">Keyboard shortcuts:</span></h3>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">q = Exit<br />f = toggle Fullscreen</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">u = Play url from the clipboard</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Mouse wheel = change window size</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">↑ = volume up</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">↓ = volume down</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">m = Ton an/aus</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">h = Mouse pointer on / off</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">r = Recording with timer</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">w = Recording without timer<br />s = Stop recording</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">--------------------------------------</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">1 bis 0 = own channels (1 to 10)</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">→ = Channels +</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">+ = own channel +</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">← = Channel -</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">- = own channel -</p>"""
        print("Welcome to the TV Player & Recorder")
        if self.is_tool("ffmpeg"):
            print("found ffmpeg\nrecording available")
            self.recording_enabled = True
        else:
            self.msgbox("ffmpeg not foundn\n no recording available")
            
        self.show()
        self.readSettings()            
            
        self.createMenu()
        
        
    def check_libmpv(self, mlib):
        cmd =  f'ldconfig -p | grep {mlib}'
        
        try:
            result = check_output(cmd, stderr=STDOUT, shell=True).decode("utf-8")
        except CalledProcessError:
            return False
            
        if not mlib in result:
            return False
        else:
            return True
            
    def check_mpv(self, mlib):
        cmd =  f'pip3 list | grep {mlib}'
        
        try:
            result = check_output(cmd, stderr=STDOUT, shell=True).decode("utf-8")
            
            if not mlib in result:
                return False
            else:
                return True
            
        except CalledProcessError as exc:
            result = exc.output
            return False
        
    def logger(self, loglevel, component, message):
        print('[{}] {}: {}'.format(loglevel, component, message), file=sys.stderr)
        
    def editOwnChannels(self):
        mfile = f"{os.path.join(os.path.dirname(sys.argv[0]))}/mychannels.txt"
        QDesktopServices.openUrl(QUrl(f"file://{mfile}"))
        
    def addToOwnChannels(self):
        k = "Name"
        dlg = QInputDialog()
        myname, ok = dlg.getText(self, 'Dialog', 'Name:', QLineEdit.Normal, k, Qt.Dialog)
        if ok:
            if os.path.isfile(self.own_file):
                with open(self.own_file, 'a') as f:
                    f.write(f"\n{myname},{self.link}")
                    self.channelname = myname
            else:
                self.msgbox(f"{self.own_file} does not exist!")
            
    def readSettings(self):
        print("reading configuation ...")
        if self.settings.contains("geometry"):
            self.setGeometry(self.settings.value("geometry", QRect(26, 26, 200, 200)))
        else:
            self.setGeometry(100, 100, 480, 480 / ratio)
        if self.settings.contains("lastUrl") and self.settings.contains("lastName"):
            self.link = self.settings.value("lastUrl")
            self.channelname = self.settings.value("lastName")
            self.mediaPlayer.show_text(self.channelname, duration="4000", level=None) 
            self.mediaPlayer.play(self.link)
            print(f"current station: {self.channelname}\nURL: {self.link}")
        else:
            if len(self.own_list) > 0:
                self.play_own(0)
        if self.settings.contains("volume"):
            vol = self.settings.value("volume")
            print("set volume to", vol)
            self.mediaPlayer.volume = (int(vol))
        
    def writeSettings(self):
        print("writing configuation file ...")
        self.settings.setValue("geometry", self.geometry())
        self.settings.setValue("lastUrl", self.link)
        self.settings.setValue("lastName", self.channelname)
        self.settings.setValue("volume", self.mediaPlayer.volume)
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
        
        ### other lists
        for x in range(len(self.file_list)):
            newMenu = self.channels_menu.addMenu(os.path.splitext(os.path.basename(self.file_list[x]))[0])
            newMenu.setIcon(QIcon.fromTheme(mytv))
            channelList = open(self.file_list[x], 'r').read().splitlines()
            for ch in channelList:
                name = ch.partition(",")[0]
                url = ch.partition(",")[2]
                self.channel_list.append(f"{name},{url}")
                self.own_list.append(f"{name},{url}")
                a = QAction(name, self, triggered=self.playTV)
                a.setIcon(QIcon.fromTheme(mybrowser))
                a.setData(url)
                newMenu.addAction(a)            
        #############################
        
        if self.recording_enabled:
            self.channels_menu.addSection("Recording")
    
            self.tv_record = QAction(QIcon.fromTheme("media-record"), "record with Timer (r)", triggered = self.record_with_timer)
            self.channels_menu.addAction(self.tv_record)

            self.tv_record2 = QAction(QIcon.fromTheme("media-record"), "record without Timer (w)", triggered = self.record_without_timer)
            self.channels_menu.addAction(self.tv_record2)

            self.tv_record_stop = QAction(QIcon.fromTheme("media-playback-stop"), "stop recording (s)", triggered = self.stop_recording)
            self.channels_menu.addAction(self.tv_record_stop)
    
            self.channels_menu.addSeparator()

        self.about_action = QAction(QIcon.fromTheme("help-about"), "Info (i)", triggered = self.handleAbout, shortcut = "i")
        self.channels_menu.addAction(self.about_action)

        self.channels_menu.addSeparator()

        self.url_action = QAction(QIcon.fromTheme("browser"), "play URL from clipboard (u)", triggered = self.playURL)
        self.channels_menu.addAction(self.url_action)
        
        self.channels_menu.addSection("Settings")

        self.color_action = QAction(QIcon.fromTheme("preferences-color"), "Color Settings (c)", triggered = self.showColorDialog)
        self.channels_menu.addAction(self.color_action)

        self.channels_menu.addSeparator()

        self.channels_menu.addSeparator()

        self.channels_menu.addSection("add / edit Channels")        
        self.addChannelAction = QAction(QIcon.fromTheme("add"), "add current channel", triggered = self.addToOwnChannels)
        self.channels_menu.addAction(self.addChannelAction)
        
        self.editChannelAction = QAction(QIcon.fromTheme("text-editor"), "edit own channels", triggered = self.editOwnChannels)
        self.channels_menu.addAction(self.editChannelAction)
        
        self.channels_menu.addSeparator()
        
        self.quit_action = QAction(QIcon.fromTheme("application-exit"), "Exit (q)", triggered = self.handleQuit)
        self.channels_menu.addAction(self.quit_action)
        
    def showTime(self):
        t = str(datetime.now())[11:16]
        self.mediaPlayer.show_text(t, duration="4000", level=None) 

         
    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0].toString()
            print(f"new link dropped: '{url}'")
            self.link = url.strip()
            self.mediaPlayer.stop()
            self.mediaPlayer.play(self.link)
        elif event.mimeData().hasText():
            mydrop =  event.mimeData().text().strip()
            if ("http") in mydrop:
                print(f"new link dropped: '{mydrop}'")
                self.link = mydrop
                self.mediaPlayer.play(self.link)
        event.acceptProposedAction()
        

    def recfinished(self):
        print("recording will be stopped")

    def is_tool(self, name):
        tool = QStandardPaths.findExecutable(name)
        if tool != "":
            return True
        else:
            return False

    def getPIDR(self):
        print("pid", self.processR.processId())
        self.pid = self.processR.processId()

    def getPIDW(self):
        print("pid", self.processW.processId())
        self.pid = self.processW.processId()
        
    def record_without_timer(self):
        if not self.recording_enabled == False:
            if QFile(self.outfile).exists:
                print("delete file " + self.outfile) 
                QFile(self.outfile).remove
            else:
                print("the file " + self.outfile + " does not exist") 
            self.recname = self.channelname
            print("recording in file /tmp/TV.mp4")
            self.mediaPlayer.show_text("record without timer", duration="3000", level=None) 
            self.is_recording = True
            self.recordChannelW()

    def record_with_timer(self):
        if not self.recording_enabled == False:
            if QFile(self.outfile).exists:
                print("lösche Datei " + self.outfile) 
                QFile(self.outfile).remove
            else:
                print("the file " + self.outfile + " does not exist") 
            infotext = '<i>temporary recording in file: /tmp/TV.mp4</i> \
                            <br><b><font color="#a40000";>The storage location and file name are determined\nafter the recording is finished.</font></b> \
                            <br><br><b>Example:</b><br>60s (60 seconds)<br>120m (120 minutes)'
            dlg = QInputDialog()
            tout, ok = dlg.getText(self, 'Duration:', infotext, \
                                    QLineEdit.Normal, "90m", Qt.Dialog)
            if ok:
                self.tout = str(tout)
                self.is_recording = True
                self.recordChannel()
            else:
                print("recording cancelled")

    def recordChannel(self):
        self.processR.isRunning = True
        self.recname = self.channelname
        cmd = f'timeout {str(self.tout)} ffmpeg -y -i {self.link.replace("?sd=10&rebase=on", "")} -bsf:a aac_adtstoasc -vcodec copy -c copy -crf 50 "{self.outfile}"'
        print("recording in /tmp with timeout: " + str(self.tout))
        self.mediaPlayer.show_text(f"Recording with timer {str(self.tout)}", duration="3000", level=None) 
        self.is_recording = True
        self.processR.start(cmd)
        
    def recordChannelW(self):
        self.processW.isRunning = True
        self.recname = self.channelname
        cmd = f'ffmpeg -y -i {self.link.replace("?sd=10&rebase=on", "")} -bsf:a aac_adtstoasc -vcodec copy -c copy -crf 50 "{self.outfile}"'
        self.mediaPlayer.show_text("Recording", duration="3000", level=None) 
        self.is_recording = True
        self.processW.start(cmd)
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
                    "cannot write file %s:\n%s." % (path, infile.errorString()))
            if infile.exists:
                infile.remove()

    def stop_recording(self):
        print("StateR:", self.processR.state())
        print("StateW:", self.processW.state())
        if self.is_recording == True:
            if self.processW.isRunning:
                print("recording will be stopped")
                cmd = f"kill -9 {self.pid}"
                print(cmd, "(stop ffmpeg)")
                QProcess().execute(cmd)
                if self.processW.exitStatus() == 0:
                    self.processW.isRunning = False
                    self.saveMovie()
        else:
            print("no recording")

    def timer_finished(self):
        print("Timer ended\nrecording will be stopped")
        self.processR.isRunning = False
        self.is_recording = False
        self.saveMovie()

    def playURL(self):
        clip = QApplication.clipboard()
        self.link = clip.text().strip()
        self.mediaPlayer.play(self.link)

    def handleError(self, loglevel, message):
        print('{}: {}'.format(loglevel, message), file=sys.stderr)

    def handleMute(self):
        if not self.mediaPlayer.mute:
            self.mediaPlayer.mute = True
            print("muted")
        else:
            self.mediaPlayer.mute = False
            print("not muted")

    def handleAbout(self):
        QMessageBox.about(self, "TVPlayer2", self.myinfo)

    def handleFullscreen(self):
        if self.fullscreen == True:
            self.fullscreen = False
            print("no fullscreen")
        else:
            self.rect = self.geometry()
            self.showFullScreen()
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.fullscreen = True
            print("fullscreen")
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
        self.mediaPlayer.quit
        self.writeSettings()
        print("Goodbye ...")
        app.quit()
        sys.exit()

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
            self.record_with_timer()
        elif e.key() == Qt.Key_S:
            self.stop_recording()
        elif e.key() == Qt.Key_T:
            self.showTime()
        elif e.key() == Qt.Key_E:
            self.getEPG_detail()
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
        elif e.key() == Qt.Key_Right:
            self.play_next(self.default_key + 1)
        elif e.key() == Qt.Key_Plus:
            self.play_own(self.own_key + 1)
        elif e.key() == Qt.Key_Left:
            self.play_next(self.default_key - 1)
        elif e.key() == Qt.Key_Minus:
            if not self.own_key == 0:
                self.play_own(self.own_key - 1)
        elif e.key() == Qt.Key_Up:
            if self.mediaPlayer.volume < 160:
                self.mediaPlayer.volume = (self.mediaPlayer.volume + 5)
                print("Volume:", self.mediaPlayer.volume)
                self.mediaPlayer.show_text(f"Volume: {self.mediaPlayer.volume}")
        elif e.key() == Qt.Key_Down:
            if self.mediaPlayer.volume > 5:
                self.mediaPlayer.volume = (self.mediaPlayer.volume - 5)
                print("Volume:", self.mediaPlayer.volume)
                self.mediaPlayer.show_text(f"Volume: {self.mediaPlayer.volume}")
        else:
            e.accept()

    def contextMenuRequested(self, point):
        self.channels_menu.exec_(self.mapToGlobal(point))
        
    def playFromKey(self, url):
        self.link = url
        self.mediaPlayer.play(self.link)
                
    def playTV(self):
        action = self.sender()
        self.link = action.data().replace("\n", "")
        self.channelname = action.text()
        self.mediaPlayer.show_text(self.channelname, duration="4000", level=None) 
        if self.channelname in self.channel_list:
            self.default_key = self.channel_list.index(self.channelname)
        else:
            self.own_key = self.own_list.index(f"{self.channelname},{self.link}")
        print(f"current channel: {self.channelname}\nURL: {self.link}")
        self.mediaPlayer.play(self.link)
        
    def play_own(self, channel):
        if not channel > len(self.own_list) - 1:
            self.own_key = channel
            self.link = self.own_list[channel].split(",")[1]
            self.channelname = self.own_list[channel].split(",")[0]
            self.mediaPlayer.show_text(self.channelname, duration="4000", level=None) 
            print("own channel:", self.channelname, "\nURL:", self.link)
            self.mediaPlayer.play(self.link)
        else:
            print(f"channel {channel} not exists")
            
            
    def play_next(self, channel):
        if not channel > len(self.default_list) - 1:
            self.default_key = channel
            self.link = self.default_list[channel].split(",")[1]
            self.channelname = self.default_list[channel].split(",")[0]
            self.mediaPlayer.show_text(self.channelname, duration="4000", level=None) 
            print(f"current channel: {self.channelname}\nURL: {self.link}")
            self.mediaPlayer.play(self.link)
        else:
            self.play_next(0)
            
    def play_previous(self, channel):
        if not channel == 0:
            self.default_key = channel
            self.link = self.default_list[channel].split(",")[1]
            self.channelname = self.default_list[channel].split(",")[0]
            self.mediaPlayer.show_text(self.channelname, duration="4000", level=None) 
            print(f"current channel: {self.channelname}\nURL: {self.link}")
            self.mediaPlayer.play(self.link)
        else:
            self.play_next(len(self.default_list))

    def closeEvent(self, event):
        event.accept()

    def msgbox(self, message):
        QMessageBox.warning(self, "Message", message)
        
    def wheelEvent(self, event):
        mwidth = self.frameGeometry().width()
        mscale = round(event.angleDelta().y() / 6)
        self.resize(mwidth + mscale, round((mwidth + mscale) / ratio))
        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() \
                      - QPoint(round(self.frameGeometry().width() / 2), \
                               round(self.frameGeometry().height() / 2)))
            event.accept()
            
    def setBrightness(self):
        self.mediaPlayer.brightness = self.brightnessSlider.value()
        
    def setContrast(self):
        self.mediaPlayer.contrast = self.contrastSlider.value()
        
    def setHue(self):
        self.mediaPlayer.hue = self.hueSlider.value()

    def setSaturation(self):
        self.mediaPlayer.saturation = self.saturationSlider.value()
        
    def showColorDialog(self):
        if self.colorDialog is None:
            self.brightnessSlider = QSlider(Qt.Horizontal)
            self.brightnessSlider.setRange(-100, 100)
            self.brightnessSlider.setValue(self.mediaPlayer.brightness)
            self.brightnessSlider.valueChanged.connect(self.setBrightness)

            self.contrastSlider = QSlider(Qt.Horizontal)
            self.contrastSlider.setRange(-100, 100)
            self.contrastSlider.setValue(self.mediaPlayer.contrast)
            self.contrastSlider.valueChanged.connect(self.setContrast)
            
            self.hueSlider = QSlider(Qt.Horizontal)
            self.hueSlider.setRange(-100, 100)
            self.hueSlider.setValue(self.mediaPlayer.hue)
            self.hueSlider.valueChanged.connect(self.setHue)

            self.saturationSlider = QSlider(Qt.Horizontal)
            self.saturationSlider.setRange(-100, 100)
            self.saturationSlider.setValue(self.mediaPlayer.saturation)
            self.saturationSlider.valueChanged.connect(self.setSaturation)

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
        self.mediaPlayer.brightness = (0)

        self.contrastSlider.setValue(0)
        self.mediaPlayer.contrast = (0)

        self.saturationSlider.setValue(0)
        self.mediaPlayer.saturation = (0)

        self.hueSlider.setValue(0)
        self.mediaPlayer.hue = (0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    locale.setlocale(locale.LC_NUMERIC, 'C')
    mainWin = MainWindow()
    sys.exit(app.exec_())
