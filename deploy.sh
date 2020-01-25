#!/bin/bash

# Deploys the project to target device

MIFI_HOST="root@192.168.88.9"
MIFI_PORT=22
TARGET_FOLDER="~/Scripts/GNSSRecorder"

echo -e "Deploying the solution to target device $MIFI_HOST:$MIFI_PORT"
ssh -p $MIFI_PORT $MIFI_HOST "mkdir -p $TARGET_FOLDER > /dev/null 2> /dev/null"
scp -P $MIFI_PORT -r "src" "$MIFI_HOST:$TARGET_FOLDER/"

echo -e "Done!"
