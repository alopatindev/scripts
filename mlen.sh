#!/bin/bash
# Shows movies' duration in human-readable format

ffprobe "$@" 2>>/dev/stdout | grep Duration: | cut -d: -f2,3,4 | cut -d, -f1
