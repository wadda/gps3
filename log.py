# coding=utf-8
from xml.dom import minidom
from xml.dom.minidom import parseString
import os
from datetime import datetime, timezone, timedelta
import gps3

<?xml version="1.0" encoding="UTF-8" standalone="no" ?>

header = ('<gpx xmlns="http://www.topografix.com/GPX/1/1"\n'
'xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3"\n'
'xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" creator="Bob\'s Turnips and Carwash" version="1.1"\n'
'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
'xsi:schemaLocation="http://www.topografix.com/GPX/1/1 "\n'
'                   "http://www.topografix.com/GPX/1/1/gpx.xsd "\n'
'                   "http://www.garmin.com/xmlschemas/GpxExtensions/v3 "\n'
'                   "http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd "\n'
'                   "http://www.garmin.com/xmlschemas/TrackPointExtension/v1 "\n'
'                   "http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd">')


latitude
longitude

trkpt_attrib = '<key>value</key>'

trackpointdict = {'ele':altitude, 'time':utc, 'mode':mode,
                  'tag':nmeatag, 'sat':sats, 'hdop':hzdop,
                  'vdop':vrdop, 'pdop':podop }

def update_trkpt(key, value):
    if key.firstChild.nodeType != node.TEXT_NODE:
        raise Exception('node does not contain replaceable text')
    key.firstChild.replaceWholeText(str(value))

for key, value in trackpointdict.items():
    doc = minidom.parseString(trkpt_attrib)
    node = doc.getElementsByTagName(key)[0]
    update_trkpt(key,value)






try:
    the_connection = gps3.GPSDSocket(host="127.0.0.1")
    the_fix = gps3.Fix()
    for new_data in the_connection:
        if new_data:
            the_fix.refresh(new_data)
            # #            if not isinstance(the_fix.TPV['lat'], str):  # lat used as determinate when data is 'valid'
            latitude = "{}".format(the_fix.TPV['lat'])
            longitude = "{}".format(the_fix.TPV['lon'])
            altitude = "<ele>{}</ele>".format(the_fix.TPV['alt'])
            utc = '<time>{}</time>'.format(the_fix.TPV['time'])
            mode = "{}".format(the_fix.TPV['mode'])
            nmeatag = "{}".format(the_fix.TPV['tag'])

            sats = "{}".format(the_fix.satellites_used())
            hzdop = "{}".format(the_fix.SKY['hdop'])
            vrdop = "{}".format(the_fix.SKY['vdop'])
            podop = "{}".format(the_fix.SKY['pdop'])

            print(utc, latitude)

            trackpoint = gpx3.createElementNS(None, 'wpt')
            trackpoint.setAttribute('lat', latitude)
            trackpoint.setAttribute('lon', longitude)
            track.appendChild(trackpoint)
