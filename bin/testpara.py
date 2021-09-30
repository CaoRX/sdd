import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(os.path.join(parentdir, 'src'))

from qdmdealer.dataloading.parameterset import ParameterSet
from qdmdealer.settingLoader import loadSetting, getSetting

from qdmdealer.dataloading.datacollection import DataCollection, defaultLoadingOptions
from qdmdealer.dataloading.datafragment import DataFragment, defaultLightLoadingOptions
from qdmdealer.plotfuncs.plotfuncs import plotObs

import matplotlib.pyplot as plt
import qdmdealer.funcs.funcs as funcs
import qdmdealer.plotfuncs.plotfuncs as plotfuncs

def makeQDMPS(**kwargs):
    ps = ParameterSet()
    
    deskeys = getSetting('deskeys')
    for key in deskeys:
        if key in kwargs:
            ps.appendPara(key, kwargs[key]['type'], kwargs[key]['value'], kwargs[key].get('exclude', False))
    
    return ps 

def makeTimestampPS(low, high):
    ps = ParameterSet()
    ps.appendPara('timestamp', 'range', (low, high), exclude = True)
    return ps

if __name__ == '__main__':
    ps = makeQDMPS(T = {'type': 'range', 'value': (0.70, 0.90)}, wn = {'type': 'value', 'value': [0, 0]})

    # print(ps)

    # tsps = makeTimestampPS(1630822146, 1630822148)
    tsps = makeTimestampPS(0, 2000000000)
    # print(tsps)

    dc = DataCollection()
    data = dc.filter(numFilter = tsps.generateFilter(), desFilter = ps.generateFilter())
    # print(data)

    nps = makeQDMPS(T = {'type': 'fvalue', 'value': 0.71})

    dfOptions = defaultLightLoadingOptions
    df = DataFragment(data = data)
    # print(df.data)
    # print(df.data)
    # for ds in df.getFilteredDataIterable(desFilter = nps.generateFilter()):
    #     print(ds.getDescriber())

    df.divideIntoSets()
    # print(df.data)
    # print(df.dataSets)
    print('dummy keys = {}'.format(df.dummyKeys))
    print(df.data[:10])

    histKey = 'psi int hist int2DHist'
    hist = df.combine(histKey)
    histN = len(hist)
    x, y = plotfuncs.bestXY(histN)
    fig, axes = plotfuncs.getAxes(x, y)

    for data, ax in zip(hist, axes):
        ax.imshow(data[histKey])
    plt.show()

    # obs = df.getObs('rop binder', idx = 0)

    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    plotObs(obsName = 'rop binder', obsData = df.getObs('rop binder', idx = None), axis = 'T', ax = ax1)
    ax2 = fig.add_subplot(122)
    plotObs(obsName = 'cos2t binder', obsData = df.getObs('cos2t binder', idx = None), axis = 'T', ax = ax2)

    plt.show()
