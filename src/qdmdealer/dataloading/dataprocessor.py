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

def getBinderDataList(data):
    binderDataList = []
    for dataKey in data:
        if dataKey.endswith('124'):
            binderDataList.append(dataKey[:-3])
    return binderDataList

def analyzeBinData(data, dataName, dataN):
    value = data[dataName + ' average']
    binSumName = dataName + ' bin sum'
    binSqrName = dataName + ' bin sqr'
    autoT = binAutoCorr.auto_corr_from_bin(data[binSumName], data[binSqrName], dataN)

    error = 2.0 * np.sqrt(data[binSqrName][0] - data[binSumName][0] ** 2) * np.sqrt(autoT / dataN)
    return {'value': value, 'error': error, 'autoT': autoT}

def binAnalyzeFunc(**kwargs):
    data = kwargs.get('data')
    para = kwargs.get('para')
    # obs = kwargs.get('obs', None)
    res = dict()

    binDataList = getBinDataList(data)
    # print('bin data = {}'.format(binDataList))
    # print(para.keys())
    assert ('data n' in para), funcs.errorMessage(message = "no 'data n' found in para {}".format(para))
    dataN = para['data n']

    for binDataName in binDataList:
        res[binDataName] = analyzeBinData(data = data, dataName = binDataName, dataN = dataN)

    return res

def dataNProcessorFunc(**kwargs):
    para = kwargs.get('para')
    if 'data n' in para:
        return dict()
    para['data n'] = int(para.get('loop n') * (1 - para.get('equil')) + 1e-5)
    return dict()

def binderAnalyzeFunc(**kwargs):
    obs = kwargs.get('obs')
    res = dict()

    binderDataList = getBinderDataList(obs)
    for binderDataName in binderDataList:
        binderData = obs[binderDataName + '124']
        res[binderDataName + ' binder'] = {'value': binderData['value'][2] / (binderData['value'][1] ** 2)}
    
    return res

def windingNumberAnalyzeFunc(**kwargs):
    data = kwargs.get('data')
    para = kwargs.get('para')
    if 'winding number' in para:
        return dict()
    para['winding number'] = [int(data.get('winding number 0')), int(data.get('winding number 1'))]
    return dict()

denseProcessorSet = dict()

def cos2tAnalyzeFunc(**kwargs):
    dense = kwargs.get('dense')
    para = kwargs.get('para')

    L = para.get("L")
    n, m = L, L
    sx = (n * m + 1)
    sy = sx

    r = (sx - 1) // 2
    x = None 
    y = None
    d = None

    res = dict()

    for i in [1, 2, 4]:
        obsName = 'cos2t{}'.format(i)
        # print('obsName = {}'.format(obsName))
        if L in denseProcessorSet and obsName in denseProcessorSet[L]:
            data = denseProcessorSet[L][obsName]
        else:
            if d is None:
                x = np.arange(-r, r + 0.5, 1)
                y = np.arange(-r, r + 0.5, 1)
                x, y = np.meshgrid(x, y)
                d = (x ** 2 - y ** 2) / (x ** 2 + y ** 2)
                d[r][r] = 0.0
            data = d ** i
            if L not in denseProcessorSet:
                denseProcessorSet[L] = dict()
            denseProcessorSet[L][obsName] = data
        # print(data.shape, dense['psi int hist int2DHist'].shape)
            
        res[obsName] = {'value': np.sum(data * dense['psi int hist int2DHist']) / np.sum(dense['psi int hist int2DHist'])}
    
    res['cos2t binder'] = {'value': res['cos2t4'].get('value') / (res['cos2t2'].get('value') ** 2)}
    return res

windingNumberProcessor = DataProcessor(func = windingNumberAnalyzeFunc, name = 'wn processor')
dataNProcessor = DataProcessor(func = dataNProcessorFunc, name = 'dataN processor')
binProcessor = DataProcessor(func = binAnalyzeFunc, name = 'bin analyzer')
binderProcessor = DataProcessor(func = binderAnalyzeFunc, name = 'binder analyzer')
cos2tProcessor = DataProcessor(func = cos2tAnalyzeFunc, name = 'cos2t analyzer')