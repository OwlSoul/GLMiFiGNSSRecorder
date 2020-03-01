#!/usr/bin/env python3

# Simple data processing, extraction of GPGGA and GPRMC entries

# Source filename
FILENAME = "../data/GNSS_34_2020-02-23_16-20-44.txt"

# Output filename
OUTFILE = "../output/track.nmea"

if __name__ == "__main__":
    outfile = open(OUTFILE, 'w')

    with open(FILENAME, 'r') as f:
        for line in f.readlines():
            try:
                data = line.split(';')[1].strip()
                if data.startswith("$GPGGA") or data.startswith("$GPRMC"):
                    print(data)
                    outfile.write(data + '\n')
            except:
                pass

    outfile.close()
    f.close()
