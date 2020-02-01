#!/usr/bin/env python3

# Dumps the track to the database (PostgreSQL)

INPUT_FILE = "../data/GNSS_2020-01-25_23-54-55.txt"

if __name__ == '__main__':
    with open(INPUT_FILE, "r") as f:
        for line in f.readlines():
            sentence = line.strip()
            print(sentence)