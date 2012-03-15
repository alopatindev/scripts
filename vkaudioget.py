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

LOGIN=""
PASSWORD=""

url_value_regexp = re.compile(r"value=\"(.*?),.*?\"")
title_regexp = re.compile(r"return false\">(.*?)</a></b> - <span class=\"title\">(<a href=\"\".*;return false;\">|)(.*?)(</a>|)</span>")
title2_regexp = re.compile(r"<span id=\"title\d*?\">(<a href='.*?'>|)(.*?)(</a>|)</span>")
operate_regexp = re.compile(r"return operate\(\d*?,(\d*?),(\d*?),'([\da-f]*?)'")
operate2_regexp = re.compile(r"return operate\(.*?,'(.*?)',")

def usage():
    print("usage: %s 'artist - song' | \
'http://vk.com/audio.php?gid=119501' [page number] [to page number]" %
    sys.argv[0])

def page(q, number, opener, titles):
    if q[:7] == "http://":
        url = q.replace("vkontakte.ru/", "vk.com/")
        s = opener.open(url).read().decode("cp1251")
        for i in s.split('\n'):
            if i.find("<input type=\"hidden\" id=\"audio_info") != -1:
                try:
                    last_url = url_value_regexp.search(i).group(1)
                    if last_url[:7] != "http://":
                        break
                except: pass
            if i.find("<div class=\"title_wrap\">") != -1:
                try:
                    title = title_regexp.search(i).group(2).lower()
                    if title == "" or title not in titles:
                        titles.append(title)
                        print(last_url)
                except: pass
    else:
        #operate(209145,1044,362847,'db5a6cba31',194);
        #http://cs1044.vkontakte.ru/u362847/audio/db5a6cba31.mp3
        url = "http://vk.com/gsearch.php?section=audio&q=%s&name=1&offset=%d" % \
            (urllib.parse.quote(q), number * 100)
        s = opener.open(url).readlines()
        #for i in s: print (i.decode("cp1251"))
        j = 0
        for i in s:
            j += 1
            i = i.decode("cp1251")
            if i.find("return operate") != -1:
                try:
                    g = operate_regexp.search(i).groups()
                    outurl = "http://cs%s.vkontakte.ru/u%s/audio/%s.mp3" % g
                    title = title2_regexp.search(s[j+2].decode("cp1251")).\
                            group(2).lower()
                except AttributeError:
                    g = operate2_regexp.search(i)
                    #TODO: fetch title normally
                    title = ""
                    outurl = g.groups()[0]
                if title == "" or title not in titles:
                    titles.append(title)
                    print(outurl)
                    #show title
                    #g = list(g); g.append(title.replace("'", '"'))
                    #print("wget 'http://cs%s.vkontakte.ru/u%s/audio/%s.mp3' -O '%s.mp3'" % tuple(g))

def login(opener, cookies):
    cookie = os.environ["HOME"] + "/.vkcookies"
    if os.path.exists(cookie):
        cookies.load(cookie)

    data = { "email" : LOGIN, "pass" : PASSWORD }
    text = ""
    try:
        text = opener.open("http://vk.com/groups.php").read().decode("cp1251")
    except urllib.error.HTTPError as t:
        if t.geturl().find("login.php") != -1:
            url = "http://vk.com/" + t.geturl()
            try:
                text = opener.open(url).read().decode("cp1251")
            except urllib.error.HTTPError as t:
                pass
            cookies.save(cookie)

    if text.find("<title>Вход</title>") != -1:
        try:
            opener.open("http://vk.com/login.php", urllib.parse.urlencode(data))
        except urllib.error.HTTPError as t:
            url = "http://vk.com/" + t.geturl()
            opener.open(url)
        cookies.save(cookie)

    #return opener.open("http://vk.com/groups.php").read().decode("cp1251").\
    #    find("<title>Вход</title>") == -1
    return True


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
    #urllib.request.FancyURLopener(),
    #opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.121 Safari/535.2')]

    if not login(opener, cookies):
        print("Login failed :(")
        return 1

    titles = []

    for i in range(p1-1, p2-1):
        page(q, i, opener, titles)

    return 0

if __name__ == "__main__":
    sys.exit(main())
