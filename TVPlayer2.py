#!/usr/bin/python3
# -*- coding: utf-8 -*-
#############################################################################

from PyQt5.QtCore import (QPoint, QRect, Qt, QUrl)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QMainWindow, QMessageBox, QMenu, QWidget)
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
import m3u8
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.urlList = []
        self.resolutions = ["320", "480", "640", "960", "1280"]
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.StreamPlayback)
        self.mediaPlayer.setVolume(95)
        self.mediaPlayer.error.connect(self.handleError)
        self.videoWidget = QVideoWidget(self)
        self.videoWidget.setAspectRatioMode(1)
        self.videoWidget.setContextMenuPolicy(Qt.CustomContextMenu);
        self.videoWidget.customContextMenuRequested[QPoint].connect(self.contextMenuRequested)
        self.setCentralWidget(self.videoWidget)
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        try:
            self.root = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            import sys
            self.root = os.path.dirname(os.path.abspath(sys.argv[0]))

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

        self.myinfo = "TV-Player\n©2018\nAxel Schneider\n\nq = Exit\nf = toggle Fullscreen\n"

        self.getLists()
        self.playFirst()

    def playURL(self):
        clip = QApplication.clipboard()
        myurl = clip.text()
        self.mediaPlayer.setMedia(QMediaContent(QUrl(myurl)))
        self.mediaPlayer.play()

    def handleError(self):
        print("Error: " + self.mediaPlayer.errorString())

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
            self.fullscreen = True
            print("Fullscreen entered")
        if self.fullscreen == False:
            self.showNormal()
            self.setGeometry(self.rect)
    
    def handleQuit(self):
        self.mediaPlayer.stop()
        print("Goodbye ...")
        app.quit()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Q:
            self.handleQuit()
        elif e.key() == Qt.Key_F:
            self.handleFullscreen()
        elif e.key() == Qt.Key_M:
            self.handleMute()
        elif e.key() == Qt.Key_I:
            self.handleAbout()
        elif e.key() == Qt.Key_U:
            self.playURL()
        else:
            e.accept()

    def getLists(self):
        the_folder = self.root + "/tv_listen"
        for entry in os.listdir(the_folder):
            if str(entry).endswith(".m3u8"):
                self.urlList.append(the_folder + "/" + str(entry))
                self.urlList.sort()

    def contextMenuRequested(self, point):
        channels_menu = QMenu()
        for url in self.urlList:
            kanal = url.rpartition(".")[0].rpartition("/")[2].upper()
            m = channels_menu.addMenu(QIcon.fromTheme("tv-symbolic"),kanal)

            variant_m3u8 = m3u8.load(url)
            variant_m3u8.is_variant
    
            for playlist in variant_m3u8.playlists:
                if not playlist.stream_info.resolution == None:
                    res = str(playlist.stream_info.resolution[0])
                    if res in self.resolutions:
                        a = QAction(QIcon.fromTheme('browser'), playlist.uri, self, triggered=self.getLink)
                        m.addMenu(QIcon.fromTheme("computer"), res).addAction(a)

        channels_menu.addSeparator()

        about_action = QAction(QIcon.fromTheme("help-about"), "Info (i)", triggered = self.handleAbout)
        channels_menu.addAction(about_action)

        channels_menu.addSeparator()

        url_action = QAction(QIcon.fromTheme("application-exit"), "play URL from clipboard (u)", triggered = self.playURL)
        channels_menu.addAction(url_action)

        channels_menu.addSeparator()

        quit_action = QAction(QIcon.fromTheme("application-exit"), "Quit (q)", triggered = self.handleQuit)
        channels_menu.addAction(quit_action)

        channels_menu.exec_(self.mapToGlobal(point))

    def playFirst(self):
        url = "http://daserstehdde-lh.akamaihd.net/i/daserstehd_de@629196/index_1216_av-b.m3u8?sd=10&rebase=on"
        self.mediaPlayer.setMedia(QMediaContent(QUrl(url)))
        self.mediaPlayer.play()

    def getLink(self):
        action = self.sender()
        link = action.text()
        self.mediaPlayer.setMedia(QMediaContent(QUrl(link)))
        self.mediaPlayer.play()

    def closeEvent(self, event):
        event.accept()

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def msgbox(self, message):
        QMessageBox.warning(self, "Message", message)

    def wheelEvent(self, event):
        mwidth = self.frameGeometry().width()
        mheight = self.frameGeometry().height()
        mleft = self.frameGeometry().left()
        mtop = self.frameGeometry().top()
        mscale = event.angleDelta().y() / 3
        self.resize(mwidth + mscale, (mwidth + mscale) / 1.778)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() \
                      - QPoint(self.frameGeometry().width() / 2, \
                               self.frameGeometry().height() / 2))
            event.accept()


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
