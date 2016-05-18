#!/usr/bin/env python
# coding=utf-8

from datetime import timedelta

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY
MONTH = 30 * WEEK
YEAR = 365 * DAY

UNIT_MAP = {
    'y': YEAR,
    'M': MONTH,
    'w': WEEK,
    'd': DAY,
    'h': HOUR,
    'm': MINUTE,
    's': SECOND
}

UNITS = UNIT_MAP.keys()


def parse(value):

    if value[-1] in UNITS:
        value, unit = value[:-1], value[-1]
    else:
        unit = 's'

    return int(value) * UNIT_MAP[unit]


def parse_to_delta(value):
    value = parse(value)
    return timedelta(seconds=value)
