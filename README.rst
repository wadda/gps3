**gps3.py**

gps3.py is a Python 2.7-3.5 GPSD interface (http://www.catb.org/gpsd) in two classes.

1) 'GPSDSocket' creates a GPSD socket connection & request/retreive GPSD output.
    It defaults to host='127.0.0.1', port=2947, gpsd_protocol='json'
2) 'Fix' unpacks the streamed gpsd data into python dictionaries.

These dictionaries are literated from the JSON data packet sent from the GPSD.

Import           from gps3 import gps3
Instantiate      gps_connection = gps3.GPSDSocket()
                 gps_fix = gps3.Fix()
Iterate          for new_data in gps_connection:
                     if new_data:
                        gps_fix.refresh(new_data)
Use                     print('Altitude = ',gps_fix.TPV['alt'])
                        print('Latitude = ',gps_fix.TPV['lat'])

Consult Lines 152-ff for Attribute/Key possibilities.
or http://www.catb.org/gpsd/gpsd_json.html

Run human.py; python[X] human.py [arguments] for a human experience.

**/example/human.py**

human.py showcases gps3.py,

Toggle Lat/Lon form with '0', '1', '2', '3' for RAW, DDD, DMM, DMS

Toggle units with  '0', 'm', 'i', 'n', for 'raw', Metric, Imperial, Nautical

Quit with 'q' or '^c'

python[X] human.py --help for list of commandline options.

**/example/gegps3.py**

Is a trivial application that creates a 'live' kml file(s) for Google Earth.
Scant documentation is in the file.


**agps3.py**

agps3.py also is a Python 2.7-3.5 GPSD interface (http://www.catb.org/gpsd) and
defaults to host='127.0.0.1', port=2947, gpsd_protocol='json' in two classes.

1) 'GPSDSocket' creates a GPSD socket connection & request/retreive GPSD output.
2) 'Dot' unpacks the streamed gpsd data into object attribute values.

Import           from gps3 import agps3
Instantiate      gps_connection = agps3.GPSDSocket()
                 dot = agps3.Dot()
Iterate          for new_data in gps_connection:
                     if new_data:
                        dot.update(new_data)
Use                     print('Altitude = ', dot.alt)
                        print('Latitude = ', dot.lat)


Consult Lines 146-ff for Attribute-value possibilities.

**/example/ahuman.py**

ahuman.py showcases agps3.py,

Toggle Lat/Lon form with '0', '1', '2', '3' for RAW, DDD, DMM, DMS

Toggle units with  '0', 'm', 'i', 'n', for 'raw', Metric, Imperial, Nautical

Quit with 'q' or '^c'

python[X] ahuman.py --help for list of commandline options.

**/example/agegps3.py**

Is a trivial application that creates a 'live' kml file(s) for Google Earth.
Scant documentation is in the file.

