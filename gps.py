#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import client

GPSD_PORT = "2947"

WATCH_ENABLE = 0x000001  # enable streaming
WATCH_DISABLE = 0x000002  # disable watching
WATCH_JSON = 0x000010  # JSON output
WATCH_NMEA = 0x000020  # output in NMEA
WATCH_RARE = 0x000040  # output of packets in hex
WATCH_RAW = 0x000080  # output of raw packets
WATCH_SCALED = 0x000100  # scale output to floats
WATCH_TIMING = 0x000200  # timing information
WATCH_DEVICE = 0x000800  # watch specific device
WATCH_SPLIT24 = 0x001000  # split AIS Type 24s
WATCH_PPS = 0x002000  # enable PPS JSON
WATCH_NEWSTYLE = 0x010000  # force JSON streaming
WATCH_OLDSTYLE = 0x020000  # force old-style streaming


class gps(client.ClientCommon, client.GpsJson):
    """Client interface to a running gpsd instance."""

    def __init__(self, host="127.0.0.1", port=GPSD_PORT, verbose=0, mode=0):
        client.ClientCommon.__init__(self, host, port, verbose)
        # gpsdata.__init__(self)
        # self.newstyle = False
        if mode:
            self.stream(mode)

    @property
    def __next__(self):
        if self.read() == -1:
            raise StopIteration
        if hasattr(self, "data"):
            if verbose:
                print(self.response)
            return  self.data  # What's the deal with data and response?
        # else:
        #     return self.response

#
# If the following function is commented out the return stop/block after "gps.info" is delivered
    def stream(self, flags=0, devpath=None):
        """Ask gpsd to stream reports at your client."""
        if (flags & (WATCH_JSON | WATCH_OLDSTYLE | WATCH_NMEA | WATCH_RAW)) == 0:
            flags |= WATCH_JSON
        if flags & WATCH_DISABLE:
            client.GpsJson.stream(self, flags, devpath)
        else:  # flags & WATCH_ENABLE:
            client.GpsJson.stream(self, flags, devpath)


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
        print('Usage: gps.py [-v] [host [port]]')
        sys.exit(1)

    opts = {"verbose": verbose}
    if len(arguments) > 0:
        opts["host"] = arguments[0]
    if len(arguments) > 1:
        opts["port"] = arguments[1]

    session = gps(**opts)
    session.stream(WATCH_ENABLE)
    try:
        for report in session:
            print(report)
    except KeyboardInterrupt:
        # Avoid garble on ^C
        print("Terminated by user")

# gps.py ends here
