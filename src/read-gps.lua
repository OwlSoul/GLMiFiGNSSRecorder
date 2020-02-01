#!/usr/bin/lua

local os     = require("os")
local signal = require("posix.signal")

-- -------------------------- CONFIGURATION -------------------------------- --

-- Filename to read GNSS data from
local GNSS_FILENAME        = "/dev/ttyUSB1"

-- Directory where to store recorded data
local OUTPUT_FOLDER        = "/root/GNSSData"

-- Power on cycle state location
local POWER_ON_CYCLE_FILE  = "/root/Scripts/PowerOnCycle/data/cycle"

-- How often to store data (in seconds)
local STORE_FREQUENCY      = 60

-- ----------------------------- VARIABLES --------------------------------- --

-- Exit codes
local EXIT_CODE_FAILED_TO_OPEN_FILE = 1

-- Run flag
local isRunning = true

-- Power-on cycle by default
local powerOnCycle = "X"

-- ----------------------------- FUNCTIONS --------------------------------- --

--- Signal handler for SIGINT
--  @param _sig received signal
--  @param _frm frame
--  @return nothing
local function sigintHandler(_sig, _frm)
	print("SIGINT received!")
	isRunning = false
end

local function fileExists(name)
	local f=io.open(name,"r")
	if f~=nil then io.close(f) return true else return false end
end

-- ------------------------------- MAIN ------------------------------------ --

-- Disable io buffering
io. output():setvbuf("no")

-- Set SIGINT handler
signal.signal(signal.SIGINT, sigintHandler)

print("\nGPS Reader Started\n")

-- Getting power-on cycle, if possible
local powerOnCycleFile, eMessage, eCode = io.open(POWER_ON_CYCLE_FILE, "r")
if powerOnCycleFile ~= nil then
	powerOnCycle = powerOnCycleFile:read("*a")
	powerOnCycle = string.gsub(powerOnCycle, "n", "")
	print("Power on cycle: " .. powerOnCycle)
	powerOnCycleFile:close()
else
	print("Failed to read power-on cycle, Error: " .. eMessage .. ", Code: " .. tostring(eCode))
end

-- Setting output filename
local outputFilename = OUTPUT_FOLDER .. "/" .. "GNSS_" .. tostring(powerOnCycle) .. "_" ..
                       os.date('%Y-%m-%d_%H-%M-%S') .. ".txt"

-- Set starting time
local startingTime = os.time()

-- Data buffer
local dataBuffer = {}

-- Opening ttyUSB GNSS file
print("Accessing file : " .. GNSS_FILENAME)
local gnssFile, errorMessage, errorCode = io.open(GNSS_FILENAME, "r")
if gnssFile == nil then
	print("Failed to open" .. GNSS_FILENAME .. ", error: " ..
              tostring(errorCode) .. " " .. tostring(errorMessage))
	os.exit(EXIT_CODE_FAILED_TO_OPEN_FILE)
else
	print("Opened file    : " .. GNSS_FILENAME)
end

-- Writing data to port
--print("Sending command to the port")
--gnssFile:write("AT+QGPS=1","\n")

-- Receiving response
print("Getting the response")
while isRunning do
	local response = gnssFile:read("*l")
	if response ~= "" and response ~= nil then
	    table.insert(dataBuffer, os.time() .. ";" .. response)
	    print("[" .. os.date('%Y-%m-%d %H:%M:%S') .. "]: " .. response)
	end

	-- Write received data to the file
    local currentTime = os.time()
	if os.time() - startingTime >= STORE_FREQUENCY then
        startingTime = currentTime
		print("Storing GNSS data in the file " .. outputFilename .. " ...")
		-- Check if file exists
		if not fileExists(outputFilename) then
			-- Create new filename if file does not exist
			outputFilename = OUTPUT_FOLDER .. "/" .. "GNSS_" .. tostring(powerOnCycle) .. "_" ..
                       os.date('%Y-%m-%d_%H-%M-%S') .. ".txt"
		end
		local dataFile, errorMsg, errCode = io.open(outputFilename, "a")
			if dataFile == nil then
               print("Failed to open " .. outputFilename .. ", error: " ..
               tostring(errCode) .. " " .. tostring(errorMsg))
			else
               for _key, line in pairs(dataBuffer) do
	           dataFile:write(line .. "\n")
			end
			dataFile:close()
			dataBuffer = {}                           -- Clear data buffer
            print("Data stored successfully!")
        end
	end
end

-- Closing ttyUSB GNSS file
if gnssFile then
	print("Closing file   : " .. GNSS_FILENAME)
	-- This blocks until it gets another SIGINT.
	-- Let's try to get rid of it completely.
	-- UPD: The working with /dev/ttyUSB1 blocks no matter what.
	gnssFile:close()
	print("Closed file    : " .. GNSS_FILENAME)
end

print("\nGPS Reader Terminated\n")
