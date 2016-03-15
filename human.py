#!/usr/bin/env python3
# coding=utf-8

import argparse
import curses
import sys
from datetime import datetime
from time import sleep

import gps3

if sys.version_info[0] < 3:
    pass
else:
    pass

__author__ = 'Moe'
__copyright__ = "Copyright 2015-2016  Moe"
__license__ = "MIT"
__version__ = "0.11a"


def add_args():
    """Adds commandline arguments and formatted Help"""
    parser = argparse.ArgumentParser()

    parser.add_argument('-host', action='store', dest='host', default='127.0.0.1', help='DEFAULT "127.0.0.1"')
    parser.add_argument('-port', action='store', dest='port', default='2947', help='DEFAULT 2947', type=int)
    parser.add_argument('-json', dest='gpsd_protocol', const='json', action='store_const', default='json', help='DEFAULT JSON objects */')
    parser.add_argument('-device', dest='devicepath', action='store', help='alternate devicepath e.g.,"-device /dev/ttyUSB4"')
    # Infrequently used options
    parser.add_argument('-nmea', dest='gpsd_protocol', const='nmea', action='store_const', help='*/ output in NMEA */')
    parser.add_argument('-rare', dest='gpsd_protocol', const='rare', action='store_const', help='*/ output of packets in hex */')
    parser.add_argument('-raw', dest='gpsd_protocol', const='raw', action='store_const', help='*/ output of raw packets */')
    parser.add_argument('-scaled', dest='gpsd_protocol', const='scaled', action='store_const', help='*/ scale output to floats */')
    parser.add_argument('-timing', dest='gpsd_protocol', const='timing', action='store_const', help='*/ timing information */')
    parser.add_argument('-split24', dest='gpsd_protocol', const='split24', action='store_const', help='*/ split AIS Type 24s */')
    parser.add_argument('-pps', dest='gpsd_protocol', const='pps', action='store_const', help='*/ enable PPS JSON */')

    args = parser.parse_args()
    return args


def satellites_used(feed):
    """Counts number of satellites use in calculation from total visible satellites
    Arguments:
        feed feed=gps_fix.TPV['satellites']
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


def make_time(gps__datetime_str):
    if not 'n/a' == gps__datetime_str:
        datetime_string = gps__datetime_str
        datetime_object = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S")
        return datetime_object


def do_lapsed(start_time):
    time_then = make_time(start_time)
    time_now = datetime.utcnow().replace(microsecond=0)
    if time_then is None:
        return
    delta_t = time_now - time_then
    return delta_t


def show_human():
    """Curses terminal with standard outputs """
    args = add_args()
    gps_connection = gps3.GPSDSocket(args.host, args.port, args.gpsd_protocol, args.devicepath)
    gps_fix = gps3.Fix()

    screen = curses.initscr()
    # curses.KEY_RESIZE
    curses.cbreak()
    screen.clear()
    screen.scrollok(True)

    data_window = curses.newwin(19, 39, 1, 1)
    sat_window = curses.newwin(19, 39, 1, 40)
    device_window = curses.newwin(6, 39, 14, 40)
    packet_window = curses.newwin(20, 78, 20, 1)

    try:
        for new_data in gps_connection:
            if new_data:
                gps_fix.refresh(new_data)

                data_window.border(0)
                data_window.addstr(0, 2, 'GPS3 Python {}.{}.{} GPSD Interface'.format(*sys.version_info), curses.A_BOLD)
                data_window.addstr(1, 2, 'Time:  {time} '.format(**gps_fix.TPV))
                data_window.addstr(2, 2, 'Latitude:  {lat}° '.format(**gps_fix.TPV))
                data_window.addstr(3, 2, 'Longitude: {lon}° '.format(**gps_fix.TPV))
                data_window.addstr(4, 2, 'Altitude:  {alt} meters'.format(**gps_fix.TPV))
                data_window.addstr(5, 2, 'Speed:     {speed} m/s'.format(**gps_fix.TPV))
                data_window.addstr(6, 2, 'Heading:   {track}° True'.format(**gps_fix.TPV))
                data_window.addstr(7, 2, 'Climb:     {climb} m/s'.format(**gps_fix.TPV))
                data_window.addstr(8, 2, 'Status:     {mode:<}D  '.format(**gps_fix.TPV))
                data_window.addstr(9, 2, 'Latitude Err:  +/-{epx} meters '.format(**gps_fix.TPV))
                data_window.addstr(10, 2, 'Longitude Err: +/-{epy} meters  '.format(**gps_fix.TPV))
                data_window.addstr(11, 2, 'Altitude Err:  +/-{epv} meters '.format(**gps_fix.TPV))
                data_window.addstr(12, 2, 'Course Err:    +/-{epc}  '.format(**gps_fix.TPV), curses.A_DIM)
                data_window.addstr(13, 2, 'Speed Err:     +/-{eps} m/s '.format(**gps_fix.TPV), curses.A_DIM)
                data_window.addstr(14, 2, 'Time Offset:   +/-{ept}  '.format(**gps_fix.TPV), curses.A_DIM)
                data_window.addstr(15, 2, 'gdop:{gdop}  pdop:{pdop}  tdop:{tdop}'.format(**gps_fix.SKY))
                data_window.addstr(16, 2, 'ydop:{ydop}  xdop:{xdop} '.format(**gps_fix.SKY))
                data_window.addstr(17, 2, 'vdop:{vdop}  hdop:{hdop} '.format(**gps_fix.SKY))

                sat_window.clear()
                sat_window.border()
                sat_window.addstr(0, 2, 'Using {0[1]}/{0[0]} satellites (truncated)'.format(satellites_used(gps_fix.SKY['satellites'])))
                sat_window.addstr(1, 2, 'PRN     Elev   Azimuth   SNR   Used')
                line = 2
                if isinstance(gps_fix.SKY['satellites'], list):  # Nested lists of dictionaries are strings before data is present
                    for sats in gps_fix.SKY['satellites'][0:10]:
                        sat_window.addstr(line, 2, '{PRN:>2}   {el:>6}   {az:>5}   {ss:>5}   {used:}'.format(**sats))
                        line += 1

                # device_window.clear()
                device_window.border(0)
                if not isinstance(gps_fix.DEVICES['devices'], list):  # Local machines need a 'device' kick start to have valid data
                    gps_connection.send('?DEVICES;')

                if isinstance(gps_fix.DEVICES['devices'], list):  # Nested lists of dictionaries are strings before data is present (REALLY?)

                    for gizmo in gps_fix.DEVICES['devices']:
                        start_time, _uicroseconds = gizmo['activated'].split('.')  # Remove '.000Z'
                        elapsed = do_lapsed(start_time)

                        device_window.addstr(1, 2, 'Activated:{}'.format(gizmo['activated']))
                        device_window.addstr(2, 2, 'Host:{0.host}:{0.port} {1}'.format(args, gizmo['path']))
                        device_window.addstr(3, 2, 'Driver:{driver} BPS:{bps}'.format(**gizmo))
                        device_window.addstr(4, 2, 'Cycle:{0} Hz {1:>15} Elapsed'.format(gizmo['cycle'], elapsed))

                # packet_window.clear()
                # packet_window.border(0)
                packet_window.scrollok(True)
                packet_window.addstr(0, 0, '{}'.format(new_data))

                data_window.refresh()
                sat_window.refresh()
                device_window.refresh()
                packet_window.refresh()

                sleep(.4)

    except KeyboardInterrupt:
        shut_down(gps_connection)


def show_nmea():
    """NMEA"""
    args = add_args()
    gps_connection = gps3.GPSDSocket(args.host, args.port, args.gpsd_protocol, args.devicepath)

    screen = curses.initscr()
    # curses.KEY_RESIZE
    curses.cbreak()
    screen.clear()
    screen.scrollok(True)

    data_window = curses.newwin(23, 79, 1, 1)

    try:
        for new_data in gps_connection:
            if new_data:
                data_window.border(0)
                data_window.addstr(0, 2, 'GPS3 Python {}.{}.{} GPSD Interface Showing NMEA protocol'.format(*sys.version_info), curses.A_BOLD)
                data_window.addstr(2, 2, '{}'.format(gps_connection.response))
                data_window.refresh()
                sleep(.4)

    except KeyboardInterrupt:
        shut_down(gps_connection)


def shut_down(gps_connection):
    curses.nocbreak()
    # screen.keypad(False)
    curses.echo()
    curses.endwin()
    gps_connection.close()
    print("Keyboard interrupt received\nTerminated by user\nGood Bye.\n")
    sys.exit(1)


if __name__ == '__main__':
    try:

        if 'json' in add_args().gpsd_protocol:
            show_human()
        if 'nmea' in add_args().gpsd_protocol:
            show_nmea()

    except KeyboardInterrupt:
        shut_down(show_human().gps_connection)
#
# Someday a cleaner Python interface will live here
#
# End
