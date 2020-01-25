# GL MiFi GNSS Recorder

GL MiFi with EC25 4G receiver has an embedded GNSS recorder. This is a small lua script to record the data from GNSS and store it once per minute on SD card.

## Install

Just copy the `src` folder to any place you like. You can check `deploy.sh` for an example.

## Scripts

| Script | Explaination |
| ----- | ----- |
| start-gps.sh | Sends the command to start GNSS recorder, data will be published in /dev/ttyUSB1 |
| stop-gps.sh  | Sends the command to stop GNSS recorder |
| read-gps.lua | Reads GNSS data from /dev/ttyUSB1, stores it once per minute |

## Settings

Edit `read-gps.lua` to modify several settings.

| Variable | Explaination |
| ----- | ----- |
| GNSS_FILENAME | The file name of GNSS receiver, /dev/ttyUSB1 by default |
| OUTPUT_FOLDER | The folder where to store GNSS data |
| POWER_ON_CYCLE_FILE | File with power-on state (read below) |
| STORE_FREQUENCY | How often to write GNSS data on disk |

## Power-on-cycle feature

Since Gl MiFi defice does not have an internal clock, it relies on NTP for obtaining the time data. While you can definitely obtain data vis GNSS as well, this script still utilizes "power-on-cycle" feature support. Each boot, the POWER_ON_CYCLE_FILE (/root/Scripts/PowerOnCycle/data/cycle) is increased by one by a separate script, which is not a part of this repository. GNSS reader reads this value and stores together with GNSS data.

In case POWER_ON_CYCLE_FILE is missing, this mechanics is not used.

## Store data format

Data is stored as a text file, each line terminates with `\n` character. Line structure is the following:
```
<POWER_ON_CYCLE>;<TIMESTAMP>;GNSS DATA <\n>
```

Examples:

No GNSS fix
```
11;1579961537;$GPGSA,A,1,,,,,,,,,,,,,,,*1E
11;1579961537;$GPGGA,,,,,,0,,,,,,,,*66
11;1579961537;$GPRMC,,V,,,,,,,,,,N*53
11;1579961538;$GPVTG,,T,,M,,N,,K,N*2C
```

No Power-On-Cycle file found
```
-;1579961537;$GPGSA,A,1,,,,,,,,,,,,,,,*1E
-;1579961537;$GPGGA,,,,,,0,,,,,,,,*66
-;1579961537;$GPRMC,,V,,,,,,,,,,N*53
-;1579961538;$GPVTG,,T,,M,,N,,K,N*2C
```

## Licence

This little project is distributed under MIT licence.
