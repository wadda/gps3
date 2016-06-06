#!/usr/bin/env python3.5
# coding=utf-8
"""Threaded gps client"""
from threading import Thread
from time import sleep

try: # This kludge to get around imports with files and directories the same name.
    from gps3 import agps3  # Python 3
except ImportError:
    from . import agps3  # Python 2



__author__ = 'Moe'
__copyright__ = 'Copyright 2016  Moe'
__license__ = 'MIT'
__version__ = '0.2'

HOST = '127.0.0.1'  # gpsd
GPSD_PORT = 2947  # defaults
PROTOCOL = 'json'  # "


class AGPS3mechanism(object):
    """Create threaded data stream as updated object attributes
    """

    def __init__(self):
        self.socket = agps3.GPSDSocket()
        self.data_stream = agps3.Dot()

    def stream_data(self, host=HOST, port=GPSD_PORT, enable=True, gpsd_protocol=PROTOCOL, devicepath=None):
        """ Connect and command, point and shoot, flail and bail
        """
        self.socket.connect(host, port)
        self.socket.watch(enable, gpsd_protocol, devicepath)

    def unpack_data(self, usnap=.2):  # 2/10th second sleep between empty requests
        """ Iterates over socket response and refreshes values of object attributes.
        Sleeping here has the greatest response to cpu cycles short of blocking sockets
        """
        for new_data in self.socket:
            if new_data:
                self.data_stream.unpack(new_data)
            else:
                sleep(usnap)  # Sleep in seconds after an empty look up.

    def run_thread(self, usnap=.2, daemon=True):
        """run thread with data
        """
        # self.stream_data() # Unless other changes are made this would limit to localhost only.
        gps3_data_thread = Thread(target=self.unpack_data, args={usnap: usnap}, daemon=True)
        gps3_data_thread.start()

    def stop(self):
        """ Stop as much as possible, as gracefully as possible, if possible.
        """
        self.socket.close()  # Close socket, thread is on its own so far.
        self.
        print('Process stopped by user')
        print('Good bye.')


    def join(self, timeout=None):
        """ Stop the thread and wait for it to end. """
        self._stopevent.set()
        threading.Thread.join(self, timeout)

if __name__ == '__main__':
    from gps3.misc import add_args
    args = add_args()

    agps3_thread = AGPS3mechanism()  # The thread triumvirate
    agps3_thread.stream_data(host=args.host, port=args.port, gpsd_protocol=args.gpsd_protocol)
    agps3_thread.run_thread(usnap=.2)  # Throttle sleep between empty lookups in seconds defaults = 0.2 of a second.

    nod = 0
    seconds_nap = int(args.seconds_nap)  # Threaded Demo loop 'seconds_nap' is not the same as 'usnap'
    while nod <= seconds_nap - 1:
        for nod in range(1, seconds_nap):
            print('{}% completed wait period'.format(round(100 * (nod / seconds_nap), 2)))
            nod += 1
            sleep(1)

        print('\nGPS3 Thread is still functioning at {}'.format(agps3_thread.data_stream.time))
        print('Lat:{}  Lon:{}  Speed:{}  Course:{}\n'.format(agps3_thread.data_stream.lat, agps3_thread.data_stream.lon,
                                                          agps3_thread.data_stream.speed,
                                                          agps3_thread.data_stream.track))
        nod = 0
