#!/bin/sh

# Start GPS on GL-MiFi
echo "AT+QGPS=0" > /dev/ttyUSB2
