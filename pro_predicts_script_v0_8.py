## =========================================
## Sensitive information has been removed
## =========================================


# ================================
# VERSION 0.8
# ================================
# Updates since v0.7
# Script now checks if file have been modified in the directory and will read the new files
# Updated import libraries (for better readability)



## ==============
## DOCUMENTATION
## ==============
## All comments that will be kept in the final version of this code should have "##"
##
## Comments that begin with a single "#" should be temporary and the comment should
## 		be removed before certification of this file. Additionally, print statements
## 		are all temporary and should be deleted or deactivated if not in "test" mode.
##
## The purpose of this file is to read in selected PRO Predict txt files and publish the predicted values
##		to the ISP server at the appropriate timestamps in the txt files.
##
## Description of functions:
## 		main:						Create an ISP client, open a connection, and calls mainLoop() indefinitely.
##		mainLoop:					This is the true "main" function in this script. It determines when to
##										read the PRO Predict files and when to publish the appropriate telemetry to
##										the ISP server.
##		getVehicleTimestamps:		Calculates current and future vehicle timestamps. This is used to
##										collect & publish the correct amount of telemetry.
##		readFiles:					Reads in telemetry from each PRO Predict file. The script will only store
## 										telemetry that contain timestamps between current and future (predetermined)
##										timestamps.
##		parseTimestamp:				Converts vehicle timestamp (str) and returns total hours (float)
## 		fillFileModDateDict:		For each file in fileLst, store the file's modified date and directory
##										in the FileModDateDict dictionary
##		watchForChanges:			Compares original modified date with latest modified date for each file,
##										and then determines if the script should read the files again
##
## Description of main variables:
##   	publishToParamDict:       	A dictionary that uses the filename as the key and the function to call as the value.
##										The values are in a string format so that they may be evaluated later in the
##										program using eval()
##		fileLst:					A list of variables that contains the filename and file location.
##										This list is interated through when reading the files.
##   	ispCycleCount:				Keeps tracks of the number of ISP cycles that have occurred. This is used to determine
##										when to read the PRO Predict txt files.
##		telemetryDict:				A dictionary that uses the timestamp as the key and a list of telemetry lists as the value.
##										This dictionary stores telemetry read from the files and is used to determine which
##										values gets published.
##		addSecs:					This variable can be configured by the script user. It determines how many seconds-worth of telemetry
##										that the script should read from the files (i.e. addSecs = 3600 means read in 1 hours worth of telemetry).
##		cyclesBeforeUpdate:			This variable can be configured by the script user. It determines how many cycles the script should run
##										before reading the files again (i.e cyclesBeforeUpdate = 30 means read files every 30 cycles).
##		currentVehicleTimestamp:	Contains the latest timestamp provided by the ISS in "DDD/HH:MM:SS" string format.
##		futureVehicleTimestamp:		Holds result of adding "addSecs" to "currentVehicleTimestamp" in "DDD/HH:MM:SS" string format.
##		dataName:					Name of telemetry being published
##		tsTotalHours:				A float value that was originally a timestamp in "DDD/HH:MM:SS" string format. Used for the publishValue method.
##		fileModDateDict:			A dictionary that holds the modified date and directory of each file.
##										This is later processed by WatchForChanges function.
##		cyclesBeforeCheckFile:		This variable can be configured by the script user. It determines how many cycles the script should run
##										before checking if the files have been modified (i.e cyclesBeforeCheckFile = 15 means read files every 15 cycles).
##
## Description of sub variables:
##		vehicleTimeSecs:			Raw current vehicle time in seconds
##		futureVehicleTimeSecs:		Result of "vehicleTimeSecs" + "addSecs" in raw seconds
##		tempDict:					Temporary dictionary that holds telemetry as the script is reading files in.
##										It behaves like a list, which allows one to use list methods on a dictionary
##		modDate:					The current modified date recorded by the script
##		newModDate:					The latest modified date recorded by teh script (my be equal to original modified date)
##		fileHasChanged: 			Indicate whether a file has been modified since the script has last read it




## ==========
## LIBRARIES
## ==========
import os, time, collections




## ===========================
## PRO PREDICT FILE VARIABLES
## ===========================
## Store filename and file location (Current reference is from "/PyMCC/Henry" directory)
bga_1a_angle = ["bga_1a_angle", "../../../Folder1/Folder2/Folder3/Stbd_In_Fwd_PV_Beta_MOD.txt"]
bga_1b_angle = ["bga_1b_angle", "../../../Folder1/Folder2/Folder3/Stbd_Out_Aft_PV_Beta_MOD.txt"]
bga_2a_angle = ["bga_2a_angle", "../../../Folder1/Folder2/Folder3/Port_In_Aft_PV_Beta_MOD.txt"]
bga_2b_angle = ["bga_2b_angle", "../../../Folder1/Folder2/Folder3/Port_Out_Fwd_PV_Beta_MOD.txt"]
bga_3a_angle = ["bga_3a_angle", "../../../Folder1/Folder2/Folder3/Stbd_In_Aft_PV_Beta_MOD.txt"]
bga_3b_angle = ["bga_3b_angle", "../../../Folder1/Folder2/Folder3/Stbd_Out_Fwd_PV_Beta_MOD.txt"]
bga_4a_angle = ["bga_4a_angle", "../../../Folder1/Folder2/Folder3/Port_In_Fwd_PV_Beta_MOD.txt"]
bga_4b_angle = ["bga_4b_angle", "../../../Folder1/Folder2/Folder3/Port_Out_Aft_PV_Beta_MOD.txt"]

port_sarj_angle = ["port_sarj_angle", "../../../Folder1/Folder2/Folder3/Port_Pwr_Truss_Alpha_MOD.txt"]
stbd_sarj_angle = ["stbd_sarj_angle", "../../../Folder1/Folder2/Folder3/Stbd_Pwr_Truss_Alpha_MOD.txt"]

port_trrj_angle = ["port_trrj_angle", "../../../Folder1/Folder2/Folder3/Port_TCS_Gamma.txt"]
stbd_trrj_angle = ["stbd_trrj_angle", "../../../Folder1/Folder2/Folder3/Stbd_TCS_Gamma.txt"]

ch_1a_availibilities = ["ch_1a_availibilities", "../../../Folder1/Folder2/Folder3/CH_1A.all[PRI_PWR_AVAIL].txt"]
ch_1a_predicted_power_usage = ["ch_1a_predicted_power_usage", "../../../Folder1/Folder2/Folder3/CH_1A.all[PRI_PWR_USAGE].txt"]
ch_1b_availibilities = ["ch_1b_availibilities", "../../../Folder1/Folder2/Folder3/CH_1B.all[PRI_PWR_AVAIL].txt"]
ch_1b_predicted_power_usage = ["ch_1b_predicted_power_usage", "../../../Folder1/Folder2/Folder3/CH_1B.all[PRI_PWR_USAGE].txt"]
ch_2a_availibilities = ["ch_2a_availibilities", "../../../Folder1/Folder2/Folder3/CH_2A.all[PRI_PWR_AVAIL].txt"]
ch_2a_predicted_power_usage = ["ch_2a_predicted_power_usage", "../../../Folder1/Folder2/Folder3/CH_2A.all[PRI_PWR_USAGE].txt"]
ch_2b_availibilities = ["ch_2b_availibilities", "../../../Folder1/Folder2/Folder3/CH_2B.all[PRI_PWR_AVAIL].txt"]
ch_2b_predicted_power_usage = ["ch_2b_predicted_power_usage", "../../../Folder1/Folder2/Folder3/CH_2B.all[PRI_PWR_USAGE].txt"]
ch_3a_availibilities = ["ch_3a_availibilities", "../../../Folder1/Folder2/Folder3/CH_3A.all[PRI_PWR_AVAIL].txt"]
ch_3a_predicted_power_usage = ["ch_3a_predicted_power_usage", "../../../Folder1/Folder2/Folder3/CH_3A.all[PRI_PWR_USAGE].txt"]
ch_3b_availibilities = ["ch_3b_availibilities", "../../../Folder1/Folder2/Folder3/CH_3B.all[PRI_PWR_AVAIL].txt"]
ch_3b_predicted_power_usage = ["ch_3b_predicted_power_usage", "../../../Folder1/Folder2/Folder3/CH_3B.all[PRI_PWR_USAGE].txt"]
ch_4a_availibilities = ["ch_4a_availibilities", "../../../Folder1/Folder2/Folder3/CH_4A.all[PRI_PWR_AVAIL].txt"]
ch_4a_predicted_power_usage = ["ch_4a_predicted_power_usage", "../../../Folder1/Folder2/Folder3/CH_4A.all[PRI_PWR_USAGE].txt"]
ch_4b_availibilities = ["ch_4b_availibilities", "../../../Folder1/Folder2/Folder3/CH_4B.all[PRI_PWR_AVAIL].txt"]
ch_4b_predicted_power_usage = ["ch_4b_predicted_power_usage", "../../../Folder1/Folder2/Folder3/CH_4B.all[PRI_PWR_USAGE].txt"]

ddcu_LA1A_shar = ["ddcu_LA1A_shar", "../../../Folder1/Folder2/Folder3/LA1A.txt"]
ddcu_LA4A_shar = ["ddcu_LA4A_shar", "../../../Folder1/Folder2/Folder3/LA4A.txt"]
ddcu_LA2A_shar = ["ddcu_LA2A_shar", "../../../Folder1/Folder2/Folder3/LA2A.txt"]
ddcu_LA3B_shar = ["ddcu_LA3B_shar", "../../../Folder1/Folder2/Folder3/LA3B.txt"]
ddcu_N2D1B_shar = ["ddcu_N2D1B_shar", "../../../Folder1/Folder2/Folder3/N2D1B.txt"]
ddcu_N2D4B_shar = ["ddcu_N2D4B_shar", "../../../Folder1/Folder2/Folder3/N2D4B.txt"]
ddcu_N2S1B_shar = ["ddcu_N2S1B_shar", "../../../Folder1/Folder2/Folder3/N2S1B.txt"]
ddcu_N2S4A_shar = ["ddcu_N2S4A_shar", "../../../Folder1/Folder2/Folder3/N2S4A.txt"]
ddcu_N2P2A_shar = ["ddcu_N2P2A_shar", "../../../Folder1/Folder2/Folder3/N2P2A.txt"]
ddcu_N2P3A_shar = ["ddcu_N2P3A_shar", "../../../Folder1/Folder2/Folder3/N2P3A.txt"]
ddcu_N2O2B_shar = ["ddcu_N2O2B_shar", "../../../Folder1/Folder2/Folder3/N2O2B.txt"]
ddcu_N2O3A_shar = ["ddcu_N2O3A_shar", "../../../Folder1/Folder2/Folder3/N2O3A.txt"]
ddcu_N31B_shar = ["ddcu_N31B_shar", "../../../Folder1/Folder2/Folder3/N31B.txt"]
ddcu_N34A_shar = ["ddcu_N34A_shar", "../../../Folder1/Folder2/Folder3/N34A.txt"]
ddcu_N32A_shar = ["ddcu_N32A_shar", "../../../Folder1/Folder2/Folder3/N32A.txt"]
ddcu_N32B_shar = ["ddcu_N32B_shar", "../../../Folder1/Folder2/Folder3/N32B.txt"]

fileLst = [
	bga_1a_angle, bga_1b_angle, bga_2a_angle, bga_2b_angle, bga_3a_angle, bga_3b_angle, bga_4a_angle, bga_4b_angle, port_sarj_angle, stbd_sarj_angle, port_trrj_angle, stbd_trrj_angle, ch_1a_availibilities, ch_1a_predicted_power_usage, ch_1b_availibilities, ch_1b_predicted_power_usage, ch_2a_availibilities, ch_2a_predicted_power_usage, ch_2b_availibilities, ch_2b_predicted_power_usage, ch_3a_availibilities, ch_3a_predicted_power_usage, ch_3b_availibilities, ch_3b_predicted_power_usage, ch_4a_availibilities, ch_4a_predicted_power_usage, ch_4b_availibilities, ch_4b_predicted_power_usage, ddcu_LA1A_shar, ddcu_LA4A_shar, ddcu_LA2A_shar, ddcu_LA3B_shar, ddcu_N2D1B_shar, ddcu_N2D4B_shar, ddcu_N2S1B_shar, ddcu_N2S4A_shar, ddcu_N2P2A_shar, ddcu_N2P3A_shar, ddcu_N2O2B_shar, ddcu_N2O3A_shar, ddcu_N31B_shar, ddcu_N34A_shar, ddcu_N32A_shar, ddcu_N32B_shar
]

fileModDateDict = collections.defaultdict(list)




## =================
## PYMCC VARIABLES
## =================
## "M41F9001D" = GMT
subscriptions = ["M41F9001D"]
publications = [
	"testcomp2", "testcomp3", "testcomp4", "testcomp5", "testcomp6", "testcomp7", "testcomp8", "testcomp9", "testcomp10", "testcomp11", "testcomp12", "testcomp13", "testcomp14", "testcomp15", "testcomp16", "testcomp17", "testcomp18", "testcomp19", "testcomp20", "testcomp21", "testcomp22", "testcomp23", "testcomp24", "testcomp25", "testcomp26", "testcomp27", "testcomp28", "testcomp29", "testcomp30", "testcomp31", "testcomp32", "testcomp33", "testcomp34", "testcomp35", "testcomp36", "testcomp37", "testcomp38", "testcomp39", "testcomp40", "testcomp41", "testcomp42", "testcomp43", "testcomp44", "testcomp45"
]
ispCycleCount = 0
# 3600 cycles = ~ 1 hour
cyclesBeforeUpdate = 3600
cyclesBeforeCheckFile = 15




## =======================
## OUTPARAMS PUBLISH MAP
## =======================
publishToParamDict = {
##	filename:						publish method for each param
	bga_1a_angle[0]: 				"tc2.publishValue(float(value), tsTotalHours)",
	bga_1b_angle[0]: 				"tc3.publishValue(float(value), tsTotalHours)",
	bga_2a_angle[0]: 				"tc4.publishValue(float(value), tsTotalHours)",
	bga_2b_angle[0]: 				"tc5.publishValue(float(value), tsTotalHours)",
	bga_3a_angle[0]: 				"tc6.publishValue(float(value), tsTotalHours)",
	bga_3b_angle[0]: 				"tc7.publishValue(float(value), tsTotalHours)",
	bga_4a_angle[0]: 				"tc8.publishValue(float(value), tsTotalHours)",
	bga_4b_angle[0]: 				"tc9.publishValue(float(value), tsTotalHours)",
	port_sarj_angle[0]: 			"tc10.publishValue(float(value), tsTotalHours)",
	stbd_sarj_angle[0]: 			"tc11.publishValue(float(value), tsTotalHours)",
	port_trrj_angle[0]: 			"tc12.publishValue(float(value), tsTotalHours)",
	stbd_trrj_angle[0]: 			"tc13.publishValue(float(value), tsTotalHours)",
	ch_1a_availibilities[0]: 		"tc14.publishValue(float(value), tsTotalHours)",
	ch_1a_predicted_power_usage[0]: "tc15.publishValue(float(value), tsTotalHours)",
	ch_1b_availibilities[0]: 		"tc16.publishValue(float(value), tsTotalHours)",
	ch_1b_predicted_power_usage[0]: "tc17.publishValue(float(value), tsTotalHours)",
	ch_2a_availibilities[0]: 		"tc18.publishValue(float(value), tsTotalHours)",
	ch_2a_predicted_power_usage[0]: "tc19.publishValue(float(value), tsTotalHours)",
	ch_2b_availibilities[0]: 		"tc20.publishValue(float(value), tsTotalHours)",
	ch_2b_predicted_power_usage[0]: "tc21.publishValue(float(value), tsTotalHours)",
	ch_3a_availibilities[0]: 		"tc22.publishValue(float(value), tsTotalHours)",
	ch_3a_predicted_power_usage[0]: "tc23.publishValue(float(value), tsTotalHours)",
	ch_3b_availibilities[0]: 		"tc24.publishValue(float(value), tsTotalHours)",
	ch_3b_predicted_power_usage[0]: "tc25.publishValue(float(value), tsTotalHours)",
	ch_4a_availibilities[0]: 		"tc26.publishValue(float(value), tsTotalHours)",
	ch_4a_predicted_power_usage[0]: "tc27.publishValue(float(value), tsTotalHours)",
	ch_4b_availibilities[0]: 		"tc28.publishValue(float(value), tsTotalHours)",
	ch_4b_predicted_power_usage[0]: "tc29.publishValue(float(value), tsTotalHours)",
	ddcu_LA1A_shar[0]: 				"tc30.publishValue(float(value), tsTotalHours)",
	ddcu_LA4A_shar[0]: 				"tc31.publishValue(float(value), tsTotalHours)",
	ddcu_LA2A_shar[0]: 				"tc32.publishValue(float(value), tsTotalHours)",
	ddcu_LA3B_shar[0]: 				"tc33.publishValue(float(value), tsTotalHours)",
	ddcu_N2D1B_shar[0]: 			"tc34.publishValue(float(value), tsTotalHours)",
	ddcu_N2D4B_shar[0]: 			"tc35.publishValue(float(value), tsTotalHours)",
	ddcu_N2S1B_shar[0]: 			"tc36.publishValue(float(value), tsTotalHours)",
	ddcu_N2S4A_shar[0]: 			"tc37.publishValue(float(value), tsTotalHours)",
	ddcu_N2P2A_shar[0]: 			"tc38.publishValue(float(value), tsTotalHours)",
	ddcu_N2P3A_shar[0]: 			"tc39.publishValue(float(value), tsTotalHours)",
	ddcu_N2O2B_shar[0]: 			"tc40.publishValue(float(value), tsTotalHours)",
	ddcu_N2O3A_shar[0]: 			"tc41.publishValue(float(value), tsTotalHours)",
	ddcu_N31B_shar[0]: 				"tc42.publishValue(float(value), tsTotalHours)",
	ddcu_N34A_shar[0]: 				"tc43.publishValue(float(value), tsTotalHours)",
	ddcu_N32A_shar[0]: 				"tc44.publishValue(float(value), tsTotalHours)",
	ddcu_N32B_shar[0]: 				"tc45.publishValue(float(value), tsTotalHours)"
}



## =========================
## ESTABLISH ISP CONNECTION
## =========================
def main():
	## Read in file mod date timestamp
	fillFileModDateDict()
	## Creates an ISP Client
	isp = server.Client(subscriptions, publications)
	## Add a cycle callback
	isp.add(isp.CYCLE, mainLoop)
	## Open a connection with the ISP server
	if isp.open("ProPredictsToISP", "0.7"):
		print("ISP Server successfully opened")
	else:
		sys.exit(isp.error())
	## Enter an "infinite" loop handling ISP events as they occur
	isp.loop()



## ================
## ENTER MAIN LOOP
## ================
def mainLoop(isp, numEvents):
	global publishToParamDict, ispCycleCount, telemetryDict
	[gmt] = isp.inParams()
	## Any changes to these outParams() variables should be updated in publishToParamDict as well
	[tc2, tc3, tc4, tc5, tc6, tc7, tc8, tc9, tc10, tc11, tc12, tc13, tc14, tc15, tc16, tc17, tc18, tc19, tc20, tc21, tc22, tc23, tc24, tc25, tc26, tc27, tc28, tc29, tc30, tc31, tc32, tc33, tc34, tc35, tc36, tc37, tc38, tc39, tc40, tc41, tc42, tc43, tc44, tc45] = isp.outParams()

	## How many seconds-worth of telemetry should the script read from the files
	addSecs = 3600

	## Get vehicle time
	[currentVehicleTimestamp, futureVehicleTimestamp] = getVehicleTimestamps(gmt, addSecs)

	## Update files every n cycles
	if (ispCycleCount % cyclesBeforeUpdate) == 0:
		print("UPDATING FILES.")

		# delete time variables after testing
		readStart = time.time()
		telemetryDict = readFiles(fileLst, currentVehicleTimestamp, futureVehicleTimestamp)
		readEnd = time.time()

		# debug statements
		print("LAST UPDATED: " + currentVehicleTimestamp)
		print("READ TIME: " + str(readEnd - readStart) + " SECS")
		print("NUM OF READ VALUES: " + str(len(telemetryDict)) + "\n")

		## reset count to prevent integer variable using more memory
		if ispCycleCount > 268435456:
			ispCycleCount = 1
	## Check if files have changed every n cycles
	elif (ispCycleCount % cyclesBeforeCheckFile) == 0:
		isModified = watchForChanges()
		if (isModified):
			print("FILES HAS BEEN MODIFIED.")

			# delete time variables after testing
			readStart = time.time()
			telemetryDict = readFiles(fileLst, currentVehicleTimestamp, futureVehicleTimestamp)
			readEnd = time.time()

			# debug statements
			print("LAST UPDATED: " + currentVehicleTimestamp)
			print("READ TIME: " + str(readEnd - readStart) + " SECS")
			print("NUM OF READ VALUES: " + str(len(telemetryDict)) + "\n")

			## reset count to prevent integer variable using more memory
			if ispCycleCount > 268435456:
				ispCycleCount = 1
	else:
		pass

	## Publish out timestamp & value based on current GMT
	if currentVehicleTimestamp in telemetryDict:
		tsTotalHours = parseTimestamp(currentVehicleTimestamp)

		## Publish values
		for telem_lst in telemetryDict[currentVehicleTimestamp]:
			[dataName, timestamp, value] = telem_lst
			## Finds correct object and evaluate string value as a function
			eval(publishToParamDict[dataName])

			# debug
			print("PUBLISHING: " + "DATA: " + dataName + " TIMESTAMP: " + timestamp + " VALUE: " + value)

	## Increment cycle counter
	ispCycleCount += 1



## =============
## GET ISS TIME
## =============
def getVehicleTimestamps(gmt, addSecs):
	## Calculate Vehicle Time in seconds & Put into struc_time representation
	## Subtracted 86400 seconds to get day correct
	vehicleTimeSecs = time.gmtime((gmt.value() / 1000) - 86400)
	futureVehicleTimeSecs = time.gmtime((gmt.value() / 1000) - 86400 + addSecs)
	## GMT format (days/hours:minutes:seconds)
	currentVehicleTimestamp = time.strftime("%j/%H:%M:%S", vehicleTimeSecs)
	futureVehicleTimestamp = time.strftime("%j/%H:%M:%S", futureVehicleTimeSecs)

	return [currentVehicleTimestamp, futureVehicleTimestamp]



## ========================
## READ PRO PREDICT FILES
## ========================
def readFiles(fileLst, currentVehicleTimestamp, futureVehicleTimestamp):
	## defaultdict(list) allows a dictionary to use list methods such as list.append()
	tempDict = collections.defaultdict(list)

	for dataName, fileDirectory in fileLst:
		try:
			## Open file
			f = open(fileDirectory, "r")

			## Read each line in file
			for line in f:
				## Parse line
				[timestamp, value] = line.split()

				## Collect telemetry between current time and future time
				if timestamp >= currentVehicleTimestamp and timestamp <= futureVehicleTimestamp:
					## If key was already created, update key with appended values
					## Else, create new key/value
					if timestamp in tempDict:
						tempDict[timestamp].append([dataName, timestamp, value])
					else:
						tempDict[timestamp] = [[dataName, timestamp, value]]
				## If looking too far into the future, stop scanning the file
				elif timestamp > futureVehicleTimestamp:
					break
				## Ignore lines with old timestamps
				else:
					pass

			## Close file
			f.close()
		except FileNotFoundError:
			print("FAIL:" + dataName)

	return tempDict



## =============================
## CONVERT TIMESTAMP INTO HOURS
## =============================
def parseTimestamp(timestamp):
	## Parse timestamp into days, hours, minutes, and seconds (str format)
	[days, clock] = timestamp.split("/")
	[hours, minutes, seconds] = clock.split(":")
	## Convert into total hours
	tsTotalHours = (float(days) * 24) + float(hours) + (float(minutes) / 60) + (float(seconds) / 3600)
	return tsTotalHours



## ========================================================
## CREATE DICTIONARY FROM FILE LIST FOR watchForChanges()
## ========================================================
def fillFileModDateDict():
	global fileModDateDict, fileLst

	for file in fileLst:
		[filename, fileDirectory] = file
		## fileModDateDict structure - filename: [[file mod date, file directory]]
		fileModDateDict[filename].append([os.stat(fileDirectory)[8], fileDirectory])



## ====================================
## CHECK IF FILES HAVE BEEN MODIFIED
## ====================================
def watchForChanges():
	fileHasChanged = False

	## Iterate through fileModDateDict
	for filename, pack in fileModDateDict.items():
		## Unpack the double list
		[[modDate, fileDirectory]] = pack
		## Read in files' last modified date
		newModDate = os.stat(fileDirectory)[8]

		## If new modified date is different from previous modified date,
		## update dictionary and indicate that file has changed
		if (newModDate != modDate):
			tempModDate = newModDate
			fileModDateDict[filename] = tempModDate
			fileHasChanged = True
	## return false if no files have been modified
	return fileHasChanged



if __name__ == "__main__":
	main()
