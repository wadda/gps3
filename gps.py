#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is Copyright (c) 2010 by the GPSD project
# BSD terms apply: see the file COPYING in the distribution root for details.
#
# gps.py -- Python interface to GPSD.
#
# This interface has a lot of historical cruft in it related to old
# protocol, and was modeled on the C interface. It won't be thrown
# away, but it's likely to be deprecated in favor of something more
# Pythonic.
#
# The JSON parts of this (which will be reused by any new interface)
# now live in a different module.
#
import client
# from .misc import isotime

NaN = float('nan')
GPSD_PORT = "2947"

def isnan(x):
    return str(x) == 'nan'

# Don't hand-hack this list, it's generated.
ONLINE_SET = (1 << 1)
TIME_SET = (1 << 2)
TIMERR_SET = (1 << 3)
LATLON_SET = (1 << 4)
ALTITUDE_SET = (1 << 5)
SPEED_SET = (1 << 6)
TRACK_SET = (1 << 7)
CLIMB_SET = (1 << 8)
STATUS_SET = (1 << 9)
MODE_SET = (1 << 10)
DOP_SET = (1 << 11)
HERR_SET = (1 << 12)
VERR_SET = (1 << 13)
ATTITUDE_SET = (1 << 14)
SATELLITE_SET = (1 << 15)
SPEEDERR_SET = (1 << 16)
TRACKERR_SET = (1 << 17)
CLIMBERR_SET = (1 << 18)
DEVICE_SET = (1 << 19)
DEVICELIST_SET = (1 << 20)
DEVICEID_SET = (1 << 21)
RTCM2_SET = (1 << 22)
RTCM3_SET = (1 << 23)
AIS_SET = (1 << 24)
PACKET_SET = (1 << 25)
SUBFRAME_SET = (1 << 26)
GST_SET = (1 << 27)
VERSION_SET = (1 << 28)
POLICY_SET = (1 << 29)
LOGMESSAGE_SET = (1 << 30)
ERROR_SET = (1 << 31)
TIMEDRIFT_SET = (1 << 32)
EOF_SET = (1 << 33)
SET_HIGH_BIT = 34
UNION_SET = (RTCM2_SET | RTCM3_SET | SUBFRAME_SET |
             AIS_SET | VERSION_SET | DEVICELIST_SET | ERROR_SET | GST_SET)
STATUS_NO_FIX = 0
STATUS_FIX = 1
STATUS_DGPS_FIX = 2
MODE_NO_FIX = 1
MODE_2D = 2
MODE_3D = 3
MAXCHANNELS = 20
SIGNAL_STRENGTH_UNKNOWN = NaN

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


class gpsfix:

    def __init__(self):
        self.mode = MODE_NO_FIX
        self.time = NaN
        self.ept = NaN
        self.latitude = self.longitude = 0.0
        self.epx = NaN
        self.epy = NaN
        self.altitude = NaN         # Meters
        self.epv = NaN
        self.track = NaN            # Degrees from true north
        self.speed = NaN            # Knots
        self.climb = NaN            # Meters per second
        self.epd = NaN
        self.eps = NaN
        self.epc = NaN


class gpsdata:

    "Position, track, velocity and status information returned by a GPS."

    class satellite:

        def __init__(self, PRN, elevation, azimuth, ss, used=None):
            self.PRN = PRN
            self.elevation = elevation
            self.azimuth = azimuth
            self.ss = ss
            self.used = used

        def __repr__(self):
            return "PRN: %3d  E: %3d  Az: %3d  Ss: %3d  Used: %s" % (
                self.PRN, self.elevation, self.azimuth, self.ss, "ny"[
                    self.used]
            )

    def __init__(self):
        # Initialize all data members
        self.online = 0                 # NZ if GPS on, zero if not

        self.valid = 0
        self.fix = gpsfix()

        self.status = STATUS_NO_FIX
        self.utc = ""

        self.satellites_used = 0        # Satellites used in last fix
        self.xdop = self.ydop = self.vdop = self.tdop = 0
        self.pdop = self.hdop = self.gdop = 0.0

        self.epe = 0.0

        self.satellites = []            # satellite objects in view

        self.gps_id = None
        self.driver_mode = 0
        self.baudrate = 0
        self.stopbits = 0
        self.cycle = 0
        self.mincycle = 0
        self.device = None
        self.devices = []

        self.version = None

    def __repr__(self):
        st = "Time:     %s (%s)\n" % (self.utc, self.fix.time)
        st += "Lat/Lon:  %f %f\n" % (self.fix.latitude, self.fix.longitude)
        if isnan(self.fix.altitude):
            st += "Altitude: ?\n"
        else:
            st += "Altitude: %f\n" % (self.fix.altitude)
        if isnan(self.fix.speed):
            st += "Speed:    ?\n"
        else:
            st += "Speed:    %f\n" % (self.fix.speed)
        if isnan(self.fix.track):
            st += "Track:    ?\n"
        else:
            st += "Track:    %f\n" % (self.fix.track)
        st += "Status:   STATUS_%s\n" % (
            "NO_FIX",
            "FIX",
            "DGPS_FIX")[self.status]
        st += "Mode:     MODE_%s\n" % (
            "ZERO",
            "NO_FIX",
            "2D",
            "3D")[self.fix.mode]
        st += "Quality:  %d p=%2.2f h=%2.2f v=%2.2f t=%2.2f g=%2.2f\n" % \
              (self.satellites_used, self.pdop,
               self.hdop, self.vdop, self.tdop, self.gdop)
        st += "Y: %s satellites in view:\n" % len(self.satellites)
        for sat in self.satellites:
            st += "    %r\n" % sat
        return st


class gps(client.ClientCommon, gpsdata, client.GpsJson):

    "Client interface to a running gpsd instance."

    def __init__(self, host="127.0.0.1", port=GPSD_PORT, verbose=0, mode=0):
        client.ClientCommon.__init__(self, host, port, verbose)
        gpsdata.__init__(self)
        self.newstyle = False
        if mode:
            self.stream(mode)

    def read(self):
        "Read and interpret data from the daemon."
        status = client.ClientCommon.read(self)
        if status <= 0:
            return status
        if self.response.startswith("{") and self.response.endswith("}\r\n"):
            self.unpack(self.response)
            self.newstyle = True
            self.valid |= PACKET_SET
        elif self.response.startswith("GPSD"):
            self.valid |= PACKET_SET
        return 0

    def __next__(self):
        if self.read() == -1:
            raise StopIteration
        if hasattr(self, "data"):
            return self.data
        else:
            return self.response

    def stream(self, flags=0, devpath=None):
        "Ask gpsd to stream reports at your client."
        if (flags & (WATCH_JSON | WATCH_OLDSTYLE | WATCH_NMEA | WATCH_RAW)) == 0:
            flags |= WATCH_JSON
        if flags & WATCH_DISABLE:
            if flags & WATCH_OLDSTYLE:
                arg = "w-"
                if flags & WATCH_NMEA:
                    arg += 'r-'
                    return self.send(arg)
            else:
                GpsJson.stream(self, ~flags, devpath)
        else:  # flags & WATCH_ENABLE:
            if flags & WATCH_OLDSTYLE:
                arg = 'w+'
                if (flags & WATCH_NMEA):
                    arg += 'r+'
                    return self.send(arg)
            else:
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
