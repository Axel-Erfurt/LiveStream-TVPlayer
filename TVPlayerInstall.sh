#!/bin/sh
filename=$HOME/.local/share/LiveStream-TVPlayer-master/tv_listen
if [ -d "$filename" ]
then
    echo "$filename found, copying to /tmp"
    cp -rf $filename /tmp
else
    echo "$filename not found"
fi
sharedapps=$HOME/.local/share/applications/
if [ -d "$sharedapps" ]
 then
    echo "$sharedapps found"
else
    echo "$sharedapps not found"
    mkdir $sharedapps
fi
echo "removing TVPlayer2"
rm -rf ~/.local/share/LiveStream-TVPlayer-master
cd ~/.local/share/
echo "downloading TVPlayer2 ..."
wget https://github.com/Axel-Erfurt/LiveStream-TVPlayer/archive/master.zip
echo "unzip TVPlayer2"
unzip -o master.zip
sleep 1
echo "remove zip file"
rm master.zip
#mv ~/.local/share/LiveStream-TVPlayer-master ~/.local/share/LiveStream-TVPlayer-master
rf=/tmp/tv_listen
if [ -d "$rf" ]
then
    echo "restore tv_listen"
    cp $rf -rf $HOME/.local/share/LiveStream-TVPlayer-master
else
    echo "$rf not found"
fi
desktopfile=$HOME/.local/share/applications/TVPlayer2.desktop
if [ -e "$desktopfile" ]
then
    echo "$desktopfile already exists"
else
    echo "$desktopfile not found"
    cp $HOME/.local/share/LiveStream-TVPlayer-master/TVPlayer2.desktop $HOME/.local/share/applications
fi
rm ~/Downloads/TVPlayerInstall.sh
echo "check Channels ... "
python3 ~/.local/share/LiveStream-TVPlayer-master/query_mv.py ~/.local/share/LiveStream-TVPlayer-master/
echo "starting TVPlayer2 ... "
python3 ~/.local/share/LiveStream-TVPlayer-master/TVPlayer2.py
