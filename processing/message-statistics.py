#!/usr/bin/env python3

# Count messages by type
from collections import defaultdict

# Source filename
FILENAME = "../data/GNSS_2020-01-25_23-54-55.txt"

if __name__ == "__main__":
    message_counter = defaultdict(lambda: 0)

    with open(FILENAME, 'r') as f:
        for line in f.readlines():
            try:
                data = line.split(';')[2].strip()
                message_type = data.split(',')[0]
                message_counter[message_type]+=1
            except:
                pass
    
    for key, value in message_counter.items():
        print(key, value)

    f.close()