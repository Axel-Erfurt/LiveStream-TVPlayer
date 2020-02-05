#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
import os
import sys

channels = ["ard", "zdf", "mdr", "phoenix", "rbb", "br", "hr", "sr", "swr", "ndr", "dw", "wdr", "arte", "3sat", "kika", "orf"]
chList = []
urlList = []
root = sys.argv[1]
    
def getURL(name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0',
        'Accept': '*/*',
        'Accept-Language': 'de-DE,en;q=0.5',
        'Content-Type': 'text/plain;charset=UTF-8',
        'Connection': 'keep-alive',
    }


    data = {"queries":[{"fields":["title","topic"],"query":"livestream"},{"fields":["channel"],"query":"" + name + ""}]}
    response = requests.post('https://mediathekviewweb.de/api/query', headers=headers, json=data)
    response_json = response.json()
    count = int(response_json['result']['queryInfo']['resultCount'])
    for x in range(count):
        title = response_json['result']['results'][x]['title']
        url = response_json['result']['results'][x]['url_video']
        if ".m3u8" in url and "3Sat" in title:
            chList.append(title.replace(".", " ").replace(' Livestream', ''))
            urlList.append(url)
        if ".m3u8" in url and "KiKA" in title:
            title = "kika"
            chList.append(title)
            urlList.append(url)
        if ".m3u8" in url and name.upper() in title:
            chList.append(title.replace(".", " ").replace(' Livestream', ''))
            urlList.append(url)
    
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
        
for x in range(len(channels)):
    r = getURL(channels[x])
    
### alle überprüfen
for x in range(len(urlList)):
    #print(chList[x],urlList[x])
    print("überprüfe", chList[x])
    text = repairLinks(urlList[x])
    name = chList[x] + ".m3u8"
    outfile = os.path.join(root, "tv_listen/", name)
    with open(outfile, 'w') as f:
        f.write('\n'.join(text))
