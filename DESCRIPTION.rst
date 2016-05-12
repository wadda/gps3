# coding=utf-8**Installation**

``[sudo [-H]] pip[2|3] install gps3``

For example, ``sudo -H pip3 install gps3`` for your default P3 installation.
``sudo pip2 install gps3`` for Python 2.7.

**gps3.py** will install at ``/usr/local/lib/python[3.5]/dist-packages/gps3/gps3.py``

gps3.py is a Python 2.7-3.5 GPSD interface (http://www.catb.org/gpsd) and
defaults to host='127.0.0.1', port=2947, gpsd_protocol='json' in two classes.

1) **GPSDSocket** creates a GPSD socket connection & request/retrieve GPSD output.

2) **Fix** unpacks the streamed gpsd data into python dictionaries.

These dictionaries are literated from the JSON data packet sent from the GPSD.

.. code-block:: python
    from gps3 import gps3
    gps_socket = gps3.GPSDSocket()
    gps_fix = gps3.Fix()
    gps_socket.connect()
    gps_socket.watch()
    for new_data in gps_socket:
        if new_data:
            gps_fix.refresh(new_data)
            print('Altitude = ',gps_fix.TPV['alt'])
            print('Latitude = ',gps_fix.TPV['lat'])

Consult Lines 147-ff for Attribute/Key possibilities.
or http://www.catb.org/gpsd/gpsd_json.html

**agps3.py** is installed at ``/usr/local/lib/python[3.5]/dist-packages/gps3/agps3.py``

It is functionally similar to gps.py, but literates object attributes rather than Python dictionaries.

agps3.py is also a Python 2.7-3.5 GPSD interface (http://www.catb.org/gpsd) and
defaults to host='127.0.0.1', port=2947, gpsd_protocol='json' in two classes.

1) **GPSDSocket** creates a GPSD socket connection & request/retrieve GPSD output.
2) **Dot** unpacks the streamed gpsd data into object attribute values.

.. code-block:: python
   :linenos:
    from gps3 import agps3
    gps_socket = agps3.GPSDSocket()
    dot = agps3.Dot()
    gps_socket.connect()
    gps_socket.watch()
    for new_data in gps_socket:
        if new_data:
            dot.unpack(new_data)
            print('Altitude = ', dot.alt)
            print('Latitude = ', dot.lat)


Consult Lines 140-ff for Attribute-value possibilities.

For a human experience, both versions have trivial showcase scripts, located at

``/usr/local/share/gps3/examples/``

**human.py** showcases gps3.py, **ahuman.py** showcases agps3.py

``python[X] /usr/local/share/gps3/examples/[a]human.py [-host] [-port]`` or ``--help``   for list of commandline options.

Toggle Lat/Lon form with '**0**', '**1**', '**2**', '**3**' for RAW, DDD, DMM, DMS

Toggle units with  '**0**', '**m**', '**i**', '**n**', for 'raw', Metric, Imperial, Nautical

Toggle between JSON and NMEA outputs with '**j**' and '**a**' respectively.

Quit with '**q**' or '**^c**'


Likewise, both versions have trivial applications [**a**] **gegps3.py** that creates a 'live' kml file(s) for Google Earth.

``python[X] /usr/local/share/gps3/examples/[a]gegps3.py`` (defaults)

Scant documentation is in the respective file.

**Un-installation**

``[sudo -H] pip[2|3] uninstall gps3``

For example, ``sudo -H pip3 uninstall gps3`` for P3 installation.
Likewise, for Python 2.7 ``sudo pip2 uninstall gps3``

**Problems with installation**

Un-install using the method above and ``y`` to delete the old files, then

``sudo -H pip[2|3] install --ignore-installed gps3``

This will bypass the cached version and fetch the most recent *typo-free* version.

Comments are always appreciated.






