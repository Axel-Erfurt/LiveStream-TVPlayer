# LiveStream-TVPlayer

__Requirements:__

- python2 or python3
- PyQt5
- m3u8

made and testet in Linux

[Download Linux 64bit App](https://mega.nz/#!7D4VyYbD!eojB6jWi2P0YD6tvGeRolhdjf0L2PZDfITaA_zrve2Q)

place your m3u8 files inside the tv_listen folder
(create a tv_listen folder in the folder where TVPlayer2.py is located)

it reads the m3u8 files and creates a contextmenu (named from file) with the resolutions (as submenu) defined in

    self.resolutions = ["320", "480", "640", "960", "1280"]

(you can add more if you want)

m3u8 should look like this:

    #EXTM3U
    #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=184000,RESOLUTION=320x180,CODECS="avc1.66.30, mp4a.40.2"
    http://daserstehdde-lh.akamaihd.net/i/daserstehd_de@629196/index_184_av-p.m3u8?sd=10&rebase=on
    #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=3776000,RESOLUTION=1280x720,CODECS="avc1.64001f, mp4a.40.2"
    http://daserstehdde-lh.akamaihd.net/i/daserstehd_de@629196/index_3776_av-b.m3u8?sd=10&rebase=on
