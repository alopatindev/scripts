#!/usr/bin/python3
# coding=utf8
#
# Vkontakte audio links fetcher.
# Copyright (C) 2010 Alexander Lopatin
#
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

def usage(): print("usage: %s 'artist - song' [page number] [to page number]" % sys.argv[0])

def page(q, number, opener, titles):
    #operate(209145,1044,362847,'db5a6cba31',194);
    #http://cs1044.vkontakte.ru/u362847/audio/db5a6cba31.mp3
    s = opener.open("http://vk.com/gsearch.php?section=audio&q=%s\
&name=1&offset=%d" % (q, (number)*100)).readlines()
    j = 0
    for i in s:
        j += 1
        i = i.decode("cp1251")
        if i.find("return operate") != -1:
            g = re.search(r"return operate\(\d*?,(\d*?),(\d*?),'([\da-f]*?)'",
                          i).groups()
            title = re.search(
r"<span id=\"title\d*?\">(<a href='.*?'>|)(.*?)(</a>|)</span>",
s[j+2].decode("cp1251")).group(2).lower()
            if title not in titles:
                titles.append(title)
                print("http://cs%s.vkontakte.ru/u%s/audio/%s.mp3" % g)
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
        q = urllib.parse.quote(sys.argv[1])
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
