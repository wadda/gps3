# coding=utf-8
from xml.dom import minidom
import os
from datetime import datetime, timezone, timedelta

import gps3


the_connection = gps3.GPSDSocket(host="127.0.0.1")
the_fix = gps3.Fix()
the_log = '/tmp/gpx3.gpx'
key = None
trk = None
utc = altitude = hzdop = vrdop = podop = mode = sats = nmeatag = 'n/a'

def genesis():
    """time in the begininng"""
    timestart = str(datetime.utcnow().replace(tzinfo=(timezone(timedelta(0)))))
    return timestart


header = ('<gpx xmlns="http://www.topografix.com/GPX/1/1" \n'
          'xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" \n'
          'xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" \n'
          'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \n'
          'xsi:schemaLocation="http://www.topografix.com/GPX/1/1\n'
          'http://www.topografix.com/GPX/1/1/gpx.xsd \n'
          'http://www.garmin.com/xmlschemas/GpxExtensions/v3 \n'
          'http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd \n'
          'http://www.garmin.com/xmlschemas/TrackPointExtension/v1 \n'
          'http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd">\n'
          '     <metadata>\n'
          '         <link href="https://github.com/wadda/gps3">\n'
          '         <text>"gps3.py and gpx3logger.py"</text>\n'
          '         </link>\n'
          '         <time>{}</time>\n'
          '     </metadata>\n'
          '</gpx>').format(genesis())

if not os.path.isfile(the_log):
    root = minidom.parseString(header)
    log_write = open(the_log, "w")
    root.writexml(log_write)
    log_write.close()

def create_element(key):
    keystring = '"{}"'.format(key)
    key = gpx3.createElement(keystring)
    return key


def update_trkpt(node, update):
    if node.firstChild.nodeType != node.TEXT_NODE:
        raise Exception('node does not contain replaceable text')
    node.firstChild.replaceWholeText(update)
    return

trackpoint_string = '<{0}>value</{0}>'.format(key)

trackpointdict = {'time': utc,
                  'ele': altitude,
                  'hdop': hzdop,
                  'vdop': vrdop,
                  'pdop': podop,
                  'mode': mode,
                  'sat':sats,
                  'tag': nmeatag,
}

gpx3 = minidom.parse(the_log)
root = gpx3.firstChild
create_element(trk)
track = gpx3.createElementNS(None, 'trk')
trk.setAttribute('began', genesis())
root.appendChild(track)

for key, value in trackpointdict.items():
    keystring = '"{}"'.format(key)
    doc = minidom.parseString(trackpoint_string)
    node = doc.getElementsByTagName(keystring)[0]
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
            altitude = "{}".format(the_fix.TPV['alt'])
            utc = the_fix.TPV['time']
            Qmode = "{}".format(the_fix.TPV['mode'])
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

            for key in trackpointdict.items():
                trkpt_attribute[key] = '<key>value</key>'
                element[key] = minidom.parseString(trkpt_attribute[key])

            for key, value in trackpointdict.items():
                node = element.getElementsByTagName(key)[0]
                update_trkpt(key,value)
                trackpoint.appendChild(node)



# #            for key in ['ele', 'utc', 'mode', 'tag', 'sat', 'hdop', 'vdop', 'pdop']:
# #                key = gpx3.createElementNS(None, '{}'.format(key))
# #                key.setAttribute('{}'.format(key), key)
# #                trackpoint.appendChild(key)
            log_write = open(the_log, "w")
            gpx3.writexml(log_write)
            log_write.close()

except Exception as error:
    print('Danger-Danger', error)

log_write = open(the_log, "w")
gpx3.writexml(log_write)
log_write.close()

