# coding=utf-8
"""gpx logger"""
from xml.dom import minidom
import os
from datetime import datetime, timezone, timedelta
import sys

import gps3

the_log = '/tmp/gpx3.gpx'

trk = None
utc = alt = hdop = vdop = pdop = mode = sats = nmeatag = 'n/a'
# trackpoint_string = '<{0}>value</{0}>'.format(key)

# trackpointdict = {'time', 'ele', 'hdop', 'vdop', 'pdop', 'mode', 'sat', 'tag', }

# gpx3 = minidom.parse(the_log)


def main():
    """pen and read"""
    trackpoint_list = ['time', 'ele', 'hdop', 'vdop', 'pdop', 'mode', 'sat', 'tag']
    try:
        gpx3 = minidom.parse(the_log)  # opens the pre-existing
        root = gpx3.firstChild
        # create_element(trk)
        track = gpx3.createElementNS(None, 'trk')
        track.setAttribute('began', create_time())
        root.appendChild(track)
        for key in trackpoint_list:
            keystring = '"{}"'.format(key)
            gpx3.createElement(keystring)
            trackpoint_data(gpx3, track)
            trackpoint.firstChild.replaceWholeText()


    except FileNotFoundError:
        create_file()
        main()  # What could possibly go wrong?


def create_time():
    """time in the beginning"""
    timestart = str(datetime.utcnow().replace(tzinfo=(timezone(timedelta(0)))))
    return timestart


def create_file():
    """created file if one does not exist"""
    if not os.path.isfile(the_log):
        root = minidom.parseString(HEADER)
        log_write = open(the_log, "w")
        root.writexml(log_write)
        log_write.close()
    return


HEADER = ('<gpx xmlns="http://www.topografix.com/GPX/1/1" '
          'xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" '
          'xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" '
          'creator="gpx3logger.py" version="0.1" '
          'xmlns:xsi="http://www.w3.org/2001/XMLSchema-" xsi:schemaLocation="http://www.topografix.com/GPX/1/1\n '
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
          '         </metadata>\n'
          '</gpx>').format(create_time())


def trackpoint_data(gpx3, track):
    """get new data
    :param track:
    :param gpx3:
    """
    trackpoint_list = ['time', 'ele', 'hdop', 'vdop', 'pdop', 'mode', 'sat', 'tag']
    try:
        the_connection = gps3.GPSDSocket(host="127.0.0.1")
        the_fix = gps3.Fix()
        for new_data in the_connection:
            if new_data:
                the_fix.refresh(new_data)

                trackpoint = gpx3.createElementNS(None, 'trkpt')
                trackpoint.setAttribute('lat', the_fix.TPV['lat'])
                trackpoint.setAttribute('lon', the_fix.TPV['lon'])
                track.appendChild(trackpoint)
                print(the_fix.TPV['lat'])
                for key in trackpoint_list:
                    keystring = '"{}"'.format(key)
                    gpx3.createElement(keystring)  # I still don't know what this does.
                    print(keystring)

                    nodestring = '<{0}>value</{0}>'.format(key)  #, value=the_fix.TPV[key]
                    print(nodestring)

                    doc = minidom.parseString(nodestring)  # You tell me the difference between node/element

                    node = doc.getElementsByTagName(keystring)
                    trackpoint.firstChild.replaceWholeText(the_fix.TPV[key])

                                        # trackpoint.appendChild(node)
                close(gpx3)

    except Exception as error:
        print('Danger-Danger', error)


def close(gpx3):
    """closed"""
    log_write = open(the_log, "w")
    gpx3.writexml(log_write)
    log_write.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        close(the_log)
        print("Keyboard interrupt received\nTerminated by user\nGood Bye.\n")
        sys.exit(1)

trackpoint = ('<trkpt lat={lat} lon={lon}>\n'
              '    <ele>{alt}</ele>\n'
              '    <time>{time}</time>\n'
              '    <hdop>{hdop}</hdop>\n'
              '    <vdop>{vdop}</vdop>\n'
              '</trkpt>'





)
