#!/bin/bash
# shows movies' length in human-readable format using mplayer

LEN=$(mplayer -vo null -ao null -frames 0 -identify "$@" \
    | grep ID_LENGTH \
    | sed 's/ID_LENGTH=//')
MIN=$(echo "${LEN} / 60.0" | bc -l)
INT_HR=$(echo "${MIN} / 60" | bc)
MINMOD=$(echo "${MIN} - (${INT_HR} * 60)" | bc -s)
printf "%d hours, %2.f minutes\n" "${INT_HR}" "${MINMOD}"
