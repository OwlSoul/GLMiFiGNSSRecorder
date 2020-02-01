#!/bin/bash

# Force dumps the data from remote GNSS device

HOST="root@192.168.88.9"
PORT="22"

DATA_DIR="~/GNSSData"
INTERMEDIATE_DIR="$DATA_DIR/tmp"
TARGET_DIR="../data/"

echo -e ""
echo -e "Creating intermediate directory, moving the files"
ssh -p "$PORT" "$HOST" "mkdir -p $INTERMEDIATE_DIR && mv $DATA_DIR/*.txt $INTERMEDIATE_DIR"
echo -e "Copying GNSS tracks"
scp -r -P "$PORT" "$HOST:$INTERMEDIATE_DIR/"'*' "$TARGET_DIR"
echo -e "Removing the GNSS directory"
ssh -p "$PORT" "$HOST" "rm -rf $INTERMEDIATE_DIR"
echo -e "GNSS tracks transfer complete!"
echo -e ""
