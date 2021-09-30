from qdmdealer.dataloading.dataset import DataSet
from qdmdealer.dataloading.datalabel import DataLabel
from qdmdealer.settingLoader import getSetting
import qdmdealer.funcs.funcs as funcs
from qdmdealer.dataloading.parameterset import ParameterSet
import qdmdealer.funcs.bootstrap as bootstrap

defaultLightLoadingOptions = {
    'fromRawData': False, 
    'obsDataOnly': True, 
    'loadDenseData': False,
    'removeOriginData': False, 
    'discardFuncs': lambda x: False, 
    'rootFolder': getSetting('root'), 
    'dataProcessors': [], 
    'denseFilters': []
}

class DataFragment:

    def __init__(self, data, options = defaultLightLoadingOptions):
        self.data = data
        self.divided = False
        self.options = options

        self.realData = dict()
    
    def getDataIterable(self):
        for data in self.data:
            setNo = data[0].get("setNo")
            seed = data[0].get("seed")
            port = data[0].get("port")
            key = '{}-{}-{}'.format(setNo, seed, port)
            if key in self.realData:
                yield self.realData[ds]
                continue

            try:
                ds = DataSet(DataLabel(seed, port, setNo), **self.options)
                self.realData[ds] = ds
                yield ds
            except:
                pass

        return

    def divideIntoSets(self):
        if self.divided:
            return
        freekeys = getSetting('freekeys')
        deskeys = getSetting('deskeys')
        deselem = getSetting('deselem')
        desexclude = getSetting('desexclude')

        typeDict = dict()
        isExclude = dict()
        for key, elem, exclude in zip(deskeys, deselem, desexclude):
            typeDict[key] = elem
            isExclude[key] = exclude
        
        self.dataSets = []
        for data in self.data:
            inserted = False
            for ds in self.dataSets:
                # {para, filter, [data]}
                if ds['filter'](data[1]):
                    ds['data'].append(data)
                    inserted = True
                    break
            if inserted:
                continue
            ps = ParameterSet()
            para = dict()
            for key in deskeys:
                if key in freekeys:
                    continue
                if not (key in data[1]):
                    continue
                para[key] = data[1][key]
                ps.appendPara(key, typeDict[key], data[1][key], isExclude[key])
            
            self.dataSets.append({'para': para, 'filter': ps.generateFilter(), 'data': [data]})
        
        self.dummyKeys = []
        needKeys = getSetting('need-keys')
        nzNeedKeys = getSetting('nonzero-need-keys')
        if len(self.dataSets) == 0:
            return 
        for key in deskeys:
            if not key in self.dataSets[0]['para']:
                self.dummyKeys.append(key)
                continue
            if key in needKeys:
                continue

            allSameFlag = True
            currValue = self.dataSets[0]['para'][key]
            assert typeDict[key] in ['value', 'fvalue'], funcs.errorMessage("single element type can only be either value or fvalue, {} obtained.".format(typeDict[key]))
            if typeDict[key] == 'value':
                for ds in self.dataSets[1:]:
                    if not (ds['para'][key] == currValue):
                        allSameFlag = False
                        break
            else:
                for ds in self.dataSets[1:]:
                    if not (funcs.floatEqual(currValue, ds['para'][key])):
                        allSameFlag = False
                        break
            
            if (key in nzNeedKeys):
                if abs(self.dataSets[0]['para'][key]) > 1e-7:
                    continue

            if allSameFlag:
                self.dummyKeys.append(key)

        for ds in self.dataSets:
            info = dict()
            for key in ds['para']:
                if not (key in self.dummyKeys):
                    info[key] = ds['para'][key]
            ds['info'] = info

        self.divided = True

    def getFilteredDataIterable(self, numFilter = None, desFilter = None):
        for data in self.data:
            if (numFilter is not None) and (not numFilter(data[0])):
                continue
            if (desFilter is not None) and (not desFilter(data[1])):
                continue
            
            setNo = data[0].get("setNo")
            seed = data[0].get("seed")
            port = data[0].get("port")
            key = '{}-{}-{}'.format(setNo, seed, port)
            if key in self.realData:
                yield self.realData[ds]
                continue
            try:
                ds = DataSet(DataLabel(seed, port, setNo), **self.options)
                self.realData[key] = ds
                yield ds
            except:
                pass

        return

    def getObs(self, obsName, idx = None):
        self.divideIntoSets()
        dataLengthKey = getSetting('data-length-key')
        res = []
        for ds in self.dataSets:
            info = ds['info']
            if len(ds['data']) == 0:
                continue
            obsLists = []
            weights = []
            for stamps, para in ds['data']:
                setNo = stamps.get("setNo")
                seed = stamps.get("seed")
                port = stamps.get("port")
                key = '{}-{}-{}'.format(setNo, seed, port)
                if not (key in self.realData):
                    self.realData[key] = DataSet(DataLabel(seed, port, setNo), **self.options)
                    # print(self.realData[key].para.keys())
                # print('obs = {}'.format(self.realData[key].obs))
                if obsName not in self.realData[key].obs:
                    continue
                obsLists.append(self.realData[key].obs[obsName])
                weights.append(para[dataLengthKey])

            if len(obsLists) == 0:
                continue
            elif len(obsLists) == 1:
                value = obsLists[0]
            else:
                # print('obsLists = {}'.format(obsLists))
                if (idx is None) or (idx == 0):
                    value = bootstrap.weightedBootstrapEstimateFunctionalByFunc(funcs.identityFunc, weights, [funcs.getSingle(x['value']) for x in obsLists])
                else:
                    value = bootstrap.weightedBootstrapEstimateFunctionalByFunc(funcs.identityFunc, weights, [x['value'][idx] for x in obsLists])
            
            res.append({'info': info, 'obs': value})
        
        return res

    def combine(self, obsKey):
        # key is one of the data items in dense
        # combine over "divideIntoSets"

        coreKeySet = set()
        res = []

        self.divideIntoSets()
        for ds in self.dataSets:
            info = ds['info']
            if len(ds['data']) == 0:
                continue
            
            keyList = []
            hasShared = []
            for stamps, para in ds['data']:
                setNo = stamps.get("setNo")
                seed = stamps.get("seed")
                port = stamps.get("port")
                key = '{}-{}-{}'.format(setNo, seed, port)

                keyList.append(key)
                if not (key in self.realData):
                    self.realData[key] = DataSet(DataLabel(seed, port, setNo), **self.options)
                ds = self.realData[key]
                # if ds.dense is None:
                #     ds.loadDense()
                if ds.shared is None:
                    ds.loadShared()
                if (ds.shared is not None) and (obsKey in ds.shared):
                    hasShared.append({'key': key, 'contains': ds.shared[obsKey]['contains']})
            
            # our goal: combine all data of keys in keySet
            # first contain hasShared

            # if a['contains'] contain b['contains']: then only consider b
            # if they has something in common while not contain each other: error
            
            calculated = set()
            resData = None
            for hs in hasShared:
                hasCalculated = False
                hasUncalculated = False
                for key in hs['contains']:
                    if key in calculated:
                        hasCalculated = True
                    if key not in calculated:
                        hasUncalculated = True
                
                if hasCalculated and hasUncalculated:
                    raise ValueError(funcs.errorMessage("{} has both calculated and uncalculated data".format(hs), loc = 'DataFragment.combine'))

                if hasCalculated:
                    continue 

                resData = funcs.accumulate(resData, self.realData[hs['key']].shared[obsKey]['data'])
                for key in hs['contains']:
                    calculated.add(key)

            # print('keyList = {}'.format(keyList))
            # print('keyCalculated = {}'.format(calculated))
            for key in keyList:
                if key in calculated:
                    continue
                ds = self.realData[key]
                if ds.dense is None:
                    ds.loadDense()
                    print(ds.dense)
                if obsKey in ds.dense:
                    resData = funcs.accumulate(resData, ds.dense[obsKey])
                    calculated.add(key)

            calculatedList = list(calculated)
            if len(calculatedList) > 0:
                # then we need to save it to some dataset
                coreKey = keyList[0]
                self.realData[coreKey].shared[obsKey] = {'contains': calculatedList, 'data': resData}
                coreKeySet.add(coreKey)
                res.append({'info': info, obsKey: resData})
        
        for coreKey in coreKeySet:
            self.realData[coreKey].saveShared()

        return res

                    

            



