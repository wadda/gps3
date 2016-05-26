#!/usr/bin/env python3.5
# coding=utf-8
from time import sleep

from agps3threaded import AGPS3mechanism

__author__ = 'Moe'
__copyright__ = 'Copyright 2016  Moe'
__license__ = 'MIT'
__version__ = '0.1'

agps_thread = AGPS3mechanism()  # Instantiate AGPS3 Mechanisms
agps_thread.stream_data(host='192.168.0.4')  # Stream from localhost as default (), or e.g., host='192.168.0.2'
agps_thread.run_thread(usnap=.2)  # Throttle the time to sleep after an empty lookup, default 0.2 two tenths of a second

while True:  # All data is available via instantiated thread data stream attribute.
    # line #140-ff of /usr/local/lib/python3.5/dist-packages/gps3/agps.py
    print('-----')
    print(agps_thread.data_stream.time)
    print('Lat:{}'.format(agps_thread.data_stream.lat))
    print('Lon:{}'.format(agps_thread.data_stream.lon))
    print('Speed:{}'.format(agps_thread.data_stream.speed))
    print('Course:{}'.format(agps_thread.data_stream.track))
    print('-----')
    sleep(30)
