# coding=utf-8
import json
import socket
import select

GPSD_PORT = 2947
HOST = "127.0.0.1"

WATCH_ENABLE = 0x000001  # enable streaming
WATCH_DISABLE = 0x000002  # disable watching
WATCH_JSON = 0x000010  # JSON output
WATCH_NMEA = 0x000020  # output in NMEA
WATCH_RARE = 0x000040  # output of packets in hex
WATCH_RAW = 0x000080  # output of raw packets
WATCH_SCALED = 0x000100  # scale output to floats
WATCH_TIMING = 0x000200  # timing information
WATCH_SPLIT24 = 0x001000  # split AIS Type 24s
WATCH_PPS = 0x002000  # enable PPS in raw/NMEA
WATCH_DEVICE = 0x000800  # watch specific device


class  SocketPuppet():
    """Isolate socket handling and buffering from the protocol interpretation."""

    def __init__(self, host=HOST, port=GPSD_PORT, verbose=False):
        self.streamSock = None  # in case we blow up in connect
        self.results = None
        self.verbose = verbose

        if host is not None:
            self.connect(host, port)

    def connect(self, host, port):
        """Connect to a host on a given port."""
        for alotta_stuff in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
            afamily, socktype, proto, _canonname, host_port = alotta_stuff
            try:
                self.streamSock = socket.socket(afamily, socktype, proto)
                self.streamSock.connect(host_port)
                self.streamSock.setblocking(False)
                # self.streamSock.settimeout(1)
                if self.verbose:
                    print('Conecting to gpsd on', host_port)
                    # self.stream(WATCH_JSON)
            except OSError:
                print('connect fail:', host, port, file=sys.stderr)  # TODO: Make Python2.7 compliant
                self.close()
                continue
            break
        if not self.streamSock:  # Does this ever happen?
            print(' Something is really stuffed in the sockets; possibly no gpsd ',
                  file=sys.stderr)  # TODO: Make Python2.7 compliant
            # sys.exit(1)
            return

    def stream(self, flags=0, devpath=None):
        """Control stream from the daemon, spigot and content"""
        if flags & WATCH_DISABLE:
            arg = '?WATCH={"enable":false'
            if flags & WATCH_JSON:
                arg += ',"json":false'
            if flags & WATCH_NMEA:
                arg += ',"nmea":false'
            if flags & WATCH_RARE:
                arg += ',"raw":1'
            if flags & WATCH_RAW:
                arg += ',"raw":2'
            if flags & WATCH_SCALED:
                arg += ',"scaled":false'
            if flags & WATCH_TIMING:
                arg += ',"timing":false'
            if flags & WATCH_SPLIT24:
                arg += ',"split24":false'
            if flags & WATCH_PPS:
                arg += ',"pps":false'
        else:  # flags & WATCH_ENABLE:
            arg = '?WATCH={"enable":true'
            if flags & WATCH_JSON:
                arg += ',"json":true'
            if flags & WATCH_NMEA:
                arg += ',"nmea":true'
            if flags & WATCH_RARE:
                arg += ',"raw":1'
            if flags & WATCH_RAW:
                arg += ',"raw":2'
            if flags & WATCH_SCALED:
                arg += ',"scaled":true'
            if flags & WATCH_TIMING:
                arg += ',"timing":true'
            if flags & WATCH_SPLIT24:
                arg += ',"split24":true'
            if flags & WATCH_PPS:
                arg += ',"pps":true'
            if flags & WATCH_DEVICE:
                arg += ',"device":"%s"' % devpath
        return self.send(arg + "}")

    def send(self, commands):
        """Ship commands to the daemon."""
        self.streamSock.send(bytes(commands, encoding='utf-8'))

    @property
    def read(self, timeout=1):
        """Return empty unless new data is ready for the client."""
        try:
            (waitin, _waitout, _waiterror) = select.select((self.streamSock,), (), (), timeout)
            if not waitin:
                return
            else:
                gpsd_response = self.streamSock.makefile()
                line = gpsd_response.readline()
                self.results = json.loads(line)
                for key, value in self.results.items():
                    print(key, ": ", value)

        except OSError as e:
            print('OSError is this: ', e)
            return

    def __iter__(self):
        return self

    def __next__(self):
        if self.read == -1:
            raise StopIteration  # TODO: error recovery, tell why; e.g., no gpsd, no gps, etc.

    def close(self):
        if self.streamSock:
            self.streamSock.close()
        self.streamSock = None


if __name__ == '__main__':
    import getopt
    import sys

    (options, arguments) = getopt.getopt(sys.argv[1:], "v")
    streaming = False
    verbose = False
    for (switch, val) in options:
        if switch == '-v':
            verbose = True
    if len(arguments) > 2:
        print('Usage: client.py [-v] [host [port]]')
        sys.exit(1)

    opts = {"verbose": verbose}
    if len(arguments) > 0:
        opts["host"] = arguments[0]
    if len(arguments) > 1:
        opts["port"] = arguments[1]

    session =  SocketPuppet(**opts)
    session.stream(WATCH_JSON)

    for gpsdata in session:
        try:
            doitagain = True  # No, this is just a lazy hacked loop.

        except KeyboardInterrupt:
            session.close()
            print("Terminated by user")
#
# Someday a cleaner Python interface will live here
#
# End
