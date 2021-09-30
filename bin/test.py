import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(os.path.join(parentdir, 'src'))

from qdmdealer.settingLoader import loadSetting

# data filter: T, V, L, N, m, b, mu, wf

def testDataBuffer():
    import qdmdealer.dataloading.binarydatabuffer as databuffer
    import os
    settings = loadSetting()

    filename = "test1631464238/1631496683/para1631496683-6.dat"
    # filename = "para1631496683-6.dat"
    localDataFolder = "/Users/akks_npc/Desktop/git-folder/qdm-dealer/data"

    absFilename = os.path.join(settings['root'], filename)
    # absFilename = os.path.join(localDataFolder, filename)
    print(absFilename)

    if os.path.isfile(absFilename):
        fileContent = databuffer.loadParaFile(absFilename)
        print(fileContent)

if __name__ == '__main__':
    print(loadSetting())
    testDataBuffer()