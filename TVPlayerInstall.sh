#!/bin/sh
cd ~/.local/share/
echo "downloading TVPlayer2 ..."
wget https://github.com/Axel-Erfurt/LiveStream-TVPlayer/archive/master.zip
echo "unzip TVPlayer"
unzip -o master.zip
echo "remove zip file"
rm master.zip
cp ~/.local/share/LiveStream-TVPlayer-master/TVPlayer2.desktop ~/.local/share/applications
echo "starting TVPlayer2 ..."
python3 ~/.local/share/LiveStream-TVPlayer-master/TVPlayer2.py
