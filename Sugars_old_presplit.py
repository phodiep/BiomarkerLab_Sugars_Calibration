import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import csv

os_name = os.name # windows = nt
slash = ('\\' if os_name=='nt' else '/') # nt = windows (\\), else use (/)

def clear_terminal():
	"""clear terminal"""
	os.system('cls' if os_name=='nt' else 'clear')

def convertCSVType(csvFile):
	"""Opens csv File decodes 'UTF-16'and returns 'ASCII' encoded data csvFile = file to be opened"""

	decodeData = csvFile.read().decode('UTF-16')            #decode UTF-16
	encodeData = decodeData.encode('ASCII','replace')       #encode ASCII
	return encodeData

def getCSVdata(csvData,keyName):
	"""converts csv file data to tuple for each entry
	   and removes all " <space> newLine from csv file and splits lines at \r"""

	reData = re.sub('"|\n| ','',str(csvData)) #remove all " and <spaces> and newLine using Regular Expressions (re) ... must 'import re'
	tmpSample = reData.split('\r')     #split string into list - spliting at \r
	
	tmpData = ()
	for row in tmpSample: tmpData += row.split(','),

	if keyName == 'info': cleanData = cleanInfo_info(tmpData)
	if keyName == 'column': cleanData = cleanInfo_column(tmpData)

	return cleanData

def cleanInfo_info(tmpData):
	"""only keep columns of interest to study  - return as dictionary"""

	dataToReturn = {}

	listToKeep1 = ('SampleName','Acq.Instrument','Acq.Method')
	listToKeep2 = 'DataFile'

	for line in tmpData:
		if line[0] in listToKeep1: dataToReturn[line[0]] = line[1]
		if line[0] == listToKeep2: dataToReturn[line[0]] = line[2]

	return dataToReturn

def cleanInfo_column(tmpData):
	"""only keep columns of interest to study  - return as dictionary"""

	dataToReturn = {}

	for line in tmpData:
		if line == ['']: continue
		if line[2] == '-': continue
		dataToReturn[line[7]] = float(line[2])

	return dataToReturn

def main():
	print """
	==============================================
	           Urinary Sugar Analysis

	                 Version 1.0
	           Last updated 2.10.2014

	==============================================
	   Written By: Pho Diep (phodiep@gmail.com)

	          Written in Python 2.7.3
	         Packaged using Py2Exe 0.6.9

	----------------------------------------------
	"""

	directions = raw_input('Do you want directions? (y/n) \n') or 'n'
	if directions.lower() == 'y':
		print """
	---------------------------------------------------------------------
	Directions:
	           
	1. Place the rawdata folder into the following path:
	   P:\\XSONG\\Laboratory\\Assay_Sugars\\rawdata\\

	2. User will then be asked for "Folder Name".
	   This is the name of the folder placed above.

	   Example: '091312PD'

	3. The consolidated "raw_data.csv" file will be placed inside
	   the same rawdata folder.

	   Example: P:\\XSONG\\Laboratory\\Assay_Sugars\\rawdata\\091312PD\\raw_data.csv
	---------------------------------------------------------------------
		"""

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

def setStdConc(df):
	stdConc = {'S1': 5.0,
			   'S2': 1.67,
			   'S3': 0.56,
			   'S4': 0.19,
			   'S5': 0.06,
			   'S6': 0.02,
			   'S7': 0.01,
			   'S8': 0.005,
			   'S9': 0.0025,
			   'S10': 0.0013,
			   'S11': 0.0006,
			   'S12': 0.0003}

	results = list()
	for sample in df: results += stdConc.get(sample, 'NaN'),

	return results

def userError(error):
	if error == 'null':     print '\nPlease enter a valid folder name.'
	if error == 'folder':   print '\nPlease enter a valid folder name.'
	if error == 'results':  print '\nThere were no results to consolidate!'
	raw_input('\nPress ENTER to close application')

def getLinearZero(x,y):
	x = x[:,np.newaxis]
	a, _, _, _ = np.linalg.lstsq(x, y)
	return a[0]

def add_Plot(x, y, m, q, q_x, allX, fig,subR,subC,subN,title):

	ax = fig.add_subplot(subR,subC,subN)

	ax.plot(x, y, 'o',label='Standards', markersize=5)
	ax.plot(allX, m*allX, '-',label='Fitted')
	ax.plot(q_x, q, '.',label='Unknowns')

	plt.title(title, fontsize = 12) #add plot title
	ax.locator_params(nbins=10)
	plt.setp(ax.get_xticklabels(), fontsize=10)
	plt.setp(ax.get_yticklabels(), fontsize=10)
	ax.set_xlabel('Concentration (ug/ml)', fontsize=10)
	ax.set_ylabel('Adjusted Area Count', fontsize=10)
	plt.legend(loc='upper left', fontsize=10)

	return fig



clear_terminal()
finalResults = ()

if os_name == 'nt': #running windows at work
	pDrivePath = 'P:\\XSONG\\Laboratory\\Assay_Sugars\\rawdata\\'
	fileDate = str(raw_input('\nEnter Folder Name \n')) or ''
	main()
else:
	pDrivePath = '/Users/phodiep/Dropbox/Sugars/'
	fileDate = '020614pd'

path = pDrivePath + fileDate
fileWriteTo = '%s%sraw_data.csv' % (path, slash)
pltWriteTo = '%s%scalibration.jpg' % (path, slash)

#check for null user input
if fileDate == '': userError('null')
  
#check for non-existent folder
elif not os.path.isdir(pDrivePath + fileDate): userError('folder')

#else... folder exists... so run
else:
	startTime = time.time()
	print '\nPlease wait while data is being consolidated........ \n'
	finalResults = extractDataFromCSV(path)

	#if no data found don't print report
	if finalResults == (): userError('results')

	#else run report
	else:
		columnOrder = ['SampleName','Acq.Instrument','Acq.Method','DataFile','Mannitol','Fructose','Glucose','Inositol','Sucrose','Lactulose','Turanose','Fructose1','Fructose2']
		df = pd.DataFrame(list(finalResults), columns = columnOrder)

		#=======================calculate IS Ratio and add standard concentration values=======================
		df['ISTD Ratio'] = df['Inositol']/df['Turanose']
		df['StdConc'] = setStdConc(df['SampleName'])
		df['ISConc_Inositol'] = float(raw_input('\n\nEnter INOSITOL concentration (press ENTER for default: 0.428):   ') or 0.428)
		df['ISConc_Turanose'] = float(raw_input('\n\nEnter TURANOSE concentration (press ENTER for default: 0.396):   ') or 0.396)
		
		# calculate Fructose = Fructose1+Fructose2
		try: 
			df['Fructose'] = df['Fructose1'] + df['Fructose2']
			df = df.drop(['Fructose1','Fructose2'], axis = 1)
		except: pass

		clear_terminal()
		print '\nPlease confirm the Standard Concentrations: \n'
		print df[['SampleName','StdConc']]

		prompt_Sample = raw_input('\nEnter Sample # to correct concentration (else press ENTER to continue) \n')
		confirm = str(prompt_Sample)
		while confirm != '':
			try:
				df['StdConc'][int(confirm)] = float(raw_input('\nEnter correct concentration (or NaN):   '))
				print df[['SampleName','StdConc']]
				confirm = str(prompt_Sample)

			except:
				print df[['SampleName','StdConc']]
				confirm = str(prompt_Sample)

		#=======================calculate adjusted area counts	= sugarX / ISTD=======================
		df['adjAC_Mannitol'] = df['Mannitol']/df['Inositol']
		df['adjAC_Fructose'] = df['Fructose']/df['Inositol']
		df['adjAC_Glucose'] = df['Glucose']/df['Inositol']
		df['adjAC_Sucrose'] = df['Sucrose']/df['Turanose']
		df['adjAC_Lactulose'] = df['Lactulose']/df['Turanose']

		#=======================calculate m (slope) for each analyte=======================
		tmpStd = df.loc[df['StdConc']!='NaN']
		tmpSample = df.loc[df['StdConc']=='NaN']
		m_Mannitol = getLinearZero(np.array(tmpStd['StdConc']), np.array(tmpStd['adjAC_Mannitol']))
		m_Fructose = getLinearZero(np.array(tmpStd['StdConc']), np.array(tmpStd['adjAC_Fructose']))
		m_Inositol = 1.0
		m_Glucose = getLinearZero(np.array(tmpStd['StdConc']), np.array(tmpStd['adjAC_Glucose']))
		m_Sucrose = getLinearZero(np.array(tmpStd['StdConc']), np.array(tmpStd['adjAC_Sucrose']))
		m_Lactulose = getLinearZero(np.array(tmpStd['StdConc']), np.array(tmpStd['adjAC_Lactulose']))
		m_Turanose = 1.0

		#=======================get plot titles w/ equation=======================
		getTitle = lambda name, m: '%s (y = %.4f * x)' % (name, m)

		title_Mannitol = getTitle('Mannitol', m_Mannitol)
		title_Fructose = getTitle('Fructose', m_Fructose)
		title_Glucose = getTitle('Glucose', m_Glucose)
		title_Inositol = getTitle('Inositol', m_Inositol)
		title_Sucrose = getTitle('Sucrose', m_Sucrose)
		title_Lactulose = getTitle('Lactulose', m_Lactulose)
		title_Turanose = getTitle('Turanose', m_Turanose)

		#=======================calculate concentrations for analytes ... y = x * m ... x = y / m =======================
		getConcentration = lambda y, m: np.array(y) / m

		df['Conc_Mannitol'] = getConcentration(df['adjAC_Mannitol'], m_Mannitol)
		df['Conc_Fructose'] = getConcentration(df['adjAC_Fructose'], m_Fructose)
		df['Conc_Glucose'] = getConcentration(df['adjAC_Glucose'], m_Glucose)
		df['Conc_Inositol'] = df['ISConc_Inositol']
		df['Conc_Sucrose'] = getConcentration(df['adjAC_Sucrose'], m_Sucrose)
		df['Conc_Lactulose'] = getConcentration(df['adjAC_Lactulose'], m_Lactulose)
		df['Conc_Turanose'] = df['ISConc_Turanose']

		#calculate unknowns for plotting
		qx_Mannitol = getConcentration(tmpSample['adjAC_Mannitol'], m_Mannitol)
		qx_Fructose = getConcentration(tmpSample['adjAC_Fructose'], m_Fructose)
		qx_Glucose = getConcentration(tmpSample['adjAC_Glucose'], m_Glucose)
		qx_Sucrose = getConcentration(tmpSample['adjAC_Sucrose'], m_Sucrose)
		qx_Lactulose = getConcentration(tmpSample['adjAC_Lactulose'], m_Lactulose)

		#=======================plot============================
		fig = plt.figure(figsize=(12,9), dpi=100)
		fig.suptitle('Calibration Tables (' + str(fileDate) + ')')
		add_Plot(tmpStd['StdConc'],tmpStd['adjAC_Mannitol'],m_Mannitol,tmpSample['adjAC_Mannitol'],qx_Mannitol,df['adjAC_Mannitol'],fig,2,3,1,title_Mannitol)
		add_Plot(tmpStd['StdConc'],tmpStd['adjAC_Fructose'],m_Fructose,tmpSample['adjAC_Fructose'],qx_Fructose,df['adjAC_Fructose'],fig,2,3,2,title_Fructose)
		add_Plot(tmpStd['StdConc'],tmpStd['adjAC_Glucose'],m_Glucose,tmpSample['adjAC_Glucose'],qx_Glucose,df['adjAC_Glucose'],fig,2,3,3,title_Glucose)
		add_Plot(tmpStd['StdConc'],tmpStd['adjAC_Sucrose'],m_Sucrose,tmpSample['adjAC_Sucrose'],qx_Sucrose,df['adjAC_Sucrose'],fig,2,3,4,title_Sucrose)
		add_Plot(tmpStd['StdConc'],tmpStd['adjAC_Lactulose'],m_Lactulose,tmpSample['adjAC_Lactulose'],qx_Lactulose,df['adjAC_Lactulose'],fig,2,3,5,title_Lactulose)
		plt.tight_layout()
		plt.subplots_adjust(top=0.92)

		#=======================export csv/plot=======================
		columnOrderExport = ['SampleName','Acq.Instrument','Acq.Method','DataFile',
							 'StdConc', 'ISConc_Inositol', 'ISConc_Turanose',
							 'Mannitol','Fructose','Glucose','Inositol','Sucrose','Lactulose','Turanose','ISTD Ratio',
							 'Conc_Mannitol','Conc_Fructose','Conc_Glucose','Conc_Inositol','Conc_Sucrose','Conc_Lactulose','Conc_Turanose']
		df_export = df[columnOrderExport]

		df_export.to_csv(fileWriteTo,index=False)
		fig.savefig(pltWriteTo)

		print '\n%s\n\nConsolidated Report has been saved here: %s\n' % ('*'*70, fileWriteTo)
		print 'Total time for data consolidation: %.5f seconds' % (time.time() - startTime)
		raw_input('\nPress ENTER to close application and open the consolidated report in Excel')
		os.startfile(fileWriteTo, 'open')
		os.startfile(pltWriteTo, 'open')

