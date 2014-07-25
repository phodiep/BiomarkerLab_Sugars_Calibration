import matplotlib.pyplot as plt


def add_Plot(xyml, fig,subR,subC,subN,title, xLabel, yLabel):
	"""xyml = {dataX, dataY, marker, label} as dictionary"""

	ax = fig.add_subplot(subR,subC,subN)
	for series in xyml:
		ax.plot(series['dataX'],
			series['dataY'],
			series['marker'],
			label=series['label'])

	plt.title(title, fontsize = 12) #add plot title
	ax.locator_params(nbins=10)
	plt.setp(ax.get_xticklabels(), fontsize=10)
	plt.setp(ax.get_yticklabels(), fontsize=10)
	ax.set_xlabel(xLabel, fontsize=10)
	ax.set_ylabel(yLabel, fontsize=10)
	plt.legend(loc='upper left', fontsize=10)

	return fig