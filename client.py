# coding=utf-8
import socket

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


class ClientCommon:
    """Isolate socket handling and buffering from the protocol interpretation."""
    def __init__(self, host=HOST, port=GPSD_PORT, verbose=0):
        self.sock = None  # in case we blow up in connect
        self.response = None  # because two Nones is the start of
        self.verbose = verbose
        if host is not None:
            self.connect(host, port)

    def connect(self, host, port):
        """Connect to a host on a given port.
        """
        for lotta_stuff in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
            afamily, socktype, proto, _canonname, host_port = lotta_stuff
            try:
                self.sock = socket.socket(afamily, socktype, proto)
                self.sock.connect(host_port)
                if self.verbose:
                    print('Conecting to gpsd on', host_port)
            except OSError:
                print('connect fail:', host, port, file=sys.stderr)
                self.close()
                continue
            break
        if not self.sock:  # Does this ever happen?
            print('_-^-_-^-_-^-_-^-_-^-_-^-_-^-_-^-_-^-_-^-_-', file=sys.stderr)
            print('Something is really stuffed in the sockets', file=sys.stderr)
            print('_-^-_-^-_-^-_-^-_-^-_-^-_-^-_-^-_-^-_-^-_-', file=sys.stderr)
            sys.exit(1)

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
        self.sock.send(bytes(commands, encoding='utf-8'))

    def read(self):
        """Read data streamed from the daemon."""
        if self.verbose:
            print("\nreading JSON Object streamed from the daemon.\n")
        golden_fleece = self.sock.recv(4096)

        if golden_fleece:
            print('The golden fleece is type: ', type(golden_fleece))
            print(golden_fleece)
            return golden_fleece

        else:
            print('gpsd terminated while reading, or something else.', file=sys.stderr)
            return -1  # Test, test, 1,2,3  Is this even on?

    def __iter__(self):
        return self

    def __next__(self):
        if self.read() == -1:
            raise StopIteration  # TODO: error recovery
        if hasattr(self, "data"):
            return self.data  # What's the deal with data and response?

    def data(self):
        """Return the client data buffer."""
        return self.response

    def close(self):
        if self.sock:
            # self.sock.shutdown(flag == SHUT_RDWR) # TODO: syntax and efficacy
            self.sock.close()
        self.sock = None


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

    session = ClientCommon(**opts)
    session.stream(WATCH_JSON)

    try:
        for gpsdata in session:
            print('\nSisyphus')  # Help Me, Mr. Wizard.
    except KeyboardInterrupt:
        # Avoid garble on ^C
        print("Terminated by user")
#
# Someday a cleaner Python interface using this machinery will live here
#
# End
