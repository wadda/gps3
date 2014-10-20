# coding=utf-8
"""Python3 interface to gpsd """
import socket
import select
import time
import sys
import json

GPSD_PORT = 2947
HOST = "127.0.0.1"  # "121.211.81.51"
PROTOCOL = 'json'


class GPSDSocket():
    """Isolate socket handling"""

    def __init__(self, host=HOST, port=GPSD_PORT, protocol=PROTOCOL, devicepath=None, verbose=False):
        self.devicepath = devicepath
        self.output = {}  # TODO: a class by itself decision
        self.response = None
        self.protocol = protocol
        self.streamSock = None
        self.verbose = verbose

        if host is not None:
            self.connect(host, port)

    def connect(self, host, port):
        """Connect to a host on a given port.
        :param port:
        :param host:
        """
        for alotta_stuff in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
            afamily, socktype, proto, _canonname, host_port = alotta_stuff
            try:
                self.streamSock = socket.socket(afamily, socktype, proto)
                self.streamSock.connect(host_port)
                self.streamSock.setblocking(False)
                if self.verbose:
                    print('Conecting to gpsd on', host_port)
                    print('and will be watching ', self.protocol, ' protocol')

            except OSError as error:
                print('\nconnect OSError is----->', error, file=sys.stderr)  # TODO: Make Python2.7 compliant
                print('\nAttempt to connect to gpsd on {0} at port \'{1}\' failed:\n'.format(host, port),
                      file=sys.stderr)  # TODO: Make Python2.7 compliant
                print('Please, check your number and dial again.\n', file=sys.stderr)  # TODO: Make Python2.7 compliant
                self.close()
                sys.exit(1)  # TODO: gpsd check and start

            finally:
                self.watch(protocol=self.protocol)

    def watch(self, enable=True, protocol='json', devicepath=None):
        """watch gpsd in various protocols or devices.  The protocols
        could be: 'json', 'nmea', 'rare', 'raw', 'scaled', 'timing',
        'split24', and 'pps'; with option for non-default device path
        :param devicepath:
        :param protocol:
        :param enable:
        """
        command = '?WATCH={{"enable":true,"{0}":true}}'.format(protocol)
        if protocol == 'human':
            command = command.replace('human', 'json')  # TODO: rework proof of concept hack
        if protocol == 'rare':
            command = command.replace('"rare":true', '"raw":1')
        if protocol == 'raw':
            command = command.replace('"raw":true', '"raw",2')
        if not enable:
            command = command.replace('true', 'false')
        if devicepath:
            command = command.replace('}', ',"device":"') + devicepath + '"}'
        return self.send(command)

    def send(self, commands):
        """Ship commands to the daemon.
        :param commands:
        """  # session.send("?POLL;")  # TODO: remember why this is here.
        self.streamSock.send(bytes(commands, encoding='utf-8'))

    def __iter__(self):
        return self

    def __next__(self, timeout=0):
        """Return empty unless new data is ready for the client.  Will sit and wait for
        :param timeout:
        """
        try:
            # poll.register(self.streamSock, POLLIN)  # Could be  faster than
            (waitin, _waitout, _waiterror) = select.select((self.streamSock,), (), (), timeout)
            if not waitin:
                return
            else:
                gpsd_response = self.streamSock.makefile()
                self.response = gpsd_response.readline()  # When does this fail?

            return self.response

        except OSError as error:
            print('readline OSError is this: ', error)
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

    def __init__(self):
        version = ("class", "release", "rev", "proto_major", "proto_minor", "remote")
        tvp = ("class", "tag", "device", "mode", "time", "ept", "lat", "lon", "alt",
               "epx", "epy", "epv", "track", "speed", "climb", "epd", "eps", "epc")
        sky = ("class", "xdop", "ydop", "vdop", "tdop", "hdop", "gdop", "pdop", "satellites")

        self.VERSION = {key: "n/a" for (key) in version}
        self.TPV = {key: "n/a" for (key) in tvp}
        self.SKY = {key: "n/a" for (key) in sky}

    def update(self, socket_response):
        """Mostly a quick proof of concept
        :param socket_response:
        """  # TODO: find less clumbsy sub-dictionary access

        try:
            jsondata = socket_response
            updated_json = json.loads(jsondata)
            # if updated_json['class']:
            #     key = updated_json['class']
            self.TPV.update(updated_json) # TODO: Impliment 'key'.update

            print('Latitude: {0} Longitude: {1}'.format((self.TPV['lat']), (self.TPV['lon'])))
            print('Time: {0} Altitude: {1}'.format((self.TPV['time']), (self.TPV['alt'])))
            print('Speed: {0}  Course: {1}'.format((self.TPV['speed']), (self.TPV['track'])))

        except KeyError as error:
            print('There was a KeyError with:', error)

            return


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()  # TODO: beautify and idiot-proof makeover to prevent clash from options error
    # Defaults from the command line
    parser.add_argument('-human', dest='protocol', const='human', action='store_const', default='human', help='DEFAULT Human Friendly ')
    parser.add_argument('-host', action='store', dest='host', default='127.0.0.1', help='DEFAULT "127.0.0.1"')
    parser.add_argument('-port', action='store', dest='port', default='2947', help='DEFAULT 2947', type=int)
    parser.add_argument('-metric', dest='units', const='metric', action='store_const', default='metric', help='DEFAULT METRIC units')
    # Verbose
    parser.add_argument("-verbose", action="store_true", help="increases verbosity, but not that much")
    # Alternate devicepath
    parser.add_argument('-device', dest='devicepath', action='store', help='alternate devicepath e.g.,"/dev/ttyUSB0"')
    parser.add_argument('-json', dest='protocol', const='json', action='store_const', help='/* output as JSON objects */')
    parser.add_argument('-nautical', dest='units', const='nautical', action='store_const', help='/* output in NAUTICAL units */')
    parser.add_argument('-imperial', dest='units', const='imperial', action='store_const', help='/* output in IMPERIAL units */')
    # Work/storage shed, and heap.
    parser.add_argument('-nmea', dest='protocol', const='nmea', action='store_const', help='/* output in NMEA */')
    parser.add_argument('-rare', dest='protocol', const='rare', action='store_const', help='/* output of packets in hex */')
    parser.add_argument('-raw', dest='protocol', const='raw', action='store_const', help='/* output of raw packets */')
    parser.add_argument('-scaled', dest='protocol', const='scaled', action='store_const', help='/* scale output to floats */')
    parser.add_argument('-timimg', dest='protocol', const='timing', action='store_const', help='/* timing information */')
    parser.add_argument('-split24', dest='protocol', const='split24', action='store_const', help='/* split AIS Type 24s */')
    parser.add_argument('-pps', dest='protocol', const='pps', action='store_const', help='/* enable PPS JSON */')

    args = parser.parse_args()

    if args.verbose:
        print("verbose is in chatty mode")
        print('These are the command line arguments: ', args)

    session = GPSDSocket(args.host, args.port, args.protocol, args.devicepath, args.verbose)  # The setup
    fix = Fix()
    try:
        for gpsfix in session:
            if session.response is not None and args.protocol == 'human':
                fix.update(session.response)  # Output for the humans, JSON module chokes on None
            else:
                print('So far we have:', session.response)  # Other for other humans and Nones

            time.sleep(.5)  # A nap to keep from spinning silly.
            doitagain_yeah = True  # and a quick lazy loop.

    except KeyboardInterrupt:
        session.close()
        print("\nTerminated by user\nGood Bye.\n")
        sys.exit(1)
#
# Someday a cleaner Python interface will live here
#
# End
#
