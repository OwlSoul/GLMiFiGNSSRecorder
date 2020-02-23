#!/usr/bin/env python3

# Dumps the track to the database (PostgreSQL)

from datetime import datetime
import pytz
import math

INPUT_FILE = "../data/GNSS_28_2020-01-27_00-28-25.txt"

def nmea_to_degrees(data):
    DD = int(float(data)/100)
    SS = float(data) - DD * 100
    return DD + SS/60

def read_gprmc(sentence, timestamp, do_print=False):
    """ Read and parse GPRMC message"""
    values = sentence.split(',')
    result = {}

    # Linux timestamp
    try:
        result['linux_stamp'] = int(timestamp)
    except:
        result['linux_stamp'] = 0
    result['linux_date'] = datetime.fromtimestamp(result['linux_stamp'], tz=pytz.UTC)

    # Validity
    try:    
        result['validity'] = str(values[2])
    except:
        result['validity'] = None

    # Latitude
    try:
        result['latitude'] = float(values[3])
        result['latitude_deg'] = nmea_to_degrees(result['latitude']) if values[4]=='N' else -nmea_to_degrees(result['latitude'])
    except:
        result['latitude'] = None
        result['latitude_deg'] = None

    # Longitude
    try:
        result['longitude'] = float(values[5])
        result['longitude_deg']= nmea_to_degrees(result['longitude']) if values[6]=='E' else nmea_to_degrees(result['longitude']) 
    except:
        result['longitude'] = None
        result['longitude_deg'] = None

    # Speed in Knots
    try:
        result['speed_knots'] = float(values[7])
    except:
        result['speed_knots'] = None
    
    # True course
    try:
        result['true_course'] = float(values[8])
    except:
        result['true_course'] = None

    # Time stamp
    try:
        result['timestamp'] = str(values[1])
    except:
        result['timestamp'] = None

    # Date stamp
    try:
        result['datestamp'] = str(values[9])
    except:
        result['datestamp'] = None

    # Magnetic variation
    try:
        result['variation'] = float(values[10]) if values[11] == 'E' else -float(values[10])
    except:
        result['variation'] = None

    # Calculate actual timestamp
    try:
        ts_day = int(result['datestamp'][0:2])
        ts_month = int(result['datestamp'][2:4])
        ts_year = 2000 + int(result['datestamp'][4:6])

        ts_hours = int(result['timestamp'][0:2])
        ts_mins = int(result['timestamp'][2:4])
        ts_sec = int(result['timestamp'][4:6])
        ts_micro = int(result['timestamp'][7:])

        result['actual_date'] = datetime(year=ts_year, month=ts_month, day=ts_day,
                                         hour=ts_hours,minute=ts_mins,second=ts_sec,microsecond=ts_micro,
                                         tzinfo=pytz.UTC)
    except Exception as e:
        result['actual_date'] = None
    result['actual_timestamp'] = datetime.timestamp(result['actual_date'])   
    
    if do_print and result['validity'] == 'A':
        print("Linux timestamp :", result['linux_stamp'])
        print("Linux datetime  :", result['linux_date'])
        print("Actual timestamp:", result['actual_timestamp'])
        print("Actual date-time:", result['actual_date'])
        print("  Validity      :", result['validity'])
        print("  ----------------------------")
        print("  Time stamp    :", result['timestamp'])
        print("  Date stamp    :", result['datestamp'])
        print("  ----------------------------")
        print("  Latitude      :", result['latitude'], "(" + str(result['latitude_deg']) + ")")
        print("  Longitude     :", result['longitude'], "("+ str(result['longitude_deg']) + ")")
        print("  Variation     :", result['variation'])
        print("  Speed (knots) :", result['speed_knots'])
        print("  True course   :", result['true_course'])
        print("")

    return result

def read_gpgga(sentence, timestamp, do_print=False):
    """ Read and parse GPGGA message"""
    values = sentence.split(',')
    result = {}

    # Linux timestamp
    try:
        result['linux_stamp'] = int(timestamp)
    except:
        result['linux_stamp'] = 0
    result['linux_date'] = datetime.fromtimestamp(result['linux_stamp'], tz=pytz.UTC)

    #GNSS UTC Time
    try:
        result['utc_stamp'] = str(values[1])
    except:
        result['utc_stamp'] = 0

    # Fix
    try:
        result['fix'] = int(values[6])
    except:
        result['fix'] = 0

    # Latitude
    try:
        result['latitude'] = float(values[2])
        result['latitude_deg'] = nmea_to_degrees(result['latitude']) if values[3]=='N' else -nmea_to_degrees(result['latitude'])
    except:
        result['latitude'] = None
        result['latitude_deg'] = None

    # Longitude
    try:
        result['longitude'] = float(values[4])
        result['longitude_deg']= nmea_to_degrees(result['longitude']) if values[5]=='E' else nmea_to_degrees(result['longitude']) 
    except:
        result['longitude'] = None
        result['longitude_deg'] = None

    # Altitude
    try:
        result['altitude'] = float(values[9])
    except:
        result['altitude'] = None

    # Satellites
    try:
        result['satellites_in_use'] = int(values[7])
    except:
        result['satellites_in_use'] = None

    # HDOP
    try:
        result['hdop'] = float(values[8])
    except:
        result['hdop'] = None

    # Geoidal Separation
    try:
        result['geoidal_separation'] = float(values[11])
    except:
        result['geoidal_separation'] = None

    # Diff last update
    try:
        result['diff_last_update'] = float(values[13])
    except:
        result['diff_last_update'] = None

    # Diff last update
    try:
        if len(values) <= 15:
            result['diff_reference_station'] = None
        else:
            result['diff_reference_station'] = str(values[14])
    except:
        result['diff_reference_station'] = None

    if do_print and result['fix'] != 0:
        print("Linux timestamp   :", result['linux_stamp'])
        print("Linux datetime    :", result['linux_date'])
        print("UTC stamp         :", result['utc_stamp'])
        print("  Fix             :", result['fix'])
        print("  Used sats       :", result['satellites_in_use'])
        print("  ----------------------------")
        print("  Latitude        :", result['latitude'], "(" + str(result['latitude_deg']) + ")")
        print("  Longitude       :", result['longitude'], "("+ str(result['longitude_deg']) + ")")
        print("  HDOP            :", result['hdop'])
        print("  Altitude        :", result['altitude'])
        print("  Geoid separation:", result['geoidal_separation'])
        print("  Diff last update:", result['diff_last_update'])
        print("  Diff ref station:", result['diff_reference_station'])
        print("")
    
    return result

if __name__ == '__main__':
    totaldata = {}
    with open(INPUT_FILE, "r") as f:
        for line in f.readlines():s
            try:
                sentence = line.strip().split(';')
                if not sentence[0] in totaldata:
                        totaldata[sentence[0]] = {'gprmc' : [],
                                                  'gpgga' : [],
                                                  'gpgsa' : [],
                                                  'gpvtg' : [],
                                                  'gpgsv' : []
                                                 }
                if sentence[1].startswith("$GPRMC"):
                    gprmc = read_gprmc(sentence[1], sentence[0], do_print=False)
                    totaldata[sentence[0]]['gprmc'].append(gprmc)
                if sentence[1].startswith("$GPGGA"):
                    gpgga = read_gpgga(sentence[1], sentence[0], do_print=False)
                    totaldata[sentence[0]]['gpgga'].append(gpgga)
            except Exception as e:
                pass
    
    print("Track contains " + str(len(totaldata)) + " entries")
    for key, entry in totaldata.items():
        print(key, entry)
        print()

    print("Track dumped successfully!")