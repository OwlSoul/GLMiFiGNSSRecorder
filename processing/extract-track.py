#!/usr/bin/env python3

FILENAME = "../data/GNSS_2020-01-25_23-54-55.txt"

OUTFILE = "../output/track.nmea"

outfile = open(OUTFILE, 'w')

with open(FILENAME, 'r') as f:
    for line in f.readlines():
        data = line.split(';')[2].strip()
        if data.startswith("$GPGGA") or data.startswith("$GPRMC"):
            print(data)
            outfile.write(data + '\n')

outfile.close()
f.close()