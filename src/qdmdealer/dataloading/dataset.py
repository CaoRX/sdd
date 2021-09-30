# load from .npz file
# load from .dat file, and save to .npz

import qdmdealer.funcs.funcs as funcs
from qdmdealer.dataloading.datalabel import DataLabel
import os
import warnings

import numpy as np 
import json
import qdmdealer.dataloading.binarydatabuffer as binarydatabuffer
import qdmdealer.dataloading.dataprocessor as dataProcessor
from qdmdealer.settingLoader import loadSetting

# dataset should contain
# para, obs, data, dense
# data can be None: then only para and obs is useful

# the data: setNo, seed, port

# make it free from QDM!

defaultSetting = loadSetting()
defaultRoot = defaultSetting.get('root', None)
defaultDesKeys = defaultSetting.get('deskeys', [])
defaultDesNames = defaultSetting.get('desnames', [])
class DataSet:

    def decodeOptions(self, **kwargs):
        # what options do we need?
        # fromRawData: from .dat files, otherwise from .npz files
        # obsDataOnly: do not load from data files, only from obs
        # removeOriginalData: whether to remove original data after loading and saving to npz files or not
        # discardFuncs: discard a piece of data from the name of data, a function that accept a string and return a boolean
        # rootFolder: the "data" folder

        self.fromRawData = kwargs.get('fromRawData', False)
        self.obsDataOnly = kwargs.get('obsDataOnly', True)
        self.loadDenseData = kwargs.get('loadDenseData', False)
        self.removeOriginalData = kwargs.get('removeOriginalData', False)
        self.discardFuncs = kwargs.get('discardFuncs', lambda x: False)
        self.rootFolder = kwargs.get('rootFolder', defaultRoot)
        self.dataProcessors = kwargs.get('dataProcessors', [])
        self.denseFilters = kwargs.get('denseFilters', [])
        self.denseFilter = funcs.anyFilter(self.denseFilters)
        
        self.desKeys = kwargs.get('desKeys', defaultDesKeys)
        self.desNames = kwargs.get('desNames', defaultDesNames)

        assert len(self.desKeys) == len(self.desNames), funcs.errorMessage("Number of describer keys must equal to No. of describer names, {} and {} obtained.".format(len(self.desKeys), len(self.desNames)))
        self.forceUpdateObs = kwargs.get('forceUpdateObs', False)

    @property
    def processorNames(self):
        return [dp.name for dp in self.dataProcessors]

    @property
    def dataSetLabel(self):
        return self.dataLabel.seedStr() + '-' + str(self.dataLabel.port)

    def getDescriber(self):
        if self.describer is not None:
            return self.describer
        self.describer = dict()
        for key, name in zip(self.desKeys, self.desNames):
            if name in self.para:
                self.describer[key] = self.para[name]
        return self.describer
    
    def __init__(self, dataLabel, **kwargs):
        self.decodeOptions(**kwargs)

        self.data = None
        self.para = None
        self.dense = None
        self.obs = dict([])
        self.describer = None
        self.dataLabel = dataLabel

        self.generateFileNames()
        self.process()

    def appendDataProcessor(self, dp):
        assert not (dp.name in self.processorNames), funcs.errorMessage(message = '{} is already in processors'.format(dp.name))
        # assert not (dp.name in self.obs), funcs.errorMessage(message = '{} is already in obs: {}'.format(dp.name, self.obs.keys()))
        self.dataProcessors.append(dp)
    
    def applyDataProcessors(self, force = False):
        for dp in self.dataProcessors:
            try:
                newObsData = dp.func(**{'obs': self.obs, 'data': self.data, 'para': self.para, 'dense': self.dense})
                # print('obs data = {}'.format(newObsData))
                for key in newObsData:
                    if (key not in self.obs) or force:
                        self.obs[key] = newObsData[key]
            except:
                warnings.warn(message = funcs.warningMessage(message = 'error in calculating data processor {}'.format(dp.name)))
            # if (not force) and (dp.name in self.obs):
            #     continue
            # try:
            #     self.obs[dp.name] = dp.funcs(self.data, self.para)
            # except:
            #     warnings.warn(message = funcs.warningMessage(message = 'error in calculating obs {}'.format(dp.name)))

    def generateFileNames(self):
        self.files = dict()

        # npz files: located at rootFolder/npzfiles/dataLabel.data()['seed']/dataLabel.data()['port']
        # dat files: located at rootFolder/dataLabel.data()['seed']/xxx{seed}-{port}.dat
        seed, port = self.dataLabel.seed, self.dataLabel.port
        seedStr = self.dataLabel.seedStr()
        portStr = str(port)
        
        npzFolder = os.path.join(self.rootFolder, 'npzfiles', seedStr, portStr)
        
        npzToSeed = os.path.join(self.rootFolder, 'npzfiles', seedStr)
        npzToPort = os.path.join(npzToSeed, portStr)

        if not os.path.isdir(npzToSeed):
            os.mkdir(npzToSeed)
        if not os.path.isdir(npzToPort):
            os.mkdir(npzToPort)

        self.npzFileTypes = ['data', 'para', 'obs']

        filenameDict = {'npz data': 'data.npz', 'npz dense': 'dense.npz', 'npz para': 'para.json', 'npz obs': 'obs.npz'}
        for key in filenameDict:
            self.files[key] = os.path.join(npzFolder, filenameDict[key])

        rawFolder = os.path.join(self.rootFolder, 'test' + str(self.dataLabel.setNo), str(seed))

        rawSuffix = '{}-{}.dat'.format(seed, port)
        
        self.rawFileTypes = ['stdout', 'para', 'data']
        for rawFile in self.rawFileTypes:
            self.files['raw {}'.format(rawFile)] = os.path.join(rawFolder, rawFile + rawSuffix)

    def isRawFilesExist(self):
        for rawFile in self.rawFileTypes:
            file = self.files['raw {}'.format(rawFile)]
            if not os.path.isfile(file):
                return False
        return True

    def isNpzFilesExist(self):
        for npzFile in self.npzFileTypes:
            file = self.files['npz {}'.format(npzFile)]
            if not os.path.isfile(file):
                return False
        return True

    def discardDataItems(self):
        dataKeys = list(self.data.keys())
        for key in dataKeys:
            if self.discardFuncs(key):
                del self.data[key]
        if self.loadDenseData:
            for key in list(self.dense.keys()):
                if self.discardFuncs(key):
                    del self.dense[key]

    def process(self):
        # load data, para, obs from dat files
        # process obs
        # save to npz files
        # (optional) remove raw data files
        # labels: 

        # fromRawData: from .dat files, otherwise from .npz files
        # obsDataOnly: do not load from data files, only from obs
        # removeOriginalData: whether to remove original data after loading and saving to npz files or not
        # discardFuncs: discard a piece of data from the name of data, a function that accept a string and return a boolean

        if self.fromRawData:
            # load raw data
            # generate obs
            data = binarydatabuffer.loadDataFile(self.files['raw data'])
            self.data = dict()
            self.dense = dict()
            for key in data:
                if self.denseFilter(key):
                    # then this key is belonging to dense data
                    self.dense[key] = data[key]
                else:
                    self.data[key] = data[key]
            
            self.para = binarydatabuffer.loadParaFile(self.files['raw para'])

            self.discardDataItems()
            self.obs = dict()
            self.applyDataProcessors(force = True)

            self.saveToNpzFiles()
            if self.removeOriginalData:
                self.removeOriginalDataFile()
            return
        
        else:
            with open(self.files['npz para'], 'r') as paraFile:
                self.para = json.load(paraFile)
            self.obs = funcs.loadNpzFile(self.files['npz obs'])
            if not self.obsDataOnly:
                self.data = funcs.loadNpzFile(self.files['npz data'])
                if self.loadDenseData:
                    self.dense = funcs.loadNpzFile(self.files['npz dense'])
                self.discardDataItems()
                self.applyDataProcessors(force = self.forceUpdateObs)
                self.saveToNpzObsFile()

    def saveToNpzFiles(self):
        assert (self.data is not None), funcs.errorMessage(message = 'npz data is None in {}'.format(self.dataSetLabel))
        assert (self.para is not None), funcs.errorMessage(message = 'npz para is None in {}'.format(self.dataSetLabel))

        if self.data is not None:
            np.savez(self.files['npz data'], **self.data)
        if self.obs is not None:
            np.savez(self.files['npz obs'], **self.obs)
        if self.dense is not None:
            np.savez(self.files['npz dense'], **self.dense)
        with open(self.files['npz para'], 'w') as paraFile:
            json.dump(self.para, paraFile)
            paraFile.close()

    def saveToNpzObsFile(self):
        assert (self.obs is not None), funcs.errorMessage(message = 'npz obs is None in {}'.format(self.dataSetLabel))
        np.savez(self.files['npz obs'], **self.obs)

    def removeOriginalDataFile(self):
        command = 'rm {}'.format(self.files['raw data'])
        os.system(command)

    def __repr__(self):
        paraStr = 'para: {}'.format(self.para)
        dataShapeDict = dict([])
        if (self.data is not None):
            for key in self.data:
                dataShapeDict[key] = self.data[key].shape
        dataStr = 'data: {}'.format(dataShapeDict)
        return paraStr + ', ' + dataStr