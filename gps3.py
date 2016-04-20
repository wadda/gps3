#!/usr/bin/env python3
# coding=utf-8
"""
GPS3 (gps3.py) is a Python 2.7-3.5 GPSD interface (http://www.catb.org/gpsd)
Default host='127.0.0.1', port=2947, gpsd_protocol='json'

GPS3 has two classes.
1) 'GPSDSocket' creates a GPSD socket connection & request/retreive GPSD output.
2) 'Fix' unpacks the streamed gpsd data into python dictionaries.

These dictionaries are literated from the JSON data packet sent from the GPSD.

Import          from gps3 import gps3
Instantiate     gps_socket = gps3.GPSDSocket()
                gps_fix = gps3.Fix()
Run             gps_socket.connect()
                gps_socket.watch()
Iterate         for new_data in gps_connection:
                    if new_data:
                        gps_fix.refresh(new_data)
Use                     print('Altitude = ',gps_fix.TPV['alt'])
                        print('Latitude = ',gps_fix.TPV['lat'])

Consult Lines 147-ff for Attribute/Key possibilities.
or http://www.catb.org/gpsd/gpsd_json.html

Run human.py; python[X] human.py [arguments] for a human experience.
"""
from __future__ import print_function

import json
import select
import socket
import sys

__author__ = 'Moe'
__copyright__ = 'Copyright 2015-2016  Moe'
__license__ = 'MIT'
__version__ = '0.30'

HOST = '127.0.0.1'  # gpsd
GPSD_PORT = 2947  # defaults
PROTOCOL = 'json'  # "


class GPSDSocket(object):
    """Establish a socket with gpsd, by which to send commands and receive data."""

    def __init__(self):
        self.streamSock = None
        self.response = None

    def connect(self, host=HOST, port=GPSD_PORT):
        """Connect to a host on a given port.
        Arguments:
            host: default host='127.0.0.1'
            port: default port=2947
        """
        for alotta_stuff in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
            family, socktype, proto, _canonname, host_port = alotta_stuff
            try:
                self.streamSock = socket.socket(family, socktype, proto)
                self.streamSock.connect(host_port)
                self.streamSock.setblocking(False)
            except (OSError, IOError) as error:
                sys.stderr.write('\r\nGPSDSocket.connect exception is--> {}'.format(error))
                sys.stderr.write('\r\nGPS3 connection to a gpsd at \'{0}\' on port \'{1}\' failed\r\n'.format(host, port))

    def watch(self, enable=True, gpsd_protocol=PROTOCOL, devicepath=None):
        """watch gpsd in various gpsd_protocols or devices.
        Arguments:
            enable: (bool) stream data to socket
            gpsd_protocol: (str) 'json' | 'nmea' | 'rare' | 'raw' | 'scaled' | 'split24' | 'pps'
            devicepath: (str) device path - '/dev/ttyUSBn' for some number n or '/dev/whatever_works'
        Returns:
            command: (str) e.g., '?WATCH={"enable":true,"json":true};'
        """
        # N.B.: 'timing' requires special attention, as it is undocumented and lives with dragons.
        command = '?WATCH={{"enable":true,"{0}":true}}'.format(gpsd_protocol)

        if gpsd_protocol == 'rare':  # 1 for a channel, gpsd reports the unprocessed NMEA or AIVDM data stream
            command = command.replace('"rare":true', '"raw":1')
        if gpsd_protocol == 'raw':  # 2 channel that processes binary data, received data verbatim without hex-dumping.
            command = command.replace('"raw":true', '"raw",2')
        if not enable:
            command = command.replace('true', 'false')  # sets -all- command values false .
        if devicepath:
            command = command.replace('}', ',"device":"') + devicepath + '"}'

        return self.send(command)

    def send(self, commands):
        """Ship commands to the daemon
        Arguments:
            commands: e.g., '?WATCH={{'enable':true,'json':true}}'|'?VERSION;'|'?DEVICES;'|'?DEVICE;'|'?POLL;'
        """
        # The POLL command requests data from the last-seen fixes on all active GPS devices.
        # Devices must previously have been activated by ?WATCH to be pollable.
        try:
            self.streamSock.send(bytes(commands, encoding='utf-8'))
        except TypeError:
            self.streamSock.send(commands)  # 2.7 chokes on 'bytes' and 'encoding='
        except (OSError, IOError) as error:  # TODO: HEY MOE, LEAVE THIS ALONE!
            sys.stderr.write('\nGPS3 send command fail with {}\n'.format(error))  # [Errno 107] Transport endpoint is not connected

    def __iter__(self):
        """banana"""  # <------- for scale
        return self

    def next(self, timeout=0):
        """Return empty unless new data is ready for the client.
        Arguments:
            timeout: Default timeout=0  range zero to float specifies a time-out as a floating point
        number in seconds.  Will sit and wait for timeout seconds.  When the timeout argument is omitted
        the function blocks until at least one file descriptor is ready. A time-out value of zero specifies
        a poll and never blocks.
        """
        try:
            waitin, _waitout, _waiterror = select.select((self.streamSock,), (), (), timeout)
            if not waitin: return
            else:
                gpsd_response = self.streamSock.makefile()  # '.makefile(buffering=4096)' In strictly Python3
                self.response = gpsd_response.readline()
            return self.response

        except StopIteration as error:
            sys.stderr.write('The readline exception in GPSDSocket.next is--> {}'.format(error))

    __next__ = next  # Workaround for changes in iterating between Python 2.7 and 3

    def close(self):
        """turn off stream and close socket"""
        if self.streamSock:
            self.watch(enable=False)
            self.streamSock.close()
        self.streamSock = None


class Fix(object):
    """Retrieve JSON Object(s) from GPSDSocket and unpack it into respective
    gpsd 'class' dictionaries, TPV, SKY, etc. yielding hours of fun and entertainment.
    """

    def __init__(self):
        """Potential data packages from gpsd for a generator of class attribute dictionaries"""

        packages = {'VERSION': {'release', 'proto_major', 'proto_minor', 'remote', 'rev'},
                    'TPV': {'alt', 'climb', 'device', 'epc', 'epd', 'eps', 'ept', 'epv', 'epx', 'epy', 'lat', 'lon', 'mode', 'speed', 'tag', 'time', 'track'},
                    'SKY': {'satellites', 'gdop', 'hdop', 'pdop', 'tdop', 'vdop', 'xdop', 'ydop'},
                    # Subset of SKY: 'satellites': {'PRN', 'ss', 'el', 'az', 'used'}  # is always present.
                    'GST': {'alt', 'device', 'lat', 'lon', 'major', 'minor', 'orient', 'rms', 'time'},
                    'ATT': {'acc_len', 'acc_x', 'acc_y', 'acc_z', 'depth', 'device', 'dip', 'gyro_x', 'gyro_y', 'heading', 'mag_len', 'mag_st', 'mag_x',
                            'mag_y', 'mag_z', 'pitch', 'pitch_st', 'roll', 'roll_st', 'temperature', 'time', 'yaw', 'yaw_st'},
                    # 'POLL': {'active', 'tpv', 'sky', 'time'},
                    'PPS': {'device', 'clock_sec', 'clock_nsec', 'real_sec', 'real_nsec', 'precision'},
                    'TOFF': {'device', 'clock_sec', 'clock_nsec', 'real_sec', 'real_nsec'},
                    'DEVICES': {'devices', 'remote'},
                    'DEVICE': {'activated', 'bps', 'cycle', 'mincycle', 'driver', 'flags', 'native', 'parity', 'path', 'stopbits', 'subtype'},
                    # 'AIS': {}  # see: http://catb.org/gpsd/AIVDM.html
                    'ERROR': {'message'}}  # TODO: Full suite of possible GPSD output

        for package_name, dataset in packages.items():
            _emptydict = {key: 'n/a' for key in dataset}
            setattr(self, package_name, _emptydict)

        self.DEVICES['devices'] = {key: 'n/a' for key in packages['DEVICE']}  # How does multiple listed devices work?
        # self.POLL = {'tpv': self.TPV, 'sky': self.SKY, 'time': 'n/a', 'active': 'n/a'}

    def refresh(self, gpsd_data_package):
        """Sets new socket data as Fix attributes in those initialied dictionaries
        Arguments:
            gpsd_data_package (json object):
        Provides:
        self attribute dictionaries, e.g., self.TPV['lat'], self.SKY['gdop']
        Raises:
        AttributeError: 'str' object has no attribute 'keys' when the device falls out of the system
        ValueError, KeyError: most likely extra, or mangled JSON data, should not happen, but that
        applies to a lot of things.
        """
        try:
            fresh_data = json.loads(gpsd_data_package)  # The reserved word 'class' is popped from JSON object class
            package_name = fresh_data.pop('class', 'ERROR')  # gpsd data package errors are also 'ERROR'.
            package = getattr(self, package_name, package_name)  # packages are named for JSON object class
            for key in package.keys():  # TODO: Rollover and retry.  It fails here when device disappears
                package[key] = fresh_data.get(key, 'n/a')  # Updates and restores 'n/a' if key is absent in the socket
                # response, present --> 'key: 'n/a'' instead.'
        except AttributeError:  # 'str' object has no attribute 'keys'
            sys.stderr.write('There is an unexpected exception in Dot.unpack')
            return

        except (ValueError, KeyError) as error:
            sys.stderr.write(str(error))  # Extra data or aberrant data in stream.
            return


if __name__ == '__main__':
    print(__doc__)

#
# Someday a cleaner Python interface will live here
#
# End
