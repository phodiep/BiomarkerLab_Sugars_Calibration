import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import csv
import math

from ScatterPlots import add_Plot
from Report00_01Handling import extractDataFromCSV

os_name = os.name # windows = nt
slash = ('\\' if os_name=='nt' else '/') # nt = windows (\\), else use (/)

def clear_terminal():
	"""clear terminal"""
	os.system('cls' if os_name=='nt' else 'clear')

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

clear_terminal()
finalResults = ()

if os_name == 'nt': #running windows at work
	main()
	pDrivePath = 'P:\\XSONG\\Laboratory\\Assay_Sugars\\rawdata\\'
	# fileDate = str(raw_input('\nEnter Folder Name \n')) or ''
	fileDate = '050214pda'

else:
	pDrivePath = '/Users/phodiep/Dropbox/Sugars/'
	fileDate = '020614pd'

path = pDrivePath + fileDate
fileWriteTo = '%s%sraw_data.csv' % (path, slash)
pltWriteTo = '%s%scalibration.jpg' % (path, slash)
stdCurveFile = 'StandardCurve.csv'

#check for null user input
if fileDate == '': userError('null')
  
#check for non-existent folder
elif not os.path.isdir(pDrivePath + fileDate): userError('folder')

#else... folder exists... so run
else:
	startTime = time.time()
	print '\nPlease wait while data is being consolidated........ \n'

	#====import standard curve expected values====
	stdCurve = pd.read_csv(stdCurveFile)
	finalResults = extractDataFromCSV(path)

	#if no data found don't print report
	if finalResults == (): userError('results')

	#else run report
	else:
		sugarsList1, sugarsList2 = ['Mannitol','Fructose','Glucose',], ['Sucrose','Lactulose']
		internalStandard1, internalStandard2 = 'Inositol', 'Turanose'
		internalStandards = [internalStandard1, internalStandard2]
		sugarsList = sugarsList1 + sugarsList2 + internalStandards
		columnOrder = ['SampleName','Acq.Instrument','Acq.Method','DataFile','Fructose1','Fructose2'] + sugarsList
		
		df = pd.DataFrame(list(finalResults), columns = columnOrder)

		#======================= Standard concentration values and calculate IS Ratio=======================
		for sugar in sugarsList:
			if sugar in internalStandards:
				df['std_'+str(sugar)] = stdCurve[sugar][0]
			else:
				df['std_'+str(sugar)] = stdCurve.get(sugar,'NaN')

		df['ISTD Ratio'] = df[internalStandard1] / df[internalStandard2]

		#============================ Calculate Fructose = Fructose1+Fructose2 ==============================
		try: 
			df['Fructose'] = df['Fructose1'] + df['Fructose2']
			df = df.drop(['Fructose1','Fructose2'], axis = 1)
		except: pass

		#=======================calculate adjusted area counts	= sugarX / ISTD=======================
		for sugar in sugarsList:
			if sugar in internalStandards:
				df['adjAC_'+str(sugar)] = 1.0
			if sugar in sugarsList1:
				df['adjAC_'+str(sugar)] = df[sugar]/df[internalStandard1]
			if sugar in sugarsList2:
				df['adjAC_'+str(sugar)] = df[sugar]/df[internalStandard2]

		#=======================calculate m (slope) for each analyte=======================
		tmpStd = df.loc[df['std_Mannitol'] > 0.0]
		m_Dict = {}
		for sugar in sugarsList:
			if sugar in internalStandards:
				m_Dict['m_'+str(sugar)] = 1.0
			else:
				m_Dict['m_'+str(sugar)] = getLinearZero(np.array(tmpStd['std_'+str(sugar)]), np.array(tmpStd['adjAC_'+str(sugar)]))

		#=======================get plot titles w/ equation=======================
		getTitle = lambda name, m: '%s (y = %.4f * x)' % (name, m)
		title_Dict = {}
		for sugar in sugarsList:
			title_Dict['title_'+str(sugar)] = getTitle(str(sugar), m_Dict['m_'+str(sugar)])

		#=======================calculate concentrations for analytes ... y = x * m ... x = y / m =======================
		getConcentration = lambda y, m: np.array(y) / m

		for sugar in sugarsList:
			if sugar in internalStandards:
				df['Conc_'+str(sugar)] = df['std_'+str(sugar)]
			else:
				df['Conc_'+str(sugar)] = getConcentration(df['adjAC_'+str(sugar)], m_Dict['m_'+str(sugar)])



		# #=======================plot============================
		fig = plt.figure(figsize=(12,9), dpi=100)
		fig.suptitle('Calibration Tables (' + str(fileDate) + ')')

		numberOfPlots = len(sugarsList1 + sugarsList2)
		gridForPlots = math.ceil(math.sqrt(numberOfPlots))

		plotCount = 1
		for sugar in sugarsList:
			if sugar in internalStandards:
				pass
			else:
				plotTrendline = {'dataX': df['Conc_'+str(sugar)],
								 'dataY': df['adjAC_'+str(sugar)],
								 'marker': 'y-',
								 'label': 'Fitted'}

				plotSamples = {'dataX': df['Conc_'+str(sugar)],
							   'dataY': df['adjAC_'+str(sugar)],
							   'marker': 'r.',
							   'label': 'Samples'}

				plotStandards = {'dataX': tmpStd['std_'+str(sugar)],
								 'dataY': tmpStd['std_'+str(sugar)] * m_Dict['m_'+str(sugar)],
								 'marker': 'b.',
								 'label': 'Standards'}

				add_Plot([plotTrendline, plotSamples, plotStandards],
						fig, gridForPlots, gridForPlots, plotCount,
						title_Dict['title_'+str(sugar)],
						'Concentration (ug/ml)', 'Adjusted Area Count')
				plotCount += 1

		plt.tight_layout()
		plt.subplots_adjust(top=0.92)


		#=======================export csv/plot=======================

		#-------------- Column order for export ----------------------
		std_columnOrder = ['std_'+str(sugar) for sugar in sugarsList]
		area_columnOrder = [str(sugar) for sugar in sugarsList]
		conc_columnOrder = ['Conc_'+str(sugar) for sugar in sugarsList]
		
		columnOrderExport = ['SampleName','Acq.Instrument','Acq.Method','DataFile'] + std_columnOrder + area_columnOrder + conc_columnOrder
		df_export = df[columnOrderExport]

		df_export.to_csv(fileWriteTo,index=False)
		fig.savefig(pltWriteTo)

		print '\n%s\n\nConsolidated Report has been saved here: %s\n' % ('*'*70, fileWriteTo)
		print 'Total time for data consolidation: %.5f seconds' % (time.time() - startTime)
		raw_input('\nPress ENTER to close application and open the consolidated report in Excel')
		os.startfile(fileWriteTo, 'open')
		os.startfile(pltWriteTo, 'open')

