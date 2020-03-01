#!/usr/bin/lua

local os     = require("os")
local math   = require("math")
local signal = require("posix.signal")

-- -------------------------- CONFIGURATION -------------------------------- --

-- Filename to read GNSS data from
local GNSS_FILENAME         = "/dev/ttyUSB1"

-- Directory where to store recorded data
local OUTPUT_FOLDER         = "/root/GNSSData"

-- Power on cycle state location
local POWER_ON_CYCLE_FILE   = "/root/Scripts/PowerOnCycle/data/cycle"

-- Temporary GNSS file (in-memory) for data output
local TEMP_OUTFILE          = "/tmp/gnss"

-- How often to store data (in seconds)
local STORE_FREQUENCY       = 60

-- How big the difference between GPS and Local time can be, in seconds
local TIME_DIFFERENCE       = 1

-- How big the difference between GPS and Local time can be until the new track file is created
local TRACK_TIME_DIFFERENCE = 5 * 60

-- ----------------------------- VARIABLES --------------------------------- --

-- Output filename
local outputFilename

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

local function startsWith(str, start)
	return str:sub(1, #start) == start
end

local function splitStr(inputstr, sep)
	if sep == nil then
			sep = "%s"
	end
	local t={}
	inputstr = inputstr .. sep
	for w in inputstr:gmatch("(.-)" .. sep) do table.insert(t, w) end
	return t
end

local function executeShell(command)
    local handle = io.popen(command)
    local result = handle:read("*a")
    handle:close()

    return result
end

--- Convert time and date from NMEA to date-understandable format, and set time and date of the system
--  Also, if date differences are too high (big time burst), the GNSS file will be reset to a new one.
local function setTime(gpsTime, gpsDate)
	print("Current time:", gpsTime)
	print("Current date:", gpsDate)

	-- Check input date for validity
	if gpsTime == nil or gpsDate == nil then return end
	if string.match(gpsTime, "[0-9][0-9][0-9][0-9][0-9][0-9].[0-9]+") == nil then return end
	if string.match(gpsDate, "[0-9][0-9][0-9][0-9][0-9][0-9]") == nil then return end

	-- Get required time and date values
	local hours   = string.sub(gpsTime, 1, 2)
	local minutes = string.sub(gpsTime, 3, 4)
	local seconds = string.sub(gpsTime, 5, 6)
	local day     = string.sub(gpsDate, 1, 2)
	local month   = string.sub(gpsDate, 3, 4)
	local year    = "20" .. string.sub(gpsDate, 5, 6) -- This will stop working in year 21XX =)

	-- Command to set time on OpenWRT is like this one: date -u -s "2020-03-05 15:15:15"
	local currentDateISO = year .. "-" .. month .. "-" .. day .. " " .. hours .. ":" .. minutes .. ":" .. seconds
	print("ISO Date:", currentDateISO)
	local preTime = os.time(os.date("!*t"))
	local satTime = os.time({year  = tonumber(year),
	                         month = tonumber(month),
							 day   = tonumber(day),
							 hour  = tonumber(hours),
							 min   = tonumber(minutes),
							 sec   = tonumber(seconds)})
	print("preTime:", preTime)
	print("satTime:", satTime)
	local diff = math.abs(preTime - satTime)
	print("diff:", diff)

	-- Sync the time if difference is detected
	if diff > TIME_DIFFERENCE then
		print("Oh my, the time is incorrect. Fixing the time now.")
		print("Syncing time with GPS data")
		executeShell("date -u -s '" .. currentDateISO .. "'")
	end

	-- Start a new track file if difference was too big
	if diff > TRACK_TIME_DIFFERENCE then
		print("We'll start a new track right now, time difference was too big")
		outputFilename = OUTPUT_FOLDER .. "/" .. "GNSS_" .. tostring(powerOnCycle) .. "_" ..
						 os.date('%Y-%m-%d_%H-%M-%S') .. ".txt"
		print("New track filename is " .. outputFilename)
	end
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
outputFilename = OUTPUT_FOLDER .. "/" .. "GNSS_" .. tostring(powerOnCycle) .. "_" ..
                       os.date('%Y-%m-%d_%H-%M-%S') .. ".txt"

-- Set starting time
local startingTime = os.time()

-- Data buffer
local dataBuffer = {}

-- Current time and date obtained from GPS
local currentGpsTime
local currentGpsDate

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

-- Receiving response
print("Getting the response")
while isRunning do
	local response = gnssFile:read("*l")
	if response ~= "" and response ~= nil then
		-- Writing to data buffer
	    table.insert(dataBuffer, os.time() .. ";" .. response)
		print("[" .. os.date('%Y-%m-%d %H:%M:%S') .. "]: " .. response)
		-- Writing to a tempfile
		local tempfile, errMsg, errCode = io.open(TEMP_OUTFILE, "a")
			if tempfile == nil then
				print("Failed to open " .. outputFilename .. ", error: " ..
                      tostring(errCode) .. " " .. tostring(errMsg))
			else
				tempfile:write(response .. "\n")
				tempfile:close()
			end
		-- Getting the time from GPS
		if startsWith(response, "$GPRMC") then
			local timeData = splitStr(response, ",")
			currentGpsTime = timeData[2]
			currentGpsDate = timeData[10]
			setTime(currentGpsTime, currentGpsDate)
		end
	end

	-- Write received data to the file
    local currentTime = os.time()
	if math.abs(os.time() - startingTime) >= STORE_FREQUENCY then
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
			local tempfile
			tempfile, errorMsg, errorCode = io.open(TEMP_OUTFILE, "w")
			if tempfile == nil then
				print("Failed to open " .. outputFilename .. ", error: " ..
                tostring(errorCode) .. " " .. tostring(errorMsg))
			else
				tempfile:close()
			end
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
