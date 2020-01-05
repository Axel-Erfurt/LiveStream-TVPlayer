#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from subprocess import Popen, PIPE, call
import sys
import requests

chString = ""
chList = []
urlList = []

app = os.path.expanduser("~") + "/.local/share/LiveStream-TVPlayer-master/mediaterm"
cmd = Popen([app, "-now", "-l"], stdout=PIPE)
cmd_out, cmd_err = cmd.communicate()

t = cmd_out.decode(sys.stdout.encoding).splitlines()

### fehlend Links ersetzen
def repairLinks(url):
    if "master.m3u8" in url:
        base_url = url.rpartition("master.m3u8")[0]
    elif "manifest.m3u8" in url:
        base_url = url.rpartition("manifest.m3u8")[0]

    r = requests.get(url, allow_redirects=True)

    theList = r.text.splitlines()
    for x in range(len(theList)):
        if "m3u8" in  theList[x] and not "http" in theList[x]:
            theList[x] = f"{base_url}{theList[x]}"
        if not "RESOLUTION=1280x720" in theList[x]:
            theList[x] = theList[x].replace("RESOLUTION=960x540", "RESOLUTION=1280x720")
    return theList


for ch in t:
    if not ch == "":
        all = ch.splitlines()[0]
        channel = ch.split('\n')[0].partition(") ")[2].partition("  ")[0].replace('.', " ").upper().replace(" LIVESTREAM", " ").partition("  (")[0]
        url = ch.split('\n')[0].rpartition(")")[2].replace(" ", "")
        if not channel == "":
            chList.append(channel)
        if not url == "":
            urlList.append(url)
        

### alle überprüfen
for x in range(len(urlList)):
    print(chList[x],urlList[x])
    print("verfying", chList[x])
    text = repairLinks(urlList[x])
    
    outfile = os.path.expanduser("~") + "/.local/share/LiveStream-TVPlayer-master/tv_listen/" + chList[x] + ".m3u8"
    with open(outfile, 'w') as f:
        f.write('\n'.join(text))
    