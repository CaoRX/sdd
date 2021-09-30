from qdmdealer.settingLoader import loadSetting, getSetting
import qdmdealer.funcs.funcs as funcs

from qdmdealer.dataloading.datalabel import DataLabel, decodeSetSeed, encodeSetSeed
from qdmdealer.dataloading.dataset import DataSet
import json
import os
import warnings

defaultLoadingOptions = {
    'fromRawData': True, 
    'obsDataOnly': False, 
    'removeOriginData': False, 
    'discardFuncs': lambda x: False, 
    'rootFolder': getSetting('root'), 
    'dataProcessors': [], 
    'denseFilters': []
}

class DataCollection:
    # load a json file, then load data
    # can append new data
    # load to a list of tuples: (label, describer)

    def __init__(self, root = None, fileName = None, loadFlag = True, decodeFlag = True):
        if fileName is None:
            fileName = getSetting("collection", None)
        if root is None:
            root = getSetting("root", None)
        assert (fileName is not None) and (root is not None), funcs.errorMessage("{} and {} is invalid for file name and root for a DataCollection".format(fileName, root), loc = "DataCollection.__init__")

        self.filePath = os.path.join(root, fileName)
        self.root = root
        self.fileName = fileName

        self.jsonData = None
        self.data = None
        if loadFlag:
            print('Loading data collection...')
            self.load()
            print('Data collection loading finished.')
            if decodeFlag:
                print('Decoding data collection...')
                self.decode()
                print('Data collection decoding finished.')

    @property
    def dataCount(self):
        if self.data is None:
            return 0
        return len(self.data)

    def decode(self):
        # decode the json data into {DataLabel, describer}
        self.data = []
        for key in self.jsonData:
            setNo, seed = decodeSetSeed(key)
            for port in self.jsonData[key]:
                self.data.append(({'seed': seed, 'setNo': setNo, 'port': port, 'timestamp': int(seed)}, self.jsonData[key][port]))


    def load(self):
        if not os.path.isfile(self.filePath):
            warnings.warn(funcs.warningMessage("JSON file not existing: creating an empty data collection.", loc = 'DataCollection.load'))
            self.jsonData = dict()
            return 
        with open(self.filePath, 'r') as f:
            self.jsonData = json.load(f)
            f.close()

    def save(self, extraRoot = None):
        if self.jsonData is None:
            warnings.warn(funcs.warningMessage("Data collection cannot be saved when json data is not loaded.", loc = "DataCollection.save"))
            return 
        if extraRoot is None:
            path = self.filePath
        else:
            path = os.path.join(extraRoot, self.fileName)
        with open(path, 'w') as f:
            json.dump(self.jsonData, f)
            f.close()

    def checkItem(self, setNo, seed, port):
        if self.jsonData is None:
            return False
        setName = encodeSetSeed(setNo = setNo, seed = seed)
        port = str(port)
        return (setName in self.jsonData) and (port in self.jsonData[setName])

    def appendItem(self, setNo, seed, port, describer):
        if self.jsonData is not None:
            setName = encodeSetSeed(setNo = setNo, seed = seed)
            port = str(port)
            if setName in self.jsonData and port in self.jsonData[setName]:
                return False
            if not setName in self.jsonData:
                self.jsonData[setName] = dict()
            self.jsonData[setName][port] = describer
        
        if self.data is not None:
            self.data.append(({'seed': seed, 'setNo': setNo, 'port': port, 'timestamp': int(seed)}, describer))
        
        return True
    
    def append(self, setNo, **kwargs):
        if isinstance(setNo, list):
            for singleSet in setNo:
                self.append(singleSet)
            return 

        setNo = str(setNo)
        print('appending data set {}'.format(setNo))
        seedList = []

        # files will be in root/test{setNo}
        setRoot = os.path.join(self.root, 'test' + setNo)
        for fileName in os.listdir(setRoot):
            if fileName.isdigit():
                seedList.append(fileName)

        for seed in seedList:
            port = 0
            while (True):
                paraFile = os.path.join(setRoot, seed, 'para{}-{}.dat'.format(seed, port))
                dataFile = os.path.join(setRoot, seed, 'data{}-{}.dat'.format(seed, port))
                # print('paraFile = {}, dataFile = {}'.format(paraFile, dataFile))
                if (not os.path.isfile(paraFile)) or (not os.path.isfile(dataFile)):
                    break

                if self.checkItem(setNo, seed, port):
                    port += 1
                    continue
                dataSet = DataSet(DataLabel(seed, port, setNo), **kwargs)
                self.appendItem(setNo, seed, port, dataSet.getDescriber())

                dataSet.saveToNpzFiles()
                port += 1

    def filter(self, numFilter = None, desFilter = None):
        res = self.data
        if numFilter is not None:
            res = [x for x in res if numFilter(x[0])]
        if desFilter is not None:
            res = [x for x in res if desFilter(x[1])]
        return res

        
        

        

        