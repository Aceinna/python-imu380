# python-imu380
Python driver for Aceinna 380 Series Inertial Products.  Includes local and cloud file logging, and WebSocket server

### pip install:
pyserial  
tornado  
azure-storage-blob

See demo.py for example usage

### imu380.py

This is core driver for the DMU38x family of IMU's.  It can do the following functions:

- automatically discover a DMU38x connected to serial port  TODO: make faster and more reliable
- log data to local file or azure cloud TODO: add system for using user keys
- parse various ouput packets:  TODO: complete and test all packet types, as well as custom user packet from OpenIMU
- read/write and get/set EEPROM fields
- upgrade firmware of device
- run as a thread in websocket server see below

### server_ui.py

This is simple UI to control server
