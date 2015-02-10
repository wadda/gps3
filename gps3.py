#!/usr/bin/env python3
# coding=utf-8
"""Python( 2.7 - 3.4 ) interface to gpsd """
from __future__ import print_function
from datetime import datetime
import socket
import select
import time
import sys
import json

__author__ = 'Moe'
__copyright__ = "Copyright 2015  Maurice Wick"  # nihil sub sole novum.  Everything learned/adapted from somewhere else.
__license__ = "MIT"  # Don't forget. Don't abused. Pass it along. TODO: figure the rest out, jot and tittle.
__version__ = "0.1a"

GPSD_PORT = 2947
HOST = "127.0.0.1"
PROTOCOL = 'json'


class GPSDSocket(object):
    """Isolate socket handling"""

    def __init__(self, host=HOST, port=GPSD_PORT, gpsd_protocol=PROTOCOL, devicepath=None, verbose=False):
        self.devicepath_alternate = devicepath
        # self.output = {}  # TODO: an attribute by itself decision, essentially raw socket JSON unless it's not;-)
        self.response = None
        self.protocol = gpsd_protocol  # What form of data to retrieve from gpsd  TODO: can it handle multiple?
        self.streamSock = None  # Existential
        self.verbose = verbose

        if host:
            self.connect(host, port)  # No host/port will fail here

    def connect(self, host, port):
        """Connect to a host on a given port. """
        for alotta_stuff in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):  # Default parameters
            family, socktype, proto, _canonname, host_port = alotta_stuff
            try:
                self.streamSock = socket.socket(family, socktype, proto)
                self.streamSock.connect(host_port)
                self.streamSock.setblocking(False)
                if self.verbose:
                    print('Connecting to gpsd at {0} on port \'{1}\','.format(host, port))
                    print('and will be watching ', self.protocol, ' protocol')

            except OSError as error:
                sys.stderr.write('\nGPSDSocket.connect OSError is-->', error)
                sys.stderr.write('\nAttempt to connect to a gpsd at {0} on port \'{1}\' failed:\n'.format(host, port))
                sys.stderr.write('Please, check your number and dial again.\n')
                self.close()
                sys.exit(1)  # TODO: gpsd existence check and start

            finally:
                self.watch(gpsd_protocol=self.protocol)

    def watch(self, enable=True, gpsd_protocol='json', devicepath=None):
        """watch gpsd in various gpsd_protocols or devices.  The gpsd_protocols could be: 'json', 'nmea', 'rare', 'raw',
        'scaled', 'timing', 'split24', and 'pps'; with option for non-default device path"""
        command = '?WATCH={{"enable":true,"{0}":true}}'.format(gpsd_protocol)
        # TODO: does 'timing' need to be worked in like 'devicepath'? cf. gpsprof from gpsd project
        if gpsd_protocol == 'human':
            command = command.replace('human', 'json')
        if gpsd_protocol == 'rare':
            command = command.replace('"rare":true', '"raw":1')  # TODO: This doesn't work like this.  FIXME:
        if gpsd_protocol == 'raw':
            command = command.replace('"raw":true', '"raw",2')  # TODO: This doesn't work like this.  FIXME:
        if not enable:
            command = command.replace('true', 'false')
        if devicepath:
            command = command.replace('}', ',"device":"') + devicepath + '"}'  # TODO: can it handle multiple?
        # TODO: add scaled, split24, pps, ais, and rtcm2/3, etc..
        return self.send(command)

    def send(self, commands):
        """Ship commands to the daemon"""
        # session.send("?POLL;")  # TODO: Figure a way to work this in.
        # The POLL command requests data from the last-seen fixes on all active GPS devices.
        # Devices must previously have been activated by ?WATCH to be pollable.
        if sys.version_info[0] < 3:  # Not less than 3, but 'broken hearted' because
            self.streamSock.send(commands)  # 2.7 chokes on 'bytes' and 'encoding='
        else:
            self.streamSock.send(bytes(commands, encoding='utf-8'))  # It craps out here when there is no daemon running
            # TODO: Add recovery, check gpsd existence, re/start, etc..

    def __iter__(self):
        """banana"""  # <------- for scale
        return self

    def next(self, timeout=0):
        """Return empty unless new data is ready for the client.  Will sit and wait for timeout seconds"""
        try:
            (waitin, _waitout, _waiterror) = select.select((self.streamSock,), (), (), timeout)
            # poll.register(self.streamSock, POLLIN)  # Could be faster than this method, but is it necessary to change?
            if not waitin:
                return
            else:
                gpsd_response = self.streamSock.makefile()  # was '.makefile(buffering=4096)' In strictly Python3
                self.response = gpsd_response.readline()  # When does this fail?

            return self.response  # No, seriously; when does this fail?

        except OSError as error:
            sys.stderr.write('The readline OSError in GPSDSocket.next is this: ', error)
            return  # TODO: means to recover from error, except it is an error of unknown etiology or frequency. Good luck.

    __next__ = next  # Workaround for changes in iterating between Python 2.7 and 3.4

    def close(self):
        """turn off stream and close socket"""
        if self.streamSock:
            self.watch(enable=False)
            self.streamSock.close()
        self.streamSock = None
        return


class Fix(object):
    """Retrieves JSON Object from GPSDSocket unpacking it into respective gpsd 'class' dictionaries, TPV, SKY, etc."""

    def __init__(self):
        """Sets of potential data packages from a device through gpsd, as generator of class attribute dictionaries"""
        version = {"release", "rev", "proto_major", "proto_minor", "remote"}
        tpv = {"tag", "device", "mode", "time", "ept", "lat", "lon", "alt",
               "track", "speed", "climb", "epx", "epy", "epv", "epd", "eps", "epc"}
        sky = {"gdop", "hdop", "pdop", "tdop", "vdop", "xdop", "ydop", "satellites"}
        gst = {"device", "time", "rms", "major", "minor", "orient", "lat", "lon", "alt"}
        att = {"device", "time", "heading", "mag_st", "pitch", "pitch_st", "yaw", "yaw_st",
               "roll", "roll_st", "dip", "mag_len", "mag_x", "mag_y", "mag_z", "acc_len",
               "acc_x", "acc_y", "acc_z", "gyro_x", "gyro_y", "depth", "temperature"}  # TODO: Check Device flags
        pps = {"device", "real_sec", "real_nsec", "clock_sec", "clock_nsec"}
        device = {"path", "activated", "flags", "driver", "bps", "parity", "stopbits",
                  "subtype", "native", "cycle", "mincycle"}  # TODO: Check Device flags
        poll = {"time", "active", "fixes", "skyviews"}
        devices = {"devices", "remote"}
        # ais = {}  # see: http://catb.org/gpsd/AIVDM.html
        error = {"message"}

        # The thought was a quick repository for stripped down versions, to add/subtract' module data packets'
        packages = {"VERSION": version, "TPV": tpv, "SKY": sky, "ERROR": error}  # "DEVICES": devices, "GST": gst, etc.
        # TODO: Create the full suite of possible JSON objects and a better way for deal with subsets
        for package_name, datalist in packages.items():
            _emptydict = {key: 'n/a' for (key) in datalist}  # There is a case for using None instead of 'n/a'
            setattr(self, package_name, _emptydict)
        self.SKY['satellites'] = [{'PRN': 'n/a', 'ss': 'n/a', 'el': 'n/a', 'az': 'n/a', 'used': 'n/a'}]

    def refresh(self, gpsd_data_package):
        """Sets new socket data as Fix attributes"""
        try:  # 'class', a reserved word is popped to allow, if desired, 'setattr(package_name, key, a_package[key])'
            fresh_data = json.loads(gpsd_data_package)  # error is named "ERROR" the same as the gpsd data package
            package_name = fresh_data.pop('class', 'ERROR')  # If error, return 'ERROR' except if it happened, it
            a_package = getattr(self, package_name, package_name)  # should have been too broken to get to this point.
            for key in a_package.keys():  # Iterate attribute package  TODO: It craps out here when device disappears
                a_package[key] = fresh_data.get(key, 'n/a')  # that is, update it, and if key is absent in the socket
                                                                # response, present --> "key: 'n/a'" instead.'
        except (ValueError, KeyError) as error:  # This should not happen, most likely why it's an exception.  But, it
            sys.stderr.write('There was a Value/KeyError at GPSDSocket.refresh: ', error,
                             '\nThis should never happen.')  # happened once.  But I've no idea aside from it broke.
            pass

    def satellites_used(self):  # Should this be ancillary to this class, or even included?
        total_satellites = 0
        used_satellites = 0
        for sats in self.SKY['satellites']:
            if sats['used'] is 'n/a':
                return 0, 0
            used = sats['used']
            total_satellites += 1
            if used:
                used_satellites += 1

        return total_satellites, used_satellites

    def make_datetime(self):  # Should this be ancillary to this class, or even included?
        """Creates timezone -naive- datetime object from gpsd data"""
        if 'n/a' not in self.TPV['time']:
            gps_datetime_object = (datetime.strptime(self.TPV['time'], "%Y-%m-%dT%H:%M:%S.%fZ"))
        else:  # shouldn't break anything, but return wrong Time, when IT, PO, ES, and PT switch to gregorian calendar
            gps_datetime_object = datetime.strptime('1582-10-04T12:00:00.000Z', "%Y-%m-%dT%H:%M:%S.%fZ")  # to the sec.

        return gps_datetime_object


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()  # TODO: beautify and idiot-proof makeover to prevent clash from options error
    # Defaults from the command line
    parser.add_argument('-human', dest='gpsd_protocol', const='human', action='store_const', default='human', help='DEFAULT Human Friendlier ')
    parser.add_argument('-host', action='store', dest='host', default='127.0.0.1', help='DEFAULT "127.0.0.1"')
    parser.add_argument('-port', action='store', dest='port', default='2947', help='DEFAULT 2947', type=int)
    parser.add_argument('-metric', dest='units', const='metric', action='store_const', default='metric', help='DEFAULT METRIC units')
    parser.add_argument('-ddd', dest='latlon_format', const='ddd', action='store_const', default=None, help='Degree decimal')
    parser.add_argument('-dmm', dest='latlon_format', const='dmm', action='store_const', default=None, help='Degree, Minute decimal')
    parser.add_argument('-dms', dest='latlon_format', const='dms', action='store_const', default=None, help='Degree, Minute, Second decimal')
    # Verbose
    parser.add_argument("-verbose", action="store_true", default=False, help="increases verbosity, but not that much")
    # Alternate devicepath
    parser.add_argument('-device', dest='devicepath', action='store', help='alternate devicepath e.g.,"/dev/ttyUSB4"')
    parser.add_argument('-json', dest='gpsd_protocol', const='json', action='store_const', help='/* output as JSON objects */')
    parser.add_argument('-nautical', dest='units', const='nautical', action='store_const', help='/* output in NAUTICAL units */')
    parser.add_argument('-imperial', dest='units', const='imperial', action='store_const', help='/* output in IMPERIAL units */')
    # Work/storage shed, and heap.
    parser.add_argument('-nmea', dest='gpsd_protocol', const='nmea', action='store_const', help='/* output in NMEA */')
    parser.add_argument('-rare', dest='gpsd_protocol', const='rare', action='store_const', help='/* output of packets in hex */')
    parser.add_argument('-raw', dest='gpsd_protocol', const='raw', action='store_const', help='/* output of raw packets */')
    parser.add_argument('-scaled', dest='gpsd_protocol', const='scaled', action='store_const', help='/* scale output to floats */')
    parser.add_argument('-timimg', dest='gpsd_protocol', const='timing', action='store_const', help='/* timing information */')
    parser.add_argument('-split24', dest='gpsd_protocol', const='split24', action='store_const', help='/* split AIS Type 24s */')
    parser.add_argument('-pps', dest='gpsd_protocol', const='pps', action='store_const', help='/* enable PPS JSON */')

    args = parser.parse_args()
    session = GPSDSocket(args.host, args.port, args.gpsd_protocol, args.devicepath, args.verbose)  # The setup
    fix = Fix()

    if args.verbose:
        print("verbose is in chatty mode")
        print('The command line arguments are: ', args)

    try:  # TODO: Tidy up for other protocols run on commandline
        for socket_response in session:
            if socket_response is None:
                print('Socket response is: \'None\' Do you know why?')
            elif socket_response and args.gpsd_protocol is 'human':  # Output for humans because it's the command line.
                fix.refresh(socket_response)
                print('{:^45}'.format('This gps3 interface is using Python {}.{}.{}'.format(*sys.version_info)))  # Flagpole kludge
                print('Connected to a gpsd on host {0.host}, port {0.port}.'.format(args))
                print('It reports a device at {}\n'.format(fix.TPV['device']))

                print('{:^55}'.format("Iterated Satellite Data"))
                for sats in fix.SKY['satellites'][0:10]:
                    print('      Sat {PRN:->3}: Signal: {ss:>2}  {el:>2}:el-az:{az:<3}  Used: {used}'.format(**sats))
                print('  Using {0[1]} of {0[0]} satellites in view (truncated list) providing \n'.format(fix.satellites_used()))

                print('Error estimate - epx:{epx}, epy:{epy}, epv:{epv} in metres'.format(**fix.TPV))
                print('Device coordinates- Latitude:{lat:0<11}  Longitude: {lon:0<12}'.format(**fix.TPV))
                print('Speed: {speed} metres/second tracking {track} degrees from True North'.format(**fix.TPV))
                print('Altitude: {} metres; etc.  All data is the respective gpsd \'class\'[key]'.format(fix.TPV['alt']))
                print('Via: session = GPSDSocket() and fix =  Fix() e.g., fix.TPV[\'time\'], yielding')
                print(fix.make_datetime(), 'UTC, a naive Datetime Object derived from that time string')

            else:
                print('Socket Response is:', socket_response)  # Output Nones and other protocols

            time.sleep(.9)  # to keep from spinning silly.

    except KeyboardInterrupt:
        session.close()
        print("Keyboard interrupt received\nTerminated by user\nGood Bye.\n")
        sys.exit(1)
#
# Someday a cleaner Python interface will live here
#
# End
