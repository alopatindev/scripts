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

page = urllib.request.urlopen("http://www.novgorod.ru/temperature/").read()
page = page.decode("cp1251").split("\n")
j = 0
text = ""
for i in page:
    if i == "<LI class=\"first\">Сейчас: <b>":
        text = urllib.parse.unquote(page[j+1])
        break
    j += 1

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

print(out)
