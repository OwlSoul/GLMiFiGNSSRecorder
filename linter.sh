#!/bin/bash

# Linter for the current project, requires luacheck and shellcheck

echo -e "Checking lua files"
luacheck src/*.lua \
         --ignore 211/_.* \
         --ignore 212/_.* \
         --ignore 213/_.*

echo -e "\nChecking sh files"
shellcheck -a src/start-gps.sh

echo -e "\nChecking python files, PROCESSING:"
pylint processing/dump-track.py

echo -e "\nDone!"
