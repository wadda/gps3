#### README #####

The recent addition is the 'threading adaptor'.  The simple and efficient Python2.7-3.5 client, is pre-packaged as a threaded client,

    from agps3threaded import AGPS3mechanism

You then engage the thread triumvirate.

    agps_thread = AGPS3mechanism()  # Instantiate the mechanism
    agps_thread.stream_data()  # Stream the data from host, port, devicepath
    agps_thread.run_thread()  #  Run it as a thread with throttle control for empty look ups.

Four lines of code that lets you connect, communicate and control most of what you expect a gpsd to do.

    while True:  # All data is available via instantiated thread data stream attribute.
                 # lines #140-ff of the client /usr/local/lib/python3.5/dist-packages/gps3/agps.py
        print('----------------')
        print(                   agps_thread.data_stream.time)
        print('Lat:{}   '.format(agps_thread.data_stream.lat))
        print('Lon:{}   '.format(agps_thread.data_stream.lon))
        print('Speed:{} '.format(agps_thread.data_stream.speed))
        print('Course:{}'.format(agps_thread.data_stream.track))
        print('----------------')
        sleep(60)  # Sleep, or do other things for as long as you like.

Without arguments between the brackets the threaded client defaults to `host='127.0.0.1'`, `port=2947`, `gpsd_protocol='json'`, and `usnap=0.2`, for a respectable default of 2/10th of a second micro nap after each empty socket lookup.

The rest of the project is in DESCRIPTION.rst, or documented in the files themselves.
