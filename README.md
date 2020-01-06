# TV LiveStream-Player & Recorder

__Requirements:__

- [python3](https://www.python.org/)
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/download5)
- [streamlink](https://github.com/streamlink/streamlink) for recording TV

made and testet in Linux

place your m3u8 files inside the tv_listen folder

### Shortcuts:
- q = Exit
- f = toggle Fullscreen
- u = play url from clipboard
- mouse wheel = resize window
- mouse click left + move = move window
- arrow up = more volume
- arrow down = less volume
- h = toggle mouse cursor visible
- r = record with timer
- w = record without timer
- s = stop recording

m3u8 should look like this:

    #EXTM3U
    #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=184000,RESOLUTION=320x180,CODECS="avc1.66.30, mp4a.40.2"
    http://daserstehdde-lh.akamaihd.net/i/daserstehd_de@629196/index_184_av-p.m3u8?sd=10&rebase=on
    #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=3776000,RESOLUTION=1280x720,CODECS="avc1.64001f, mp4a.40.2"
    http://daserstehdde-lh.akamaihd.net/i/daserstehd_de@629196/index_3776_av-b.m3u8?sd=10&rebase=on
    
    
![screenshot](https://github.com/Axel-Erfurt/LiveStream-TVPlayer/blob/master/screenshot.png)


### Ubuntu / Mint Installation

open Terminal

> wget 'https://raw.githubusercontent.com/Axel-Erfurt/LiveStream-TVPlayer/master/TVPlayerInstall.sh' -O ~/Downloads/TVPlayerInstall.sh && chmod +x ~/Downloads/TVPlayerInstall.sh && ~/Downloads/TVPlayerInstall.sh 

start app with

> cd ~/.local/share/LiveStream-TVPlayer-master && python3 ./TVPlayer2.py 

or use TVPlayer2 in start menu

uninstall with

> cd ~/.local/share/ && rm -rf LiveStream-TVPlayer-master


App made with pyinstaller - maybe it works or not

[Download 64bit App Ubuntu/Mint](https://mega.nz/#!mTgAlYpZ!OyNa_2tsWq8emOcZNFWO8gI0e6nAco7bty4-aSB7toU)
