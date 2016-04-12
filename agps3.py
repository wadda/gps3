#!/usr/bin/env python3
# coding=utf-8
"""
agps3.py is a Python 2.7-3.5 GPSD interface (http://www.catb.org/gpsd)
Defaults host='127.0.0.1', port=2947, gpsd_protocol='json' in two classes.

1) 'GPSDSocket' creates a GPSD socket connection & request/retreive GPSD output.
2) 'Dot' unpacks the streamed gpsd data into object attribute values.

Import           from gps3 import agps3
Instantiate      gps_connection = agps3.GPSDSocket()
                 dot = agps3.Dot()
Iterate          for new_data in gps_connection:
                     if new_data:
                        dot.unpack(new_data)
Use                     print('Lat/Lon = ',dot.lat,' ', dot.lon)
                        print('Altitude = ',dot.alt)

Consult Lines 146-ff for Attribute/Key possibilities.

As long as TPV'time', GST'time', ATT'time', and POLL'time' are the same,
or TPV'device', GST'device', ATT'device, PPS'device', and TOFF'device  is
the same as DEVICES(device)'path' throughout "she'll be right"
"""
from __future__ import print_function

import json
import select
import socket
import sys

__author__ = 'Moe'
__copyright__ = 'Copyright 2015-2016  Moe'
__license__ = 'MIT'
__version__ = '0.22'

HOST = '127.0.0.1'  # gpsd
GPSD_PORT = 2947  # defaults
PROTOCOL = 'json'  # "


class GPSDSocket(object):
    """Establish a socket with gpsd, by which to send commands and receive data."""

    def __init__(self, host=HOST, port=GPSD_PORT, gpsd_protocol=PROTOCOL, devicepath=None):
        self.devicepath_alternate = devicepath
        self.response = None
        self.protocol = gpsd_protocol
        self.streamSock = None

        if host:
            self.connect(host, port)

    def connect(self, host, port):
        """Connect to a host on a given port.
        Arguments:
            port: default port=2947
            host: default host='127.0.0.1'
        """
        for alotta_stuff in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
            family, socktype, proto, _canonname, host_port = alotta_stuff
            try:
                self.streamSock = socket.socket(family, socktype, proto)
                self.streamSock.connect(host_port)
                self.streamSock.setblocking(False)
                self.watch(gpsd_protocol=self.protocol)
            except (OSError, IOError) as error:
                sys.stderr.write('\nGPSDSocket.connect exception is--> {}'.format(error))
                sys.stderr.write('\nAttempt to connect to a gpsd at \'{0}\' on port \'{1}\' failed:\n'.format(host, port))
                sys.exit(1)  # "Lasciate ogne speranza..." TODO: something not failure

    def watch(self, enable=True, gpsd_protocol='json', devicepath=None):
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
        if sys.version_info[0] < 3:  # Not less than 3, but 'broken hearted' because
            self.streamSock.send(commands)  # 2.7 chokes on 'bytes' and 'encoding='
        else:
            self.streamSock.send(bytes(commands, encoding='utf-8'))  # It fails here when there is no gpsd running
            # TODO: Add recovery, check gpsd existence, re/start, etc..

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

        except (OSError, IOError) as error:
            sys.stderr.write('The readline exception in GPSDSocket.next is--> {}'.format(error))

    __next__ = next  # Workaround for changes in iterating between Python 2.7 and 3

    def close(self):
        """turn off stream and close socket"""
        if self.streamSock:
            self.watch(enable=False)
            self.streamSock.close()
        self.streamSock = None


class Dot(object):
    """Retrieve JSON Object(s) from GPSDSocket and unpack it into respective
    object attributes, e.g., self.lat yielding hours of fun and entertainment.
    """
    packages = {
        'VERSION': {'release', 'proto_major', 'proto_minor', 'remote', 'rev'},
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

    def __init__(self):
        """Potential data packages from gpsd for a generator of class attributes"""
        for laundry_list in self.packages.values():
            for thingy in laundry_list:
                setattr(self, thingy, 'n/a')

    def unpack(self, gpsd_data_package):
        """Sets new socket data as Fix attributes in those initialied dictionaries
        Arguments:
            gpsd_data_package (json object):
        Provides:
        self attributes, e.g., self.lat, self.gdop
        Raises:
        AttributeError: 'str' object has no attribute 'keys' when the device falls out of the system
        ValueError, KeyError: most likely extra, or mangled JSON data, should not happen, but that
        applies to a lot of things.
        """
        try:
            fresh_data = json.loads(gpsd_data_package)  # 'class' is popped for interator lead
            class_name = fresh_data.pop('class')
            for key in self.packages[class_name]:
                setattr(self, key, fresh_data.get(key, 'n/a'))  # Updates and restores 'n/a' if attribute is absent in the data

        except AttributeError:  # 'str' object has no attribute 'keys'
            print('No Data')
            return

        except (ValueError, KeyError) as error:
            sys.stderr.write(str(error))  # Look for extra data in stream.
            return


if __name__ == '__main__':
    print(__doc__)

#
# Someday a cleaner Python interface will live here
#
# End
