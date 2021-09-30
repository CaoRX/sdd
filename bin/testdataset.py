import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(os.path.join(parentdir, 'src'))

import matplotlib.pyplot as plt

from qdmdealer.dataloading.datalabel import DataLabel
from qdmdealer.dataloading.dataset import DataSet 
import qdmdealer.dataloading.dataprocessor as dataProcessor

from qdmdealer.dataloading.parameterset import ParameterSet

# our goal:
# given a parameterset, options
# load the data with given parameter set

if __name__ == '__main__':
    dl = DataLabel(setNo = 1630683685, seed = 1630822089, port = 0)
    ds = DataSet(dataLabel = dl, fromRawData = False, obsDataOnly = False, dataProcessors = [dataProcessor.binProcessor])
    # print(ds)
    # print(ds.data.keys())
    # print(ds.obs.keys())
    # print(ds.obs)
    print('para keys: {}'.format(ds.para.keys()))
    print(ds.para)
    print('describer = {}'.format(ds.getDescriber()))

    # plt.imshow(ds.data['psi int hist int2DHist'])
    # plt.show()

    ps = ParameterSet()
    ps.appendPara("T", typeName = "fvalue", value = 0.6)
    ps.appendPara("V", typeName = "fset", value = [-0.5, 0.5])
    ps.appendPara("wn", typeName = "set", value = [[-1, 0], [0, 0]])

    paraFilter = ps.generateFilter()
    print(paraFilter(ds.getDescriber()))
    print('data keys = {}'.format(ds.data.keys()))

