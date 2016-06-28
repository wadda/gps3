# coding=utf-8
"""Miscellaneous functions"""
import argparse
from math import modf
from datetime import datetime

__author__ = 'Moe'
__copyright__ = 'Copyright 2016  Moe'
__license__ = 'MIT'
__version__ = '0.1.1'

CONVERSION = {'raw': (1, 1, 'm/s', 'meters'),
              'metric': (3.6, 1, 'kph', 'meters'),
              'nautical': (1.9438445, 1, 'kts', 'meters'),
              'imperial': (2.2369363, 3.2808399, 'mph', 'feet')}


def add_args():
    """Adds commandline arguments and formatted Help"""
    parser = argparse.ArgumentParser()

    parser.add_argument('-host', action='store', dest='host', default='127.0.0.1', help='DEFAULT "127.0.0.1"')
    parser.add_argument('-port', action='store', dest='port', default='2947', help='DEFAULT 2947', type=int)
    parser.add_argument('-json', dest='gpsd_protocol', const='json', action='store_const', default='json', help='DEFAULT JSON objects */')
    parser.add_argument('-device', dest='devicepath', action='store', help='alternate devicepath e.g.,"-device /dev/ttyUSB4"')
    # Infrequently used options
    parser.add_argument('-nmea', dest='gpsd_protocol', const='nmea', action='store_const', help='*/ output in NMEA */')
    # parser.add_argument('-rare', dest='gpsd_protocol', const='rare', action='store_const', help='*/ output of packets in hex */')
    # parser.add_argument('-raw', dest='gpsd_protocol', const='raw', action='store_const', help='*/ output of raw packets */')
    # parser.add_argument('-scaled', dest='gpsd_protocol', const='scaled', action='store_const', help='*/ scale output to floats */')
    # parser.add_argument('-timing', dest='gpsd_protocol', const='timing', action='store_const', help='*/ timing information */')
    # parser.add_argument('-split24', dest='gpsd_protocol', const='split24', action='store_const', help='*/ split AIS Type 24s */')
    # parser.add_argument('-pps', dest='gpsd_protocol', const='pps', action='store_const', help='*/ enable PPS JSON */')
    parser.add_argument('-v', '--version', action='version', version='Version: {}'.format(__version__))
    parser.add_argument('-seconds_nap', action='store', dest='seconds_nap', default=20, help='Demo DEFAULT "20 Sec Nap"')
    parser.add_argument('-usnap', action='store', dest='usnap', default=0.2, help='sleep in seconds after empty socket read')
    cli_args = parser.parse_args()
    return cli_args


def satellites_used(feed):
    """Counts number of satellites used in calculation from total visible satellites
    Arguments:
        feed feed=data_stream.satellites
    Returns:
        total_satellites(int):
        used_satellites (int):
    """
    total_satellites = 0
    used_satellites = 0

    if not isinstance(feed, list):
        return 0, 0

    for satellites in feed:
        total_satellites += 1
        if satellites['used'] is True:
            used_satellites += 1
    return total_satellites, used_satellites


def make_time(gps_datetime_str):
    """Makes datetime object from string object"""
    if not 'n/a' == gps_datetime_str:
        datetime_string = gps_datetime_str
        datetime_object = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S")
        return datetime_object


def elapsed_time_from(start_time):
    """calculate time delta from latched time and current time"""
    time_then = make_time(start_time)
    time_now = datetime.utcnow().replace(microsecond=0)
    if time_then is None:
        return
    delta_t = time_now - time_then
    return delta_t


def unit_conversion(thing, units, length=False):
    """converts base data between metric, imperial, or nautical units"""
    if 'n/a' == thing:
        return 'n/a'
    try:
        thing = round(thing * CONVERSION[units][0 + length], 2)
    except TypeError:
        thing = 'fubar'
    return thing, CONVERSION[units][2 + length]


def sexagesimal(sexathang, tag, form='DDD'):
    """
    Arguments:
        sexathang: (float), -15.560615 (negative = South), -146.241122 (negative = West)  # Apataki Carenage
        tag: (str) 'lat' | 'lon'
        form: (str), 'DDD'|'DMM'|'DMS', decimal Degrees, decimal Minutes, decimal Seconds
    Returns:
        latitude: e.g., '15°33'38.214"S'
        longitude: e.g., '146°14'28.039"W'
    """
    cardinal = 'O'
    if not isinstance(sexathang, float):
        sexathang = 'n/a'
        return sexathang

    if tag == 'lon':
        if sexathang > 0.0:
            cardinal = 'E'
        if sexathang < 0.0:
            cardinal = 'W'

    if tag == 'lat':
        if sexathang > 0.0:
            cardinal = 'N'
        if sexathang < 0.0:
            cardinal = 'S'

    if form == 'RAW':
        sexathang = '{0:4.9f}°'.format(sexathang)  # 4 to allow -100° through -179.999999° to -180°
        return sexathang

    if form == 'DDD':
        sexathang = '{0:3.6f}°'.format(abs(sexathang))

    if form == 'DMM':
        _latlon = abs(sexathang)
        minute_latlon, degree_latlon = modf(_latlon)
        minute_latlon *= 60
        sexathang = '{0}°{1:2.5f}\''.format(int(degree_latlon), minute_latlon)

    if form == 'DMS':
        _latlon = abs(sexathang)
        minute_latlon, degree_latlon = modf(_latlon)
        second_latlon, minute_latlon = modf(minute_latlon * 60)
        second_latlon *= 60.0
        sexathang = '{0}°{1}\'{2:2.3f}\"'.format(int(degree_latlon), int(minute_latlon), second_latlon)

    return sexathang + cardinal


def hertz(hz):
    """Change or enumerate a Faster/Slower gps refresh rate if device is able"""
    from subprocess import call
    inverse = str(1 / hz)
    call((['gpsctl', '-c', inverse]))
