# GL MiFi GNSS Recorder

GL MiFi with EC25 4G receiver has an embedded GNSS recorder. This is a small lua script to record the data from GNSS and store it once per minute on SD card.

## Install

Just copy the `src` folder to any place you like. You can check `deploy.sh` for an example.

## Scripts

### Data collection scripts

| Script | Explaination |
| ----- | ----- |
| start-gps.sh | Sends the command to start GNSS recorder, data will be published in /dev/ttyUSB1 |
| stop-gps.sh  | Sends the command to stop GNSS recorder |
| read-gps.lua | Reads GNSS data from /dev/ttyUSB1, stores it once per minute |

### Data processing scripts
| Script | Explaination |
| ----- | ----- |
| extract-track | Simply extracts the NMEA data from track file (cuts out timestamps) |


## Launch

To read GPS data, just launch `read-gps.lua` script. Check `launch` folder for examples of how to launch this script in background on startup (via rc.local), and how to keep it alive (with 1 minute of data loss tolerance) using cron.

## Settings

Edit `read-gps.lua` to modify several settings.

| Variable | Explaination |
| ----- | ----- |
| GNSS_FILENAME | The file name of GNSS receiver, /dev/ttyUSB1 by default |
| OUTPUT_FOLDER | The folder where to store GNSS data, default is ~/GNSSData |
| POWER_ON_CYCLE_FILE | File with power-on state (read below) |
| STORE_FREQUENCY | How often to write GNSS data on disk, in seconds, default is 60 |

## Power-on-cycle feature

Since Gl MiFi defice does not have an internal clock, it relies on NTP for obtaining the time data. While you can definitely obtain data vis GNSS as well, this script still utilizes "power-on-cycle" feature support. Each boot, the POWER_ON_CYCLE_FILE (/root/Scripts/PowerOnCycle/data/cycle) is increased by one by a separate script, which is not a part of this repository. GNSS reader reads this value and stores together with GNSS data.

In case POWER_ON_CYCLE_FILE is missing, this mechanics is not used.

## Store data format

Data is stored as a text file in the OUTPUT_FOLDER location (default is `~/GNSSData`), files are named like this: `GNSS_14_2020-01-25_17-03-00.txt`, where 
14 is the power-on-cycle number, and 2020-01-25_17-03-00 is the time when track started recording.

Each line terminates with `\n` character. Line structure is the following:
```
<TIMESTAMP>;GNSS DATA <\n>
```

### Examples:

#### No GNSS fix
```
1579961537;$GPGSA,A,1,,,,,,,,,,,,,,,*1E
1579961537;$GPGGA,,,,,,0,,,,,,,,*66
1579961537;$GPRMC,,V,,,,,,,,,,N*53
1579961538;$GPVTG,,T,,M,,N,,K,N*2C
```

#### GPS Fix 
```
1579972104;$GPRMC,112102.00,A,5615.613094,N,03725.801183,E,0.0,179.8,260120,9.0,E,A*33
1579972104;$GPGSA,A,2,05,07,08,13,15,27,28,30,,,,,1.2,0.9,0.8*31
1579972105;$GPGSV,3,1,11,05,24,237,31,07,41,091,39,08,27,052,32,13,52,289,31*73
1579972105;$GPGSV,3,2,11,15,23,305,28,27,09,022,27,28,52,187,36,30,76,102,29*74
1579972105;$GPGSV,3,3,11,11,06,088,,20,,,,21,01,327,*79
1579972105;$GPGGA,112103.00,5615.613099,N,03725.801191,E,1,08,0.9,227.2,M,15.0,M,,*6C
1579972105;$GPVTG,179.8,T,170.8,M,0.0,N,0.0,K,A*2A
```

## GL MiFi EC25 GNSS known published NMEA sentences

These are the sentences encoundered so far:

| Sentence | Notes |
|   -----  | ----- |
| GPRMC    | Minimum recommended data |
| GPGSA    | Overall satellite reception data |
| GPGGA    | Fix data |
| GPVTG    | Vector track and speed over ground |
| GPGSV    | Detailed satellite data |

## Useful links

- [NMEA to Track converter and visualizer](www.mygeodata.cloud)
- [GPRMC and GPGGA decoder with map](https://rl.se/gprmc)
- [NMEA Sentences explained](https://www.gpsinformation.org/dale/nmea.htm)

## Licence

This little project is distributed under MIT licence.
