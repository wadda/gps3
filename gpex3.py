#! /usr/bin/python3
# coding=utf-8
"""banana"""
import xml.dom.minidom
import gps3
import time
from datetime import datetime, timezone, timedelta
import os
import sys

gps_connection = gps3.GPSDSocket()
gps_fix = gps3.Fix()


the_log = '/tmp/gpx3.gpx'


def start_time():
    """time in the beginning"""
    timestart = str(datetime.utcnow().replace(tzinfo=(timezone(timedelta(0)))))
    return timestart

if os.path.isfile(the_log):
    doc = minidom.parse(the_log)  # opens the pre-existing
    # gpx_element = doc.firstChild
    # create_element(trk)
    # track = gpx3.createElementNS(None, 'trk')

else:
    doc = xml.dom.minidom.Document()
    gpx_element = doc.createElement("gpx")
    doc.appendChild(gpx_element)

trk_element = doc.createElement("trkseg")
trk_element.setAttribute("began", start_time())
gpx_element.appendChild(trk_element)
utc = alt = hdop = vdop = pdop = mode = sats = tag = 'n/a'
try:
    tpv_list = {'time': utc, 'ele': alt, 'tag': tag}
    sky_list = {'hdop': hdop, 'vdop': vdop, 'pdop': pdop}
    # misc_list = {'sat': sats, 'fix':mode}
    element = {}

    for new_data in gps_connection:
        if new_data:
            gps_fix.refresh(new_data)
        if not isinstance(gps_fix.TPV['lat'], str):
            trkpt_element = doc.createElement("trkpt")
            trk_element.appendChild(trkpt_element)
            trkpt_element.setAttribute('lat', str(gps_fix.TPV['lat']))
            trkpt_element.setAttribute('lon', str(gps_fix.TPV['lon']))

            # for latlon in ('lat', 'lon'):
            #     trkpt_element.setAttribute(latlon, str(gps_fix.TPV[latlon]))

            #tp_list[key] =
            for key in tpv_list:
                if key == 'ele':
                    element[key] = '{}'.format(gps_fix.TPV['alt'])  # because consistency with labels is a horrible.
                else:
                    element[key] = '{}'.format(gps_fix.TPV[key])
            for key in sky_list:
                element[key] = '{}'.format(gps_fix.SKY[key])
            # Misc.
            element['sat'] = '{}'.format(gps_fix.satellites_used()[1])

            # tp_list['ele'] = '{}'.format(gps_fix.TPV['alt'])
            # tp_list['hdop'] = '{}'.format(gps_fix.SKY['hdop'])
            # tp_list['vdop'] = '{}'.format(gps_fix.SKY['vdop'])
            # tp_list['pdop'] = '{}'.format(gps_fix.SKY['pdop'])
            # tp_list['fix'] = '{}'.format(("ZERO", "NO_FIX", "2D", "3D")[gps_fix.TPV['mode']])
            # tp_list['sat'] = '{0[1]}'.format(gps_fix.satellites_used())
            # tp_list['tag'] = '{}'.format(gps_fix.TPV['tag'])

            for key in element:
                trkpt_data = doc.createElement(key)
                trkpt_element.appendChild(trkpt_data)

                new_value = doc.createTextNode(element[key])
                trkpt_data.appendChild(new_value)

            print(doc.toprettyxml())
            time.sleep(1)

except KeyboardInterrupt:
    gps_connection.close()
    print("\nTerminated by user\nGood Bye.\n")
