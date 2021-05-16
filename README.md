# TV LiveStream-Player & Recorder

[german Version -> 🇩🇪 ](https://github.com/Axel-Erfurt/LiveStream-TVPlayer-Deutsch)

__Requirements:__

- [python3](https://www.python.org/)
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/download5)
- ffmpeg for recording TV

made and testet in Linux Mint 20

__Shortcuts:__
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
    
    
![screenshot](https://github.com/Axel-Erfurt/LiveStream-TVPlayer/blob/master/screenshot.png)


__Ubuntu / Mint Installation__

open Terminal

> wget 'https://raw.githubusercontent.com/Axel-Erfurt/LiveStream-TVPlayer/master/TVPlayerInstall.sh' -O ~/Downloads/TVPlayerInstall.sh && chmod +x ~/Downloads/TVPlayerInstall.sh && ~/Downloads/TVPlayerInstall.sh 

start app with

> cd ~/.local/share/LiveStream-TVPlayer-master && python3 ./TVPlayer2.py 

or use TVPlayer2 in start menu

uninstall with

> cd ~/.local/share/ && rm -rf LiveStream-TVPlayer-master

