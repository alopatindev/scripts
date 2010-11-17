#!/usr/bin/python2
# -*- coding: utf-8 -*-
#
# tagconvd is an mp3 proxy for audiostreams with wrong tags' charset.
# Copyright (C) 2010 Alexander Lopatin
#
# Usage: play "http://127.0.0.1:8123/http://link/to/audio/stream.mp3"
# via your favorite player
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

import time
import os
import sys
import socket
from SimpleHTTPServer import SimpleHTTPRequestHandler
import BaseHTTPServer
import urllib
import mutagen, mutagen.id3
import tempfile

TMP = "/var/tmp"
LOG = "/var/log/tagconvd.log"
BUFSIZE = 8192
CHARSET = "CP1251"
HOST = "127.0.0.1"
PORT = 8123

def isunicode(text):
    # FIXME: rewrite this stupid hack to support other languages
    alphabet1 = range(ord(u'а'), ord(u'я'))
    alphabet2 = range(ord(u'А'), ord(u'Я'))
    uni = False
    for i in text:
        letter = ord(i)
        if letter in alphabet1 or letter in alphabet2:
            uni = True
    return uni


class ServerHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.find('?') != -1:
             path = self.path.split('?',1)[0]
        else:
             path = self.path
        if path[0] == '/':
            path = path[1:]
        # TODO: process 404 and other errors

        try:
            self.send_response(200)
            self.send_header("Content-Type", "audio/mpeg")
            self.end_headers()

            f = urllib.urlopen(path)
            buf = f.read(BUFSIZE)
            tmp_filename = tempfile.mktemp(".mp3", "", TMP)
            tmp = open(tmp_filename, "wb")
            tmp.write(buf)
            tmp.close()

            try:
                id3 = mutagen.id3.ID3(tmp_filename)
                tags = id3.pprint()
                del id3

                # FIXME: use mutagen to convert tags
                # TODO: work with ICY-info "StreamTitle=''"
                if not isunicode(tags):
                    os.system("mid3iconv -q -e%s --remove-v1 '%s'" %
                              (CHARSET, tmp_filename))
            except Exception as text:
                print(text)

            tmp = open(tmp_filename, "rb")
            buf = tmp.read(BUFSIZE)
            self.wfile.write(buf)
            tmp.close()
            os.remove(tmp_filename)

            while len(buf) > 0:
                buf = f.read(BUFSIZE)
                self.wfile.write(buf)
            self.wfile.close()
        except Exception as text:
            print(text)

    def server_bind(self):
        # set SO_REUSEADDR (if available on this platform)
        if hasattr(socket, 'SOL_SOCKET') and hasattr(socket, 'SO_REUSEADDR'):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        BaseHTTPServer.HTTPServer.server_bind(self)

def daemonize():
    #os.chdir("/")
    #os.umask(0)
    #os.setsid()

    pid = os.fork()
    if pid > 0:
        sys.exit(0) # exit second parent

    #sys.stdin.close()
    #sys.stdout.close()
    #sys.stderr.close()
    log = open(LOG, "a+")
    ##os.dup2(log.fileno(), sys.stdin.fileno())
    os.dup2(log.fileno(), sys.stdout.fileno())
    os.dup2(log.fileno(), sys.stderr.fileno())

    while True:
        try:
            server = BaseHTTPServer.HTTPServer((HOST, PORT), ServerHandler)
            server.serve_forever()
        except Exception as text:
            server.close()
            print(text)

if __name__ == "__main__":
    daemonize()
