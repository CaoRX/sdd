import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(os.path.join(parentdir, 'src'))

from qdmdealer.dataloading.parameterset import ParameterSet
from qdmdealer.settingLoader import loadSetting, getSetting

from qdmdealer.dataloading.datacollection import DataCollection, defaultLoadingOptions

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
    ps = makeQDMPS(T = {'type': 'range', 'value': (0.71, 0.73)})
    print(ps)

    tsps = makeTimestampPS(1630822146, 1630822148)
    print(tsps)

    dc = DataCollection()
    data = dc.filter(numFilter = tsps.generateFilter(), desFilter = ps.generateFilter())
    print(data)