# TV LiveStream-Player & Recorder

__Requirements:__

- [python3](https://www.python.org/)
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/download5)
- [streamlink](https://github.com/streamlink/streamlink) for recording TV

made and testet in Linux

place your m3u8 files inside the tv_listen folder

m3u8 should look like this:

    #EXTM3U
    #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=184000,RESOLUTION=320x180,CODECS="avc1.66.30, mp4a.40.2"
    http://daserstehdde-lh.akamaihd.net/i/daserstehd_de@629196/index_184_av-p.m3u8?sd=10&rebase=on
    #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=3776000,RESOLUTION=1280x720,CODECS="avc1.64001f, mp4a.40.2"
    http://daserstehdde-lh.akamaihd.net/i/daserstehd_de@629196/index_3776_av-b.m3u8?sd=10&rebase=on


[Ubuntu / Mint Installer](https://www.dropbox.com/s/zyvt4jgngxbli58/TVPlayerInstall.sh?dl=1)

Save the file in the Downloads folder.

then in the terminal

> cd ~/Downloads && chmod +x ./TVPlayerInstall.sh && ./TVPlayerInstall.sh

make mediaterm executable (once)

> chmod +x ~/.local/share/LiveStream-TVPlayer-master/mediaterm

starting with

> cd ~/.local/share/LiveStream-TVPlayer-master && python3 ./TVPlayer2.py

to update channels 

> python3 ~/.local/share/LiveStream-TVPlayer-master/Sender_aktualisieren.py


uninstall with

> cd ~/.local/share/ && rm -rf LiveStream-TVPlayer-master


[Download 64bit App Ubuntu/Mint](https://mega.nz/#!mTgAlYpZ!OyNa_2tsWq8emOcZNFWO8gI0e6nAco7bty4-aSB7toU)
