#!/bin/sh
cd ~/.local/share/
echo "estelle Ordner TVPlayer"
echo "TVPlayer herunterladen ..."
wget https://github.com/Axel-Erfurt/LiveStream-TVPlayer/archive/master.zip
echo "TVPlayer entpacken"
unzip -o master.zip
echo "zip Datei wird entfernt"
rm master.zip
chmod +x ~/.local/share/LiveStream-TVPlayer-master/mediaterm
python3 ~/.local/share/LiveStream-TVPlayer-master/Sender_aktualisieren.py ~/.local/share/LiveStream-TVPlayer-master
echo "TVPlayer wird gestartet ..."
python3 ~/.local/share/LiveStream-TVPlayer-master/TVPlayer2.py
