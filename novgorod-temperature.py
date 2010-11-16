#!/usr/bin/python3
# coding=utf8

# novgorod-temperature.py -- shows temperature in Velikij Novgorod town
# Copyright (C) 2010 Alexander Lopatin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

# FIXME: rewrite this code without those dirty hacks

import urllib, urllib.parse, urllib.request
import re

def get_page():
    page = urllib.request.urlopen("http://www.novgorod.ru/temperature/").read()
    page = page.decode("cp1251").split("\n")
    return page[page.index("<LI class=\"first\">Сейчас: <b>") + 1]

def anti_obusfaction(text):
    shit = list(re.search(r"&#([0-9]{2}?);", text).groups())
    for i in range(len(shit)):
        shit[i] = int(shit[i]) - 48

    out = ""
    i = 0
    while i < len(text):
        if i + 3 < len(text) and text[i] == "&" and text[i+1] == "#":
            for j in str(shit.pop(0)):
                out += j
            i += 5
        else:
            out += text[i]
            i += 1
    return out

if __name__ == "__main__":
    print(anti_obusfaction(get_page()))
