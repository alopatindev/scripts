#!/bin/bash
# shows temperature in Velikij Novgorod town

wget -qO - --timeout=5 http://www.novgorod.ru/weather \
    | iconv -f cp1251 \
    | grep -io 'Фактическая</td><td>.* °C</td>' \
    | sed 's/Фактическая<\/td><td>//g;s/<\/td>//g'
