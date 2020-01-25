#!/bin/sh

# Start GPS on GL-MiFi
echo "AT+QGPS=1" > /dev/ttyUSB2
