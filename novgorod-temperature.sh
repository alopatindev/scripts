#!/bin/bash
# shows temperature in Velikij Novgorod town

curl -s http://www.novgorod.ru/temperature/ \
    | iconv -f cp1251 | grep -io "сейчас:\ .*C" | cut -d' ' -f2
