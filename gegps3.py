# coding=utf-8
# !/usr/bin/python
# Concept from these guys
# Jaroslaw Zachwieja <grok!warwick.ac.uk>
# TJ <linux!tjworld.net>
# from their work in gegpsd.py included in gpsd (http://catb.org/gpsd)
"""creates google earth kml file (/tmp/gps3_live.kml) for realtime (4 second) updates of gps coordinates"""
import time

import gps3

the_connection = gps3.GPSDSocket(host='sypy.ddns.net')  # The demo address
the_fix = gps3.Fix()
the_link = '/tmp/gps3_live.kml'  # AFAIK, 'Links' call href on time events or entry/exit  Multiple href may be possible.
the_file = '/tmp/gps3_static.kml'

live_link = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                   "<kml xmlns=\"http://www.opengis.net/kml/2.2\" xmlns:gx=\"http://www.google.com/kml/ext/2.2\" xmlns:kml=\"http://www.opengis.net/kml/2.2\" xmlns:atom=\"http://www.w3.org/2005/Atom\">\n"
                   "<NetworkLink>\n"
                   "    <name>GPS3 Live</name>\n"
                   "    <Link>\n"
                   "        <href>{0}</href>\n"
                   "        <refreshMode>onInterval</refreshMode>\n"
                   "    </Link>\n"
                   "</NetworkLink>\n"
                   "</kml>"
).format(the_file)  # inserts 'the file' into a refresh mode
f = open(the_link, 'w')
f.write(live_link)
f.close()

try:
    for new_data in the_connection:
        if new_data:
            the_fix.refresh(new_data)
        if not isinstance(the_fix.TPV['speed'], str):
            speed = the_fix.TPV['speed']
            latitude = the_fix.TPV['lat']
            longitude = the_fix.TPV['lon']
            altitude = the_fix.TPV['alt']
            heading = the_fix.TPV['track']

            static_file = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                               "<kml xmlns=\"http://earth.google.com/kml/2.0\">\n"
                               "    <Placemark>\n"
                               "        <name>{0:.2f}km/h {4:.0f}°</name>\n"
                               "        <description></description>\n"
                               "        <LookAt>\n"
                               "            <longitude>{1}</longitude>\n"
                               "            <latitude>{2}</latitude>\n"
                               "            <range>600</range>\n"
                               "            <tilt>10</tilt>\n"
                               "            <heading>0</heading>\n"
                               "        </LookAt>\n"
                               "        <Point>\n"
                               "            <coordinates>{1},{2},{3}</coordinates>\n"
                               "        </Point>\n"
                               "    </Placemark>\n"
                               "</kml>"
            ).format(speed, longitude, latitude, altitude, heading)  # Change heading from '0' to '{4}' for 'Course Up'

            f = open(the_file, 'w')
            f.write(static_file)
            f.close()

        else:
            pass
        time.sleep(1)  # default GE refresh rate is 4 seconds, therefore no refresh older than 1 second from itself.
except KeyboardInterrupt:
    the_connection.close()
    print("\nTerminated by user\nGood Bye.\n")
#End
