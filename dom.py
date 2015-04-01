#!/usr/bin/env python
""" banana """ # <-- For scale

import os
import time
import gps3
from datetime import datetime

from xml.dom.minidom import getDOMImplementation, parse, parseString

import xml.etree.ElementTree as ET

__author__ = "moe"
__copyright__ = "Copyright 2015, Wadda Big Deal"
__license__ = "MIT"
__version__ = "0.1a"
__email__ = "waddagit@wadda.org"
__status__ = "Flammable"
__created__ = '2015/03/16'


the_connection = gps3.GPSDSocket(host="192.168.0.2")
the_fix = gps3.Fix()
the_log = '/tmp/gpx3.gpx'

creation = datetime.utcnow()
fmt = '%Y-%m-%d %H:%M:%S %Z%z'
genesis = creation.strftime(fmt)

if not os.path.isfile(the_log):
    header = ('<?xml version="1.0"?>\n'
              '<gpx version="1.1" creator="gps3.py and gpx3logger.py - http://github.com/wadda/gps3">\n'
              '<metadata>\n'
              '     <time>{}\n'
              '</metadata>\n'
              '</gpx>').format(genesis)
    log = open(the_log, 'w')
    log.write(header)
    log.close()

try:
    for new_data in the_connection:
        if new_data:
            the_fix.refresh(new_data)
            #if not isinstance(the_fix.TPV['lat'], str):  # lat used as determinate when data is 'valid'
            latitude = the_fix.TPV['lat']
            longitude = the_fix.TPV['lon']
            altitude = the_fix.TPV['alt']
            time = the_fix.TPV['time']
            mode = the_fix.TPV['mode']
            tag = the_fix.TPV['tag']

            sats = the_fix.satellites_used()
            hdop = the_fix.SKY['hdop']
            vdop = the_fix.SKY['vdop']
            pdop = the_fix.SKY['pdop']

            gpspoint = '<trkpt lat=12.3456789 lon=98.7654321</trkpt>'

            trkpt = ET.Element('trkpt')
            trkpt.append((ET.fromstring(gpspoint)))


                
except Exception as error:
    print('Danger-Danger', error)



##trackpoint = parseString(gpspoint)



##impl = getDOMImplementation()
##
##newdoc = impl.createDocument(None, header, None)
##top_element = newdoc.documentElement
##text = newdoc.createTextNode('Some textual content.')
##top_element.appendChild(text)







# if __name__ == '__main__':    # code to execute if called from command-line
#     pass    # do nothing, unless code is added to this template
            # this is either a simple example of how to use the module,
            # or when the module can meaningfully be called as a script.
