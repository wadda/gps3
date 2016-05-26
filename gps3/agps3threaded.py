#!/usr/bin/env python3.5
# coding=utf-8
"""Threaded gps client"""
from threading import Thread
from time import sleep

import agps3

__author__ = 'Moe'
__copyright__ = 'Copyright 2016  Moe'
__license__ = 'MIT'
__version__ = '0.1'

HOST = '127.0.0.1'  # gpsd
GPSD_PORT = 2947  # defaults
PROTOCOL = 'json'  # "


class AGPS3mechanism(object):
    """Create threaded data stream as updated object attributes
    """

    def __init__(self):
        self.socket = agps3.GPSDSocket()
        self.data_stream = agps3.Dot()

    def stream_data(self, host=HOST, port=GPSD_PORT, gpsd_protocol=PROTOCOL):
        """ Connect and command, point and shoot, flail and bail
        """
        self.socket.connect(host, port)
        self.socket.watch(gpsd_protocol)

    def unpack_data(self, usnap=.2):  # 2/10th second sleep between empty requests
        """ Iterates over socket response and refreshes values of object attributes.
        Sleeping here has the greatest response to cpu cycles short of blocking sockets
        """
        for new_data in self.socket:
            if new_data:
                self.data_stream.unpack(new_data)
            else:
                sleep(usnap)

    def run_thread(self, usnap=.2):
        """run thread with data
        """
        # self.stream_data()
        gps3_data_thread = Thread(group=None, target=self.unpack_data, args={'usnap': usnap})
        gps3_data_thread.start()

    def stop(self):
        """ Stop as much as possible, as gracefully as possible, if possible.
        """
        self.socket.close()
        # Thread.isAlive kill killkill...why are you running away?
        print('Process stopped by user')
        print('Good bye.')


def add_args():
    """Adds commandline arguments and formatted Help"""
    parser = argparse.ArgumentParser()

    parser.add_argument('-host', action='store', dest='host', default='127.0.0.1', help='DEFAULT "127.0.0.1"')

    parser.add_argument('-port', action='store', dest='port', default='2947', help='DEFAULT 2947', type=int)
    parser.add_argument('-json', dest='gpsd_protocol', const='json', action='store_const', default='json',
                        help='DEFAULT JSON objects */')
    parser.add_argument('-device', dest='devicepath', action='store',
                        help='alternate devicepath e.g.,"-device /dev/ttyUSB4"')
    # Infrequently used options
    parser.add_argument('-nmea', dest='gpsd_protocol', const='nmea', action='store_const', help='*/ output in NMEA */')
    parser.add_argument('-v', '--version', action='version', version='Version: {}'.format(__version__))
    parser.add_argument('-seconds_nap', action='store', dest='seconds_nap', default='20',
                        help='Demo DEFAULT "20 Sec Nap"')
    cli_args = parser.parse_args()
    return cli_args


if __name__ == '__main__':
    import argparse

    args = add_args()

    agps3_thread = AGPS3mechanism()  # The thread triumvirate
    agps3_thread.stream_data(host=args.host, port=args.port, gpsd_protocol=args.gpsd_protocol)
    agps3_thread.run_thread()  # Throttle sleep between empty lookups in seconds defaults = 0.2 two tenths of a second.

    nod = 0
    seconds_nap = int(args.seconds_nap)
    while nod <= seconds_nap - 1:
        for nod in range(1, seconds_nap):
            print('{}% completed wait period'.format(round(100 * (nod / seconds_nap), 2)))
            nod += 1
            sleep(1)

        print('\nGPS3 Thread is still functioning at {}'.format(agps3_thread.data_stream.time))
        print('Lat:{} Lon:{} Speed:{} Course:{}\n'.format(agps3_thread.data_stream.lat, agps3_thread.data_stream.lon,
                                                          agps3_thread.data_stream.speed,
                                                          agps3_thread.data_stream.track))
        nod = 0
