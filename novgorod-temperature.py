#!/usr/bin/python3
# coding=utf8

# novgorod-temperature.py -- shows temperature in Velikij Novgorod town
# Copyright (C) 2010 Alexander Lopatin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

import urllib, urllib.parse, urllib.request

def request_text():
    page = urllib.request.urlopen("http://www.novgorod.ru/temperature/").read()
    lines = page.decode("cp1251").split("\n")
    return lines[lines.index("<LI class=\"first\">Сейчас: <b>") + 1]

def anti_obusfaction(text):
    # replacing "&#[two digits number];" with "[number - 48]"
    out = ""
    i = 0
    while i < len(text):
        if i + 3 < len(text) and text[i:i+2] == "&#":
            number = int(text[i+2:i+4]) - 48
            out += str(number)
            i += 5
        else:
            out += text[i]
            i += 1
    return out

if __name__ == "__main__":
    print(anti_obusfaction(request_text()))
