# coding=utf-8
# This file is Copyright (c) 2010 by the GPSD project
# BSD terms apply: see the file COPYING in the distribution root for details.
#
import time
import socket
import sys
import select


if sys.hexversion >= 0x2060000:
    import json			# For Python 2.6
else:
    import simplejson as json  # For Python 2.4 and 2.5

GPSD_PORT = "2947"


class JSONerror(Exception):

    def __init__(self, data, explanation):
        exceptions.Exception.__init__(self)
        self.data = data
        self.explanation = explanation


class ClientCommon:

    """Isolate socket handling and buffering from the protocol interpretation."""

    def __init__(self, host="127.0.0.1", port=GPSD_PORT, verbose=0):
        self.sock = None        # in case we blow up in connect
        self.linebuffer = ""
        self.verbose = verbose
        if host is not None:
            self.connect(host, port)

    def connect(self, host, port):
        """Connect to a host on a given port.

        If the hostname ends with a colon (`:') followed by a number, and
        there is no port specified, that suffix will be stripped off and the
        number interpreted as the port number to use.
        """
        if not port and (host.find(':') == host.rfind(':')):
            i = host.rfind(':')
            if i >= 0:
                host, port = host[:i], host[i + 1:]
            try:
                port = int(port)
            except ValueError:
                raise socket.error("nonnumeric port")
        if self.verbose:
            print('connect:', (host, port))
        msg = "getaddrinfo returns an empty list"
        self.sock = None
        for res in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
            af, socktype, proto, _canonname, sa = res
            try:
                self.sock = socket.socket(af, socktype, proto)
                # if self.verbose: print 'connect:', (host, port)
                self.sock.connect(sa)
            except socket.error as msg:
                # if self.verbose: print 'connect fail:', (host, port)
                self.close()
                continue
            break
        if not self.sock:
            raise socket.error(msg)

    def close(self):
        if self.sock:
            self.sock.close()
        self.sock = None

    def __del__(self):
        self.close()

    def read(self):
        """Wait for and read data being streamed from the daemon."""
        if self.verbose:
            print("read in client.read...\n")
        eol = self.linebuffer.find('\n')
        if eol == -1:
            frag = self.sock.recv(4096)
            self.linebuffer += frag.decode('utf-8')
            if self.verbose:
                print("eol == -1 in client.read...\n")
            if not self.linebuffer: # Does this ever happen?
                if self.verbose:
                    print("read fail (-1) in client.read...\n", file=sys.stderr)
                # Read failed
                return -1
            eol = self.linebuffer.find('\n')
            if eol == -1:
                if self.verbose:
                    print("reading only framgent in client.read (0)...\n", file=sys.stderr)
                # Read succeeded, but only got a fragment
                return 0
        else:
            if self.verbose:
                print("I have no idea why this is here in client.read...", file=sys.stderr)

        # We got a line
        eol += 1
        self.response = self.linebuffer[:eol]
        self.linebuffer = self.linebuffer[eol:]

        # Can happen if daemon terminates while we're reading.
        if not self.response:
            return -1
        if self.verbose:
            print("The read data is: %s\n" % repr(self.response))
        self.received = time.time()
        # We got a \n-terminated line
        return len(self.response)

    def data(self):
        """Return the client data buffer."""
        return self.response

    def send(self, commands):
        """Ship commands to the daemon."""
        if not commands.endswith("\n"):
            commands += "\n"
        self.sock.send(bytes(source=commands, encoding='utf-8'))

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


class GpsJson:

    """Basic JSON decoding."""

    def __iter__(self):
        return self

    def unpack(self, buf):
        try:
            self.data = DictWrapper(json.loads(buf.strip(), encoding="ascii"))
        except ValueError as e:
            raise JSONerror(buf, e.args[0])
        # Should be done for any other array-valued subobjects, too.
        # This particular logic can fire on SKY or RTCM2 objects.
        if hasattr(self.data, "satellites"):
            self.data.satellites = list(map(DictWrapper, self.data.satellites))

    def stream(self, flags=0, devpath=None):
        """Control streaming reports from the daemon,"""
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


class DictWrapper:

    """Wrapper that yields both class and dictionary behavior,"""

    def __init__(self, ddict):
        self.__dict__ = ddict

    def get(self, k, d=None):
        return self.__dict__.get(k, d)

    def keys(self):
        return list(self.__dict__.keys())

    def __getitem__(self, key):
        """Emulate dictionary, for new-style interface."""
        return self.__dict__[key]

    def __setitem__(self, key, val):
        """Emulate dictionary, for new-style interface."""
        self.__dict__[key] = val

    def __contains__(self, key):
        return key in self.__dict__

    def __str__(self):
        return "<DictWrapper: " + str(self.__dict__) + ">"
    __repr__ = __str__

#
# Someday a cleaner Python interface using this machinery will live here
#

# End
