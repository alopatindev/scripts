#!/usr/bin/python3
# coding=utf8
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
import http.server
import urllib, urllib.request
import tempfile

TMP = "/var/tmp"
LOG = "/var/log/tagconvd.log"
BUFSIZE = 8192
CHARSET = "CP1251"
HOST = "127.0.0.1"
PORT = 8123

class ServerHandler(http.server.SimpleHTTPRequestHandler):
    ## FIXME: use log_message from http.server.BaseHTTPRequestHandler.log_message
    ## and make it work!
    #def __init__(self):
    #    self.log_message("starting server on %s:%d", HOST, PORT)

    #def log_date_time_string(self):
    #    now = time.time()
    #    year, month, day, hh, mm, ss, x, y, z = time.localtime(now)
    #    s = "%02d/%3s/%04d %02d:%02d:%02d" % (
    #            day, self.monthname[month], year, hh, mm, ss)
    #    return s

    #def address_string(self):
    #    host, port = self.client_address[:2]
    #    return socket.getfqdn(host)

    #def log_message(self, format, *args):
    #    sys.stderr.write("%s - - [%s] %s\n" %
    #                     (self.address_string(),
    #                      self.log_date_time_string(),
    #                      format % args))

    def do_GET(self):
        if self.path.find('?') != -1:
             path = self.path.split('?',1)[0]
        else:
             path = self.path
        if path[0] == '/':
            path = path[1:]
        print(path)

        try:
            self.send_response(200)
            self.send_header("Content-Type", "audio/mpeg")
            self.end_headers()

            f = urllib.request.urlopen(path)

            buf = f.read(BUFSIZE)
            tmp_filename = tempfile.mktemp(".mp3", "", TMP)
            tmp = open(tmp_filename, "wb")
            tmp.write(buf)
            tmp.close()
            os.system("mid3iconv -e%s --remove-v1 '%s' >> /dev/null" %
                (CHARSET, tmp_filename))
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
        print("binding")
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
            server = http.server.HTTPServer((HOST, PORT), ServerHandler)
            server.serve_forever()
        except Exception as text:
            server.close()
            print(text)

if __name__ == "__main__":
    daemonize()
