# !/usr/bin/python3
# coding=utf-8
"""Python3 interface to gpsd """
import socket
import select
import time
import sys
import json

GPSD_PORT = 2947
HOST = "127.0.0.1"
PROTOCOL = 'json'


class GPSDSocket(object):
    """Isolate socket handling"""

    def __init__(self, host=HOST, port=GPSD_PORT, gpsd_protocol=PROTOCOL, devicepath=None, verbose=False):
        self.devicepath_alternate = devicepath
        # self.output = {}  # TODO: a class by itself decision
        self.response = None
        self.protocol = gpsd_protocol  # What form of data to retrieve from gpsd
        self.streamSock = None  # Existential
        self.verbose = verbose

        if host is not None:
            self.connect(host, port)

    def connect(self, host, port):
        """Connect to a host on a given port. """
        for alotta_stuff in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
            afamily, socktype, proto, _canonname, host_port = alotta_stuff
            try:
                self.streamSock = socket.socket(afamily, socktype, proto)
                self.streamSock.connect(host_port)
                self.streamSock.setblocking(False)
                if self.verbose:
                    print('Conecting to gpsd at {0} on port \'{1}\','.format(host, port))
                    print('and will be watching ', self.protocol, ' protocol')

            except OSError as error:
                print('\nconnect OSError is----->', error, file=sys.stderr)  # TODO: Make Python2.7 compliant
                print('\nAttempt to connect to a gpsd at {0} on port \'{1}\' failed:\n'.format(host, port),
                      file=sys.stderr)  # TODO: Make Python2.7 compliant
                print('Please, check your number and dial again.\n', file=sys.stderr)  # TODO: Make Python2.7 compliant
                self.close()
                sys.exit(1)  # TODO: gpsd check and start

            finally:
                self.watch(gpsd_protocol=self.protocol)

    def watch(self, enable=True, gpsd_protocol='json', devicepath=None):
        """watch gpsd in various gpsd_protocols or devices.  The gpsd_protocols
        could be: 'json', 'nmea', 'rare', 'raw', 'scaled', 'timing',
        'split24', and 'pps'; with option for non-default device path"""
        command = '?WATCH={{"enable":true,"{0}":true}}'.format(gpsd_protocol)
        if gpsd_protocol == 'human':
            command = command.replace('human', 'json')  # TODO: rework this for better presentation
        if gpsd_protocol == 'rare':
            command = command.replace('"rare":true', '"raw":1')
        if gpsd_protocol == 'raw':
            command = command.replace('"raw":true', '"raw",2')
        if not enable:
            command = command.replace('true', 'false')
        if devicepath:
            command = command.replace('}', ',"device":"') + devicepath + '"}'
        return self.send(command)

    def send(self, commands):
        """Ship commands to the daemon"""
        # session.send("?POLL;")  # TODO: remember why this is here.  It has to do with ?WATCH
        self.streamSock.send(bytes(commands, encoding='utf-8'))
        # This is where it craps out when there is no daemon running  TODO: Add recovery

    def __iter__(self):
        return self

    def __next__(self, timeout=0):
        """Return empty unless new data is ready for the client.  Will sit and wait for timeout seconds"""
        try:
            (waitin, _waitout, _waiterror) = select.select((self.streamSock,), (), (), timeout)
            # poll.register(self.streamSock, POLLIN)  # Could be faster than that, but...
            if not waitin:
                return
            else:
                gpsd_response = self.streamSock.makefile(buffering=4096)
                self.response = gpsd_response.readline()  # When does this fail?

            return self.response  # No, seriously; when does this fail?

        except OSError as error:
            print('The readline OSError is this: ', error)
            return
            # if waitin == -1:
            # raise StopIteration  # TODO: error recovery, tell why; e.g., no gpsd, no gps, etc.

    def close(self):
        """turn off stream and close socket"""
        if self.streamSock:
            self.watch(enable=False)
            self.streamSock.close()
        self.streamSock = None


class Fix(object):
    """banana"""

    def __init__(self):
        """Sets and Generator of class attributes from data 'packages' available fron the device through the GPSD"""
        version = {"release", "rev", "proto_major", "proto_minor", "remote"}
        tpv = {"tag", "device", "mode", "time", "ept", "lat", "lon", "alt", "epx", "epy", "epv", "track", "speed",
               "climb", "epd", "eps", "epc"}
        sky = {"xdop", "ydop", "vdop", "tdop", "hdop", "gdop", "pdop", "satellites"}
        devices = {"devices", "remote"}  # device set needs to be checked?
        # Others to be added.  The thought is to have a quick repository to add/subtract
        packages = {"VERSION": version, "DEVICES": devices, "TPV": tpv, "SKY": sky}  # 'module data packets'
        # Why clutter with code when you can clutter with comments

        for package_name, datalist in packages.items():  # which can be empty or big
            _emptydict = {key: "n/a" for (key) in datalist}  # big_dict = dict(zip(datalist, (len(datalist) * "n/a")))
            setattr(self, package_name, _emptydict)

    def refresh(self, gpsd_data_package):
        """Sets new socket data as Fix attributes"""

        try:  # 'class' is reserved and popped to allow possible attributes
            fresh_data = json.loads(gpsd_data_package)  # error should be same as named "ERROR" package from gpsd
            package_name = fresh_data.pop('class', 'ERROR')  # I don't know what that does, as if it happened, it should
            a_package = getattr(self, package_name)  # have been too broken to run.
            for key in a_package.keys():
                a_package[key] = fresh_data.get(key, "n/a")  # that is, update, but if key is absent, present key:'n/a'

        except (ValueError, KeyError) as error:
            print('There was a Value/KeyError with:', error, 'This should never happen.', file=sys.stderr)

        finally:
            self.weep()  # TODO: Move
            pass

    def used_satellites(self):
        total_birds = 0
        used_birds = 0
        for sats in self.SKY['satellites']:
            while isinstance(sats, str):
                return 0, 0
            used = sats['used']
            total_birds += 1
            if used:
                used_birds += 1
        return used_birds, total_birds

    def weep(self):
        """Read the data and shake what your mama give ya'"""

        print('Latitude: {0}  Longitude: {1}'.format(self.TPV['lat'], self.TPV['lon']))
        print('Speed: {0}  Course: {1}'.format(self.TPV['speed'], self.TPV['track']))
        print('Altitude: {1}    Time: {0}'.format(self.TPV['time'], self.TPV['alt']))
        print('Error estimate - epx:{0}, epy:{1}, epv:{2}'.format(self.TPV['epx'], self.TPV['epy'], self.TPV['epv']))
        print('Using {0[0]} of {0[1]} satellites in view'.format(self.used_satellites()))

        return


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()  # TODO: beautify and idiot-proof makeover to prevent clash from options error
    # Defaults from the command line
    parser.add_argument('-human', dest='gpsd_protocol', const='human', action='store_const', default='human', help='DEFAULT Human Friendly ')
    parser.add_argument('-host', action='store', dest='host', default='127.0.0.1', help='DEFAULT "127.0.0.1"')
    parser.add_argument('-port', action='store', dest='port', default='2947', help='DEFAULT 2947', type=int)
    parser.add_argument('-metric', dest='units', const='metric', action='store_const', default='metric', help='DEFAULT METRIC units')
    parser.add_argument('-ddd', dest='latlon_format', const='ddd', action='store_const', default=None, help='Degree decimal')
    parser.add_argument('-dmm', dest='latlon_format', const='dmm', action='store_const', default=None, help='Degree, Minute decimal')
    parser.add_argument('-dms', dest='latlon_format', const='dms', action='store_const', default=None, help='Degree, Minute, Second decimal')

    # Verbose
    parser.add_argument("-verbose", action="store_true", default=False, help="increases verbosity, but not that much")
    # Alternate devicepath
    parser.add_argument('-device', dest='devicepath', action='store', help='alternate devicepath e.g.,"/dev/ttyUSB0"')
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

    if args.verbose:
        print("verbose is in chatty mode")
        print('These are the command line arguments: ', args)

    session = GPSDSocket(args.host, args.port, args.gpsd_protocol, args.devicepath, args.verbose)  # The setup
    fix = Fix()
    try:
        for socket_response in session:
            if socket_response and args.gpsd_protocol is 'human':  # Output for the humans, JSON module chokes on None
                fix.refresh(socket_response)
                # if latlon_format is "degree_decimal":
            else:
                print('So far we have:', socket_response, 'Is this a timing issue?')  # Other output for other humans and Nones

            time.sleep(.9)  # to keep from spinning silly.
            doitagain_yeah = True

    except KeyboardInterrupt:
        session.close()
        print("\nTerminated by user\nGood Bye.\n")
        sys.exit(1)
#
# Someday a cleaner Python interface will live here
#
# End
#
