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
1579974429;$GPGSA,A,2,05,07,11,13,15,20,28,30,,,,,1.0,0.7,0.7*3D
1579974430;$GPGSV,3,1,10,05,10,227,22,07,25,098,27,08,19,037,16,11,15,074,28*73
1579974430;$GPGSV,3,2,10,13,64,264,21,15,38,296,32,17,11,157,20,20,08,336,32*73
1579974430;$GPGSV,3,3,10,28,70,172,24,30,59,101,28*72
1579974430;$GPGGA,115948.00,5615.617024,N,03725.802986,E,1,09,0.7,232.9,M,15.0,M,,*63
1579974430;$GPVTG,21.4,T,12.4,M,0.0,N,0.0,K,A*23
```

## Useful links

- [NMEA to Track converter and visualizer](www.mygeodata.cloud)
- [GPRMC and GPGGA decoder with map](https://rl.se/gprmc)

## Licence

This little project is distributed under MIT licence.
