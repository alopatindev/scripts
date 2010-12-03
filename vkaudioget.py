#!/usr/bin/python3
# coding=utf8
#
# Vkontakte audio links fetcher.
# Usage: ./vkaudioget.py Metallica | mpc add
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

import http.cookiejar
import urllib
import urllib.request
import sys
import re
import os

def usage():
    print("usage: %s 'artist - song' | \
'http://vk.com/audio.php?gid=119501' [page number] [to page number]" %
    sys.argv[0])

def page(q, number, opener, titles):
    #operate(209145,1044,362847,'db5a6cba31',194);
    #http://cs1044.vkontakte.ru/u362847/audio/db5a6cba31.mp3
    url = ((q[:7] == "http://" and q.replace("vkontakte.ru/", "vk.com/")) or
    "http://vk.com/gsearch.php?section=audio&q=%s&name=1" %
        urllib.parse.quote(q))
    url += "&offset=%d" % (number * 100)
    s = opener.open(url).readlines()
    j = 0
    for i in s:
        j += 1
        i = i.decode("cp1251")
        if i.find("return operate") != -1:
            try:
                g = re.search(r"return operate\(\d*?,(\d*?),(\d*?),'([\da-f]*?)'",
                          i).groups()
                outurl = "http://cs%s.vkontakte.ru/u%s/audio/%s.mp3" % g
                title = re.search(
r"<span id=\"title\d*?\">(<a href='.*?'>|)(.*?)(</a>|)</span>",
s[j+2].decode("cp1251")).group(2).lower()
            except AttributeError:
                g = re.search(r"return operate\(.*?,'(.*?)',", i)
                #TODO: fetch title normally title
                title = ""
                outurl = g.groups()[0]
            if title == "" or title not in titles:
            #if title not in titles:
                titles.append(title)
                print(outurl)
                #show title
                #g = list(g); g.append(title.replace("'", '"'))
                #print("wget 'http://cs%s.vkontakte.ru/u%s/audio/%s.mp3' -O '%s.mp3'" % tuple(g))

def login(opener, cookies):
    cookie = os.environ["HOME"] + "/.vkcookies"
    if os.path.exists(cookie):
        cookies.load(cookie)
    else:
        data = { "email" : "b2629268@lhsdv.com", "pass" : "mastermind123q" }
        opener.open("http://vk.com/login.php", urllib.parse.urlencode(data))
        cookies.save(cookie)

def main():
    try:
        q = sys.argv[1]
        p1 = ((len(sys.argv) > 2) and int(sys.argv[2])) or 1
        p2 = ((len(sys.argv) > 3) and int(sys.argv[3]) + 1) or p1 + 1
    except IndexError:
        usage()
        return 1

    cookies = http.cookiejar.MozillaCookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookies),
    )

    login(opener, cookies)

    titles = []

    for i in range(p1-1, p2-1):
        page(q, i, opener, titles)

    return 0

sys.exit(main())
