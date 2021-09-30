import qdmdealer.funcs.funcs as funcs
import qdmdealer.funcs.binautocorrelation as binAutoCorr
import numpy as np 
class DataProcessor:

    # self.func will accept two dictionaries(data, para) as arguments
    # then it will output a dict(name, numpy objects), and will be put into "obs"
    # nameFunc: only give a list of names that will be output in func
    # but not do real calculations

    def __init__(self, func, name):
        self.func = func
        self.name = name

def getBinDataList(data):
    binDataList = []
    for dataKey in data:
        averageIdx = dataKey.find('average')
        if (averageIdx == -1):
            continue
        binDataName = dataKey[:(averageIdx - 1)]
        if ((binDataName + ' bin sqr') in data) and ((binDataName + ' bin sum') in data):
            if (not (binDataName in binDataList)):
                binDataList.append(binDataName)
    return binDataList

def analyzeBinData(data, dataName, dataN):
    value = data[dataName + ' average']
    binSumName = dataName + ' bin sum'
    binSqrName = dataName + ' bin sqr'
    autoT = binAutoCorr.auto_corr_from_bin(data[binSumName], data[binSqrName], dataN)

    error = 2.0 * np.sqrt(data[binSqrName][0] - data[binSumName][0] ** 2) * np.sqrt(autoT / dataN)
    return {'value': value, 'error': error, 'autoT': autoT}

def binAnalyzeFunc(data, para, obs = None):
    res = dict()

    binDataList = getBinDataList(data)
    assert ('data n' in para), funcs.errorMessage(message = "no 'data n' found in para {}".format(para))
    dataN = para['data n']

    for binDataName in binDataList:
        res[binDataName] = analyzeBinData(data = data, dataName = binDataName, dataN = dataN)

    return res

binProcessor = DataProcessor(func = binAnalyzeFunc, name = 'bin analyzer')