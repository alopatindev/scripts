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
BUFSIZE = 8 * 1024  # 8 KiB
MAXSPEED = 64 * 1024  # 64 KiB/s == 512 kbit/s
CHARSET = "CP1251"
HOST = "127.0.0.1"
PORT = 8123

# TODO: multithreading

def isunicode(text):
    try:
        text.encode(CHARSET)
        return True
    except UnicodeEncodeError:
        return False

class ServerHandler(SimpleHTTPRequestHandler):
    def print_text(self, text, response=200):
        self.send_response(response)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write((response == 404 and "Not found") or text)
        self.wfile.close()

    def do_GET(self):
        if self.path.find('?') != -1:
             path = self.path.split('?',1)[0]
        else:
             path = self.path
        if path[0] == '/':
            path = path[1:]

        if path[:7] != "http://":
            # FIXME: if HOST == "": get current hostname
            self.print_text("""<h1>Welcome to tagconvd (Tag Converter Daemon)!
<br/></h1>
Add links, like «http://%s:%d/http://link/to/audiostream.mp3»
to your favorite player's playlist to play the music via this deamon."""
                % (HOST, PORT))
            return

        try:
            try:
                f = urllib.urlopen(path)
                response = f.getcode()
            except Exception:
                response = 404
            if response != 200:
                self.print_text("""Something wrong.
Try the <a href="/">main</a> page.""", response)
                return

            self.send_response(200)
            self.send_header("Content-Type", "audio/mpeg")
            self.end_headers()

            buf = f.read(BUFSIZE)
            tmp_filename = tempfile.mktemp(".mp3", "", TMP)
            tmp = open(tmp_filename, "wb")
            tmp.write(buf)
            tmp.close()

            converted = False
            while not converted:
                try:
                    id3 = mutagen.id3.ID3(tmp_filename)
                    tags = id3.pprint()
                    del id3

                    # FIXME: use mutagen to convert tags
                    # TODO: work with ICY-info "StreamTitle=''"
                    if not isunicode(tags):
                        os.system("mid3iconv -q -e%s --remove-v1 '%s'" %
                                  (CHARSET, tmp_filename))
                    converted = True
                except EOFError:
                    buf = f.read(BUFSIZE)
                    tmp = open(tmp_filename, "ab")
                    tmp.write(buf)
                    tmp.close()
                except Exception as text:
                    converted = True
                    print(text)

            tmp = open(tmp_filename, "rb")
            buf = tmp.read()  # reading file contents
            self.wfile.write(buf)
            tmp.close()
            os.remove(tmp_filename)

            while len(buf) > 0:
                start = time.time()
                buf = f.read(BUFSIZE)
                end = time.time()
                try:
                    pause = 1./float(MAXSPEED/BUFSIZE) - (end - start)
                    time.sleep(pause)
                except:
                    pass
                self.wfile.write(buf)
            self.wfile.close()
        except Exception as text:
            print(text)

    def server_bind(self):
        # set SO_REUSEADDR (if available on this platform)
        if hasattr(socket, "SOL_SOCKET") and hasattr(socket, "SO_REUSEADDR"):
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
