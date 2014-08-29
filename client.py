# coding=utf-8
# This file is Copyright (c) 2010 by the GPSD project
# BSD terms apply: see the file COPYING in the distribution root for details.
#
import socket
import sys


GPSD_PORT = "2947"


class ClientCommon:
    """Isolate socket handling and buffering from the protocol interpretation."""

    def __init__(self, host="127.0.0.1", port=GPSD_PORT, verbose=0):
        self.sock = None  # in case we blow up in connect
        self.linebuffer = ""
        self.response = None
        self.verbose = verbose
        if host is not None:
            self.connect(host, port)

    def connect(self, host, port):
        """Connect to a host on a given port.

        If the hostname ends with a colon (`:') followed by a number, and
        there is no port specified, that suffix will be stripped off and the
        number interpreted as the port number to use.
        """
        for lotta_stuff in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
            afamily, socktype, proto, _canonname, host_port = lotta_stuff
            try:
                self.sock = socket.socket(afamily, socktype, proto)
                if self.verbose:
                    print('connecting:', (host, port))
                self.sock.connect(host_port)
            except OSError:
                print('connect fail:', (host, port), file=sys.stderr)
                self.close()
                continue
            break
        if not self.sock:
            raise OSError

    def close(self):
        if self.sock:
            self.sock.close()
        self.sock = None

    def read(self):
        """Wait for and read data being streamed from the daemon."""
        if self.verbose:
            print("\nread in client.read...\n")
        eol = self.linebuffer.find('\n')
        if eol == -1:
            frag = self.sock.recv(4096)
            self.linebuffer += frag.decode('utf-8')
            if self.verbose:
                print("eol == -1 in client.read...\n")
            if not self.linebuffer:  # Does this ever happen?
                if self.verbose:
                    print("read fail (-1) in client.read...\n", file=sys.stderr)
                return -1  # Read failed

            eol = self.linebuffer.find('\n')
            if eol == -1:
                if self.verbose:
                    print("reading only framgent in client.read (0)...\n", file=sys.stderr)
                return 0  # Read succeeded, but only got a fragment
        else:
            if self.verbose:
                print("I have no GPS FIX is where this comes in, in client.read...", file=sys.stderr)

        # We got a line
        eol += 1
        self.response = self.linebuffer[:eol]
        self.linebuffer = self.linebuffer[eol:]

        # Can happen if daemon terminates while we're reading.
        if not self.response:
            return -1
        if self.verbose:
            print("The read data is:\n ")  #, self.data)  # repr(self.response))

        # We got a \n-terminated line
        return

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

    # def __init__(self):
    # self.data = None

    def __iter__(self):
        return self

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

#
# Someday a cleaner Python interface using this machinery will live here
#

# End
