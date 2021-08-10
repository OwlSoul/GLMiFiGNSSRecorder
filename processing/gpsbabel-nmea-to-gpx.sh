#!/bin/bash

# Use GPSBabel to convert raw NMEA data to gpx (can be understood by NextCloud)
# Will convert all NMEA files from input_dir
# $1 - input dire
# $2 - output file

INPUT_DIR="$1"

if [ "$INPUT_DIR" == "" ];then
	echo "No input file specified, aborting"
	exit 1
fi

OUTPUT_DIR="$2"
if [ "$OUTPUT_DIR" == "" ];then
        echo "No output file specified, aborting"
        exit 1
fi

echo -e "Mass converting NMEA tracks to GPX"

for fullfile in $INPUT_DIR/*; do
	echo "Converting: $fullfile"
	# Remove timestamps from the original file
	cat $fullfile | cut -d';' -f2 > tmp.nmea
	filename=$(basename -- "$fullfile")
	extension="${filename##*.}"
	filename="${filename%.*}"
	gpsbabel -i nmea -f "tmp.nmea" -o gpx,gpxver=1.1 -F "$OUTPUT_DIR/$filename.gpx"
done

rm tmp.nmea

echo "DONE"
