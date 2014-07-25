import os

os_name = os.name # windows = nt
slash = ('\\' if os_name=='nt' else '/') # nt = windows (\\), else use (/)

def convertCSVType(csvFile):
	"""Opens csv File decodes 'UTF-16'and returns 'ASCII' encoded data csvFile = file to be opened"""

	decodeData = csvFile.read().decode('UTF-16')            #decode UTF-16
	encodeData = decodeData.encode('ASCII','replace')       #encode ASCII
	return encodeData

def getCSVdata(csvData,keyName):
	"""converts csv file data to tuple for each entry
	   and removes all " <space> newLine from csv file and splits lines at \r"""
	import re
	
	reData = re.sub('"|\n| ','',str(csvData)) #remove all " and <spaces> and newLine using Regular Expressions (re) ... must 'import re'
	tmpSample = reData.split('\r')     #split string into list - spliting at \r
	
	tmpData = ()
	for row in tmpSample: tmpData += row.split(','),

	if keyName == 'info': cleanData = cleanInfo_info(tmpData)
	if keyName == 'column': cleanData = cleanInfo_column(tmpData)

	return cleanData

def cleanInfo_info(tmpData):
	"""only keep columns of interest to study  - return as dictionary
	listToKeep1 returns column 1
	listToKeep2 returns column 2"""

	dataToReturn = {}

	listToKeep1 = ('SampleName','Acq.Instrument','Acq.Method')
	listToKeep2 = ('DataFile',)

	for line in tmpData:
		if line[0] in listToKeep1: dataToReturn[line[0]] = line[1]
		if line[0] in listToKeep2: dataToReturn[line[0]] = line[2]

	return dataToReturn

def cleanInfo_column(tmpData):
	"""only keep columns of interest to study  - return as dictionary"""

	dataToReturn = {}

	for line in tmpData:
		if line == ['']: continue
		if line[2] == '-': continue
		dataToReturn[line[7]] = float(line[2])

	return dataToReturn

def combineReport00_01(path, listLower):
	"""given the path and list of folders, combines data from Report00 and Report01 into a single dictionary"""

	reportsToRun = [{'name': '%sREPORT00.CSV' % slash, 'datatype':'info'},
					{'name': '%sREPORT01.CSV' % slash, 'datatype':'column'}]
	results = []

	if (not 'report00.csv' in listLower) or (not 'report01.csv' in listLower): return {}
	for report in reportsToRun:
		with open(path+str(report['name']),"rb") as csvFile:			
			csvSample = convertCSVType(csvFile)                        #convert to readable format
			results += getCSVdata(csvSample,report['datatype']).items()  #convert csv to list
			
	return dict(results)

def osWalkSorted(path):
	'''Pulls out and sorts tuple of pathways to ensure files are read in acending order'''
	import os
	pathList = []

	for i in os.walk(path): pathList.append(i) 
	pathList.sort()
  
	return pathList

def extractDataFromCSV(path):
	"""combines csv data given the path, returns as a list of dictionaries"""
	results = ()
	for (path,dirs,files) in osWalkSorted(path):
		tmpListLower = []
		sampleResultsReport = {}

		for item in files: tmpListLower += item.lower(),
		sampleResultsReport = combineReport00_01(path, tmpListLower)
		if sampleResultsReport != {}: results += sampleResultsReport,

	return results