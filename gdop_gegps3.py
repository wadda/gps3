#!/usr/bin/python3
# coding=utf-8
# Concept from Jaroslaw Zachwieja <grok!warwick.ac.uk> &  TJ <linux!tjworld.net>
# from their work in gegpsd.py included in gpsd project (http://catb.org/gpsd)
# This is a time limited demo for the curious, or those without a gps.  If it
# doesn't work, you need to use the 'regular' gegps.py and use another gps device,
# as "host='wadda.ddns.net'" will not be up forever. 20141205 Psst, Line #17.
"""creates Google Earth kml file (/tmp/gps3_live.kml) for realtime (4 second GE default) updates of gps coordinates"""
__author__ = 'Moe'
__copyright__ = "Copyright 2014 Moe"
__license__ = "MIT"  # TODO: figure this out and finish requirements
__version__ = "0.1a"

import time
import gps3
from pyproj import Geod  # sudo pip3 install pyproj
geoid = Geod(ellps='WGS84')  # See pyproj documentation for other fun options
startpoint = ()
endpoint = ()


the_connection = gps3.GPSDSocket()  # A demo address TODO: needs work for commandline host selection
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

def make_circle(longitude, latitude, gdop):
    """Calculate bearings and distance between start and end.

    Arguments:
      start (tuple of float): latitude and longitude of starting position
      end (tuple of float): latitude and longitude of ending position
      units (str): the units to output distance (must be one of 'meters',
        'nautical' (miles), 'imperial' (miles) or 'metric' (km)). Defaults
        to 'meters'.

    Returns:
      float: True North bearing start -> end
      float: True North bearing end -> start
      float: distance start <-> end

    Raises:
      KeyError: if units isn't  'meters' or in CONVERSION
    fwd(lons, lats, az, dist, radians=False) method of pyproj.Geod instance
        forward transformation - Returns longitudes, latitudes and back
        azimuths of terminus points given longitudes (lons) and
        latitudes (lats) of initial points, plus forward azimuths (az)
        and distances (dist).

        Works with numpy and regular python array objects, python
        sequences and scalars.

        if radians=True, lons/lats and azimuths are radians instead of
        degrees. Distances are in meters.
    """
    circle = ''
    try:
        for theta in range(1, 361):
            lons, lats, bearing_fro = geoid.fwd(longitude, latitude, theta, gdop)
            points = lons, lats, 0
            circle.join(points)
            # print(circle[:-10])


    except Exception as error:  # try to be more specific here!
        print("Can't draw a circle because:", error)
        return None


    return circle



try:
    for new_data in the_connection:
        if new_data:
            the_fix.refresh(new_data)
        if not isinstance(the_fix.TPV['lat'], str):  # lat/lon might be a better determinate of when data is 'valid'
            speed = the_fix.TPV['speed']
            latitude = the_fix.TPV['lat']
            longitude = the_fix.TPV['lon']
            altitude = the_fix.TPV['alt']
            altitude = abs(altitude)  # absolute Kludge because sometimes altitude becomes submarine/subterrarian

            epx = the_fix.TPV['epx']
            if isinstance(the_fix.SKY['gdop'], str):  # 'track' frequently is missing and returns as 'n/a'
                epx = 20

            if isinstance(the_fix.TPV['track'], str):  # 'track' frequently is missing and returns as 'n/a'
                heading = the_fix.TPV['track']
            else:
                heading = round(the_fix.TPV['track'])  # and heading percision in hundreths is just clutter.

            the_history.append(longitude)
            the_history.append(latitude)
            the_history.append(altitude)
            hist_string = str(the_history).replace(' ', '')  # GE> 7.1.x spits up on spaces in <coordinates>

            circle = ""

            for theta in range(1, 391, 30):
                lons, lats, bearing_fro = geoid.fwd(longitude, latitude, theta, epx)
                #lons2, lats2, bearing_fro2 = geoid.fwd(longitude, latitude, theta+30, epx)
                points = '{},{},{} '.format(lons, lats, altitude)
                circle += points
                print(points)


            # make_circle(longitude, latitude, gdop)
            # if not circle:
            #     circle = longitude, latitude, 0

            static_file = ("<?xml version = \"1.0\" encoding = \"UTF-8\"?>\n"
                           "<kml xmlns = \"http://www.opengis.net/kml/2.2\" xmlns:gx = \"http://www.google.com/kml/ext/2.2\" xmlns:kml = \"http://www.opengis.net/kml/2.2\" xmlns:atom = \"http://www.w3.org/2005/Atom\">\n"
                           "<Folder>\n"
                           "    <description> Frankie likes walking and stopping </description>\n"  # http://stackoverflow.com/questions/5492939/how-to-draw-path-between-placemark

                           "    <Placemark id = \"point\">\n"
                           "        <name>Location of unit</name>\n"
                           "        <description>SOG: {0:.2f} m/s COG: {4}°\nAltitude: {3} Metres</description>\n"
                           "        <LookAt>\n"
                           "            <longitude>{1}</longitude>\n"
                           "            <latitude>{2}</latitude>\n"
                           "            <range>200</range>\n"
                           "            <tilt>0</tilt>\n"
                           "            <heading>0</heading>\n"
                           "        </LookAt>\n"
                           "        <Point>\n"
                           "            <altitudeMode>clampToGround</altitudeMode>\n"
                           "            <coordinates>{1},{2},{3}</coordinates>\n"
                           "        </Point>\n"
                           "    </Placemark>\n"


                           "    <Placemark id = \"trail\">\n"

                           # "    <Style id = \"trail\">\n"
                           "        <LineStyle>\n"
                           "            <color>640000ff</color>\n"  #full red
                           "            <width>4</width>\n"
                           "            <gx:labelVisibility>1</gx:labelVisibility>\n"
                           "        </LineStyle>\n"
                           # "    </Style>\n"

                           "        <name>Trail of Tears</name>\n"
                           "        <description>That 'fateful trip'</description>\n"
                           "        <LineString>\n"
                           "            <extrude>0</extrude>\n"
                           "            <tessellate>1</tessellate>\n"
                           "            <altitudeMode>clampToGround</altitudeMode>\n"
                           "            <coordinates>{5}</coordinates>\n"
                           "        </LineString>\n"
                           "    </Placemark>\n"



                           "    <Placemark id = \"angels\">\n"
                           "        <LookAt>\n"
                           "            <longitude>{1}</longitude>\n"
                           "            <latitude>{2}</latitude>\n"
                           "            <range>400</range>\n"
                           "            <tilt>70</tilt>\n"
                           "            <heading>0</heading>\n"
                           "        </LookAt>\n"
                           # "    <Style id = \"path\">\n"
                           "        <PolyStyle>\n"
                           "            <color>0FFFFFF</color>\n"
                           "            <colorMode>random</colorMode>\n"
                           "        </PolyStyle>\n"
                           "        <LineStyle>\n"
                           "            <color>6400FF14</color>\n"
                           "            <width>2</width>\n"
                           "            <gx:labelVisibility>1</gx:labelVisibility>\n"
                           "        </LineStyle>\n"
                           # "    </Style>\n"
                           "        <IconStyle>\n"
                           "            <color>ff00ff00</color>\n"
                           "            <colorMode>random</colorMode>\n"
                           "            <scale>0.5</scale>\n"
                           "        <Icon>\n"
                           "            <href>~/.googleearth/Cache/icons/kh.google.com_icons_city_capital_star.png</href>\n"
                           "        </Icon>"
                           "        </IconStyle>"
                           "        <Point>\n"
                           "            <altitudeMode>absolute</altitudeMode>\n"
                           "            <coordinates>{1},{2},{3}</coordinates>\n"
                           "        </Point>\n"

                           "        <name>3D Rendition</name>\n"
                           "        <description>A 3 Hour Cruise</description>\n"
                           "        <LineString>\n"
                           "            <extrude>1</extrude>\n"
                           "            <tessellate>1</tessellate>\n"
                           "            <altitudeMode>absolute</altitudeMode>\n"
                           "            <coordinates>{5}</coordinates>\n"
                           "        </LineString>\n"
                           "    </Placemark>\n"
                           "    <Placemark>\n"
                           "        <name>Horizontal Error</name>\n"
                           "        <visibility>1</visibility>\n"
                           "            <Style>\n"
                           "                <geomColor>ff00ffff</geomColor>"
                           "                <geomScale>4</geomScale>\n"
                           "            </Style>\n"
                           "        <LineString>\n"
                           "            <coordinates> {6} </coordinates>\n"
                          # "            <altitudeMode>absolute</altitudeMode>\n"
                           "        </LineString>\n"
                           "    </Placemark>\n"
                           "</Folder>\n"
                           "</kml>").format(speed, longitude, latitude, altitude, heading, hist_string.strip('[]'), circle)

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
