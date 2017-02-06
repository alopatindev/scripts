#!/usr/bin/node

'use strict'

const fs = require('fs')

const LOG_FILE = '/var/log/emerge.log'
const MAX_LINES = 10

const lines = fs
    .readFileSync(LOG_FILE)
    .toString()
    .split('\n')

function logToMap(pattern) {
    return new Map(
        lines
        .filter(x => x.includes(pattern))
        .map(x => {
            const packAndTime = x
                .replace(/: {2}.* \([0-9]* of [0-9]*\) /, ' ')
                .replace(/ to \/$/, '')
                .split(' ')
                .reverse()
            return [packAndTime[0], parseInt(packAndTime[1])]
        })
    )
}

function compareIntegers(x, y) {
    if (x < y) {
        return -1
    } else if (x > y) {
        return 1
    } else {
        return 0
    }
}

const packsStarted = logToMap('>>> emerge')
const packsFinished = logToMap('::: completed emerge')

function packIsValid(pack) {
    return packsFinished.has(pack) && packsStarted.get(pack) <= packsFinished.get(pack)
}

function secondsToHuman(seconds) {
    const minute = 60
    const minutesPerHour = 60
    const hour = minutesPerHour * minute

    if (seconds >= hour) {
        return `${(seconds / hour).toFixed(1)} hours`
    } else if (seconds >= minute) {
        return `${(seconds / minute).toFixed(1)} minutes`
    } else {
        return `${seconds} seconds`
    }
}

const result = Array
    .from(packsStarted.keys())
    .filter(packIsValid)
    .map(pack => {
        const dt = packsFinished.get(pack) - packsStarted.get(pack)
        return [pack, dt]
    })
    .sort((x, y) => compareIntegers(x[1], y[1]))
    .reverse()
    .slice(0, MAX_LINES)

result.forEach(x => console.log(`${x[0]} took ${secondsToHuman(x[1])}`))
