import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(os.path.join(parentdir, 'src'))

from qdmdealer.dataloading.datacollection import DataCollection, defaultLoadingOptions

# workflow:
# 1. load DataCollection(~1s)
# 2. for new data: append
# 3. for plot: make a ParameterSet
# 4. then filter the dataSet with ParameterSet(and timestamp filters)
# 5. obtain datasets
# 6. obtain data
# 7. plot

if __name__ == '__main__':
    dc = DataCollection()
    # print(dc.jsonData)

    # extraRoot = "/Users/akks_npc/Desktop/git-folder/qdm-dealer/data/"
    # dc.save(extraRoot = extraRoot)

    print(dc.data[:10])

    options = defaultLoadingOptions
    options['denseFilters'] = [lambda x: x.find('series') != -1, lambda x: x.find('int2DHist') != -1]

    dc.append(1631464238, **options)
    dc.save()

    print('{} datasets.'.format(dc.dataCount))