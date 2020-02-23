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
    values = sentence.split('*')[0].split(',')
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
    values = sentence.split('*')[0].split(',')
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

def read_gpvtg(sentence, timestamp, do_print=False):
    """ Read and parse GPVTG message"""
    values = sentence.split('*')[0].split(',')
    result = {}

    # Linux timestamp
    try:
        result['linux_stamp'] = int(timestamp)
    except:
        result['linux_stamp'] = 0
    result['linux_date'] = datetime.fromtimestamp(result['linux_stamp'], tz=pytz.UTC)

    # True Track
    try:
        result['truetrack'] = float(values[1])
    except:
        result['truetrack'] = None

    # Magnetic Track
    try:
        result['magnetictrack'] = float(values[3])
    except:
        result['magnetictrack'] = None

    # Groundspeed, knots
    try:
        result['groundspeed_knots'] = float(values[5])
    except:
        result['groundspeed_knots'] = None
    
    # Groundspeed, km/h
    try:
        result['groundspeed_kmh'] = float(values[7])
    except:
        result['groundspeed_kmh'] = None

    if do_print:
        if result['truetrack'] is None and \
           result['magnetictrack'] is None and \
           result['groundspeed_knots'] is None and \
           result['groundspeed_kmh'] is None:
            pass
        else:
            print("Linux timestamp   :", result['linux_stamp'])
            print("Linux datetime    :", result['linux_date'])
            print("  True Track      :", result['truetrack'])
            print("  Magnetic Track  :", result['magnetictrack'])
            print("  Ground spd, knot:", result['groundspeed_knots'])
            print("  Ground spd, km/h:", result['groundspeed_kmh'])
            print("")
    
    return result

def read_gpgsa(sentence, timestamp, do_print=False):
    """ Read and parse GPGSA message"""
    values = sentence.split('*')[0].split(',')
    result = {}

    # Linux timestamp
    try:
        result['linux_stamp'] = int(timestamp)
    except:
        result['linux_stamp'] = 0
    result['linux_date'] = datetime.fromtimestamp(result['linux_stamp'], tz=pytz.UTC)

    # Fix selection
    try:
        result['fix_selection'] = str(values[1])
    except:
        result['fix_selection'] = None

    # Fix type
    try:
        result['fix_type'] = int(values[2])
    except:
        result['fix_type'] = None

    # Fix satellites
    try:
        result['fix_satellites'] = []
        for sat in range(3, 3+12):
            try:
                sat_no = int(values[sat])
                result['fix_satellites'].append(sat_no)
            except Exception as e:
                pass
    except:
        result['fix_satellites'] = None

    # Satellite counts
    if result['fix_satellites'] is None:
        result['fix_sat_count'] = 0
    else:
        result['fix_sat_count'] = len(result['fix_satellites'])

    # PDOP
    try:
        result['pdop'] = float(values[15])
    except:
        result['pdop'] = None

    # HDOP
    try:
        result['hdop'] = float(values[16])
    except:
        result['hdop'] = None

    # VDOP
    try:
        result['vdop'] = float(values[17])
    except:
        result['vdop'] = None
    if do_print:
        print("Linux timestamp   :", result['linux_stamp'])
        print("Linux datetime    :", result['linux_date'])
        print("  Fix selection   :", result['fix_selection'])
        print("  Fix type        :", result['fix_type'])
        print("  Satellites count:", result['fix_sat_count'])
        print("  Fix satellites  :", end=" ")
        if result['fix_satellites'] == None:
            print("NONE")
        elif len(result['fix_satellites']) == 0:
            print("EMPTY")
        else:
            for sat in result['fix_satellites']:
                print(sat, end=" ")
            print()       
        print("  PDOP            :", result['pdop'])
        print("  HDOP            :", result['hdop'])
        print("  VDOP            :", result['vdop'])
        print()
    
    return result

def read_gpgsv(sentence, timestamp, do_print=False):
    """ Read and parse GPGSV message"""
    values = sentence.split('*')[0].split(',')
    result = {}

    # Linux timestamp
    try:
        result['linux_stamp'] = int(timestamp)
    except:
        result['linux_stamp'] = 0
    result['linux_date'] = datetime.fromtimestamp(result['linux_stamp'], tz=pytz.UTC)

    result['satellites'] = []
    for i in range(0, 4):
        try:
            satellite = {}
            try:
                satellite['prn'] = int(values[i*4 + 4])
            except:
                continue

            try:
                satellite['elevation'] = float(values[i*4 + 5]) 
            except:
                satellite['elevation'] = None

            try:
                satellite['azimuth'] = float(values[i*4 + 6])
            except:
                satellite['azimuth'] = None
                
            try:
                satellite['snr'] = float(values[i*4 + 7])
            except:
                satellite['snr'] = None

            result['satellites'].append(satellite)
        except Exception as e:
            print(e)

    if do_print:
        print("Linux timestamp   :", result['linux_stamp'])
        print("Linux datetime    :", result['linux_date'])
        for sat in result['satellites']:
            print("  PRN:", str(sat['prn']), \
                "Elevation:", str(sat['elevation']), \
                "Azimuth:", str(sat['azimuth']), \
                "SNR:", str(sat['snr']))
        print("")
        
    return result

if __name__ == '__main__':
    print("Processing track data...")
    totaldata = {}
    with open(INPUT_FILE, "r") as f:
        for line in f.readlines():
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
                if sentence[1].startswith("$GPVTG"):
                    gpvtg = read_gpvtg(sentence[1], sentence[0], do_print=False)
                    totaldata[sentence[0]]['gpvtg'].append(gpvtg)
                if sentence[1].startswith("$GPGSA"):
                    gpgsa = read_gpgsa(sentence[1], sentence[0], do_print=False)
                    totaldata[sentence[0]]['gpgsa'].append(gpgsa)
                if sentence[1].startswith("$GPGSV"):
                    gpgsv = read_gpgsv(sentence[1], sentence[0], do_print=False)
                    totaldata[sentence[0]]['gpgsv'].append(gpgsv)
            except Exception as e:
                pass
    
    print()
    print("TRACK ANALYSIS:")

    # Calculate valid datapoints
    valid_points = 0
    for key, entry in totaldata.items():
        if (not entry['gpgga'] is None):
            for record in entry['gpgga']:
                if (not record['fix'] is None) and record['fix'] == 1:
                    valid_points += 1

    # Fix percentage
    fix_percentage = {0: 0, 1: 0, 2: 0, 3: 0}
    for key, entry in totaldata.items():
        if (not entry['gpgsa'] is None):
            for record in entry['gpgsa']:
                if (not record['fix_type'] is None):
                    if record['fix_type'] in fix_percentage:
                        fix_percentage[record['fix_type']] += 1


    # Print analytics
    print(" - Track entries    (timestamped)   : " + str(len(totaldata)))
    print(" - Valid datapoints (with GNSS fix) : " + str(valid_points))
    print("              NO FIX points         : " + str(fix_percentage[1]))
    print("              2D FIX points         : " + str(fix_percentage[2]))
    print("              3D FIX points         : " + str(fix_percentage[3]))
    
    for key, entry in totaldata.items():
        print(key)
    #    print("GPRMC", entry['gprmc'])
    #    print("GPGGA", entry['gpgga'])
    #    print("GPVTG", entry['gpvtg'])
    #    print("GPGSA", entry['gpgsa'])
        print("GPGSV", entry['gpgsv'])
        print()

    print()
    print("Track dumped successfully!")