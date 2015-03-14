#!/usr/bin/python
# coding=utf-8
# Concept from Jaroslaw Zachwieja <grok!warwick.ac.uk> &  TJ <linux!tjworld.net>
# from their work in gegpsd.py included in gpsd project (http://catb.org/gpsd)
"""creates Google Earth kml file (/tmp/gps3_live.kml) for realtime (4 second GE default) updates of gps coordinates"""
__author__ = 'Moe'
__copyright__ = "Copyright 2014 Moe"
__license__ = "MIT"  # TODO: figure this out and finish requirements
__version__ = "0.1a"

import time
import gps3

the_connection = gps3.GPSDSocket()  # TODO: needs work for commandline host selection
the_fix = gps3.Fix()
the_link = '/tmp/gps3_live.kml'  # AFAIK, 'Links' call href on time events or entry/exit  Multiple href may be possible.
the_file = '/tmp/gps3_static.kml'
the_history = []

live_link = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
             "<kml xmlns=\"http://www.opengis.net/kml/2.2\" xmlns:gx=\"http://www.google.com/kml/ext/2.2\" xmlns:kml=\"http://www.opengis.net/kml/2.2\" xmlns:atom=\"http://www.w3.org/2005/Atom\">\n"
             "<NetworkLink>\n"
             "    <name>GPS3 Live</name>\n"
             "    <Link>\n"
             "        <href>{0}</href>\n"
             "        <refreshMode>onInterval</refreshMode>\n"
             "    </Link>\n"
             "</NetworkLink>\n"
             "</kml>").format(the_file)  # inserts 'the file' into a refresh mode default 4 second
f = open(the_link, 'w')
f.write(live_link)
f.close()

try:
    for new_data in the_connection:
        if new_data:
            the_fix.refresh(new_data)
        if not isinstance(the_fix.TPV['speed'], str):  # lat/lon might be a better determinate of when data is 'valid'
            speed = the_fix.TPV['speed']
            latitude = the_fix.TPV['lat']
            longitude = the_fix.TPV['lon']
            altitude = the_fix.TPV['alt']

            if isinstance(the_fix.TPV['track'], str):  # 'track' frequently is missing and returns as 'n/a'
                heading = the_fix.TPV['track']
            else:
                heading = round(the_fix.TPV['track'])  # and heading percision in hundreths is just clutter.

            the_history.append(longitude)
            the_history.append(latitude)
            the_history.append(altitude)
            hist_string = str(the_history).replace(' ', '')  # GE > 7.1.xxxx spits up on spaces in <coordinates>

            static_file = ("<?xml version = \"1.0\" encoding = \"UTF-8\"?>\n"
                           "<kml xmlns = \"http://www.opengis.net/kml/2.2\" xmlns:gx = \"http://www.google.com/kml/ext/2.2\" xmlns:kml = \"http://www.opengis.net/kml/2.2\" xmlns:atom = \"http://www.w3.org/2005/Atom\">\n"
                           "<Folder>\n"
                           "    <description> Frankie likes walking and stopping </description>\n"

                           "    <Placemark id = \"point\">\n"
                           "        <name>{0:.2f} m/s {4}°</name>\n"
                           "        <description>Current gps location\nAltitude: {3} Metres</description>\n"
                           "        <LookAt>\n"
                           "            <longitude>{1}</longitude>\n"
                           "            <latitude>{2}</latitude>\n"
                           "            <range>600</range>\n"
                           "            <tilt>0</tilt>\n"
                           "            <heading>0</heading>\n"
                           "        </LookAt>\n"
                           "        <Point>\n"
                           "            <coordinates>{1},{2},{3}</coordinates>\n"
                           "        </Point>\n"
                           "    </Placemark>\n"

                           "    <Placemark id = \"path\">\n"
                           "        <name>Pin Scratches</name>\n"
                           "        <description>GPS Trail of Tears</description>\n"
                           "        <LineString>\n"
                           "        <color>7f0000ff</color>\n"
                           "        <width>20</width>\n"
                           "			<tessellate>1</tessellate>\n"
                           "            <coordinates>{5}</coordinates>\n"
                           "        </LineString>\n"
                           "    </Placemark>\n"
                           "</Folder>\n"
                           "</kml>").format(speed, longitude, latitude, altitude, heading, hist_string.strip('[]'))

            f = open(the_file, 'w')
            f.write(static_file)
            f.close()

        else:
            pass
        time.sleep(1)  # default GE refresh rate is 4 seconds, therefore no refresh older than 1 second from itself.
except KeyboardInterrupt:
    the_connection.close()
    print("\nTerminated by user\nGood Bye.\n")
# End
