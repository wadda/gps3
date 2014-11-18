# coding=utf-8
# !/usr/bin/python
# Concept from these guys
# Copyright (C) 2007 by Jaroslaw Zachwieja <grok!warwick.ac.uk>
# Copyright (C) 2008 by TJ <linux!tjworld.net>
# in gegpsd.py as part of gpsd
"""creates google earth kml file (/tmp/gps3_live.kml) for realtime (4 second) updates of gps coordinates"""
import time

import gps3

the_connection = gps3.GPSDSocket(host='sypy.ddns.net')
the_fix = gps3.Fix()
the_link = '/tmp/gps3_live.kml'
the_file = '/tmp/gps3_static.kml'

output_repeater = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<NetworkLink>
    <name>GPS3 Live</name>
    <Link>
        <href>{0}</href>
        <refreshMode>onInterval</refreshMode>
    </Link>
</NetworkLink>
</kml>""".format(the_file)
f = open(the_link, 'w')
f.write(output_repeater)
f.close()

while 1:
    for new_data in the_connection:
        if new_data:
            the_fix.refresh(new_data)
        if not isinstance(the_fix.TPV['speed'], str):
            speed = the_fix.TPV['speed']
            latitude = the_fix.TPV['lat']
            longitude = the_fix.TPV['lon']
            altitude = the_fix.TPV['alt']

            output_instance = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.0">
    <Placemark>
        <name>{0} km/h</name>
        <description></description>
        <LookAt>
            <longitude>{1}</longitude>
            <latitude>{2}</latitude>
            <range>600</range>
            <tilt>30</tilt>
            <heading>0</heading>
        </LookAt>
        <Point>
            <coordinates>{1},{2},{3}</coordinates>
        </Point>
    </Placemark>
    </kml>""".format(speed, longitude, latitude, altitude)

            f = open(the_file, 'w')
            f.write(output_instance)
            f.close()

        else:
            pass
        time.sleep(1)

