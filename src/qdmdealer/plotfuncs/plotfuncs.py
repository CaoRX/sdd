import qdmdealer.funcs.funcs as funcs
import matplotlib.pyplot as plt
import numpy as np

def plotObs(obsName, obsData, axis, ax = None):
    axNone = False
    if ax is None:
        axNone = True
        fig = plt.figure()
        ax = fig.add_subplot(111)
    # obsData comes from DataFragment.getObs
    for data in obsData:
        assert axis in data['info'], funcs.errorMessage("plot axis {} not in data info {}".format(axis, data['info']), loc = 'qdmdealer.plotfuncs.plotfuncs.plotObs')
    
    dataList = []
    for data in obsData:
        info = funcs.dictExcept(data['info'], [axis])
        foundFlag = False
        for key, value in dataList:
            if funcs.dictEqual(key, info):
                value[axis].append(data['info'][axis])
                value['value'].append(data['obs']['value'])
                value['error'].append(data['obs'].get('error', None))
                foundFlag = True
                break

        if not foundFlag:
            dataList.append((info, dict()))
            dataList[-1][1][axis] = [data['info'][axis]]
            dataList[-1][1]['value'] = [data['obs']['value']]
            dataList[-1][1]['error'] = [data['obs'].get('error', None)]
    
    for key, data in dataList:
        label = funcs.makeLabel(key)
        hasError = not funcs.isAllNone(data['error'])
        if hasError:
            ax.errorbar(x = data[axis], y = data['value'], yerr = data['error'], fmt = 'o-', label = label)
        else:
            ax.plot(data[axis], data['value'], fmt = 'o-', label = label)

    ax.set_xlabel(axis)
    ax.set_ylabel(obsName)
    ax.legend()
    if axNone:
        plt.show()

def bestXY(dataCount):
	assert (dataCount > 0), "Error: bestXY(dataCount) must work with positive dataCount, but {} input".format(dataCount)
	x = int(np.sqrt(dataCount))
	if (dataCount % x == 0):
		y = dataCount // x
	else:
		y = (dataCount // x) + 1
	return x, y
def getAxes(xn, yn):
	fig, axes = plt.subplots(xn, yn)
	if (xn * yn == 1):
		axes = [axes]
	if (isinstance(axes[0], np.ndarray)):
		newAxes = []
		for axs in axes:
			for ax in axs:
				newAxes.append(ax)
		axes = newAxes

	return fig, axes