import numpy as np 
import time
import struct
import qdmdealer.funcs.funcs as funcs

class BinaryDataBuffer:

    def __init__(self, data):
        self.data = data
        self.sizeOfSizeType = 8
    def getBytes(self, byteN):
        res = self.data[:byteN]
        self.data = self.data[byteN:]
        return res
    def getDataElement(self, dataType, dataSize):
        # dataType should in 'i', 'q', 'd'
        return struct.unpack(dataType, self.getBytes(dataSize))[0]

    def getSizeType(self):
        size = struct.unpack('q', self.getBytes(self.sizeOfSizeType))[0]
        return size

    def getStr(self):
        length = self.getSizeType()
        strValue = self.getBytes(length)
        return length, strValue.decode('ascii')

    def empty(self):
        return (len(self.data) <= 0)

    def getData(self, dataSize):
        # here we only have int and double types
        # so dataSize == 4 means int, while dataSize == 8 means double
        if (dataSize == 4):
            dataType = 'i'
        else:
            dataType = 'd'
        return self.getDataElement(dataType, dataSize)

    def getParameter(self):
        _, paraName = self.getStr()
        valueLength = self.getSizeType()
        if (valueLength == 1): # string value
            _, value = self.getStr()
        else:
            value = self.getData(valueLength)

        return (paraName, value)

    def getArray(self, shape, dataSize):
        totalSize = funcs.sizeOfShape(shape)
        # print('getArray(shape = {}, dataSize = {})'.format(shape, dataSize))
        assert ((dataSize == 4) or (dataSize == 8)), "Error: data size can only be 4(int) or 8(double) in BinaryDataBuffer.getArray."
        if (dataSize == 4):
            dataType = np.int32 
        elif (dataSize == 8): 
            dataType = np.float64

        dataTotalByteN = totalSize * dataSize
        # print('dataSize = {}, totalSize = {}'.format(dataSize, totalSize))
        # print(len(self.data))
        
        res = np.frombuffer(self.getBytes(dataTotalByteN), dtype = dataType)
        res = np.reshape(res, shape)
        return res

    def getDataTerm(self):
        _, dataName = self.getStr()
        # print('dataName = {}'.format(dataName))
        dataSize = self.getSizeType()
        if (funcs.isTimeObsName(dataName)):
            pass
            # print('Be careful: this patch of time has been removed, and for older data please modify BinaryDataBuffer.getDataTerm() function in binarydatabuffer.py')
            # print("Be careful: here is a patch for several data sets and will be deprecated soon.")
            # data = self.getData(dataSize = dataSize)
            # return (dataName, data)
        dim = self.getData(dataSize = 4)
        # print('dataName = {}'.format(dataName))
        # print('dim = {}'.format(dim))
        shape = []
        for _ in range(dim):
            shape.append(self.getSizeType())
        if (dim == 0):
            shape = (1, )
        else:
            shape = tuple(shape)

        data = self.getArray(shape, dataSize)
        return (dataName, data)

def loadParaFile(paraFileName): # return a dict object, includes (paraName, paraValue) pairs
    # TODO: at timestamp 1588851367, the para part has been updated to be the same as data part
    # so we need to update the way for loading the para file
    paraFile = open(paraFileName, mode = 'rb')
    paraDataBuffer = BinaryDataBuffer(paraFile.read())
    paraFunc = paraDataBuffer.getParameter
    paraFileContent = dict([])
    while (not paraDataBuffer.empty()):
        paraName, paraValue = paraFunc()
        # print('{} = {}'.format(paraName, paraValue))
        paraFileContent[paraName] = paraValue
    return paraFileContent

def loadDataFile(dataFileName): # return a dict object, includes (dataName, dataValue) pairs
    dataFile = open(dataFileName, mode = 'rb')
    dataBuffer = BinaryDataBuffer(dataFile.read())
    dataFileContent = dict([])

    while (not dataBuffer.empty()):
        # print('remain data = {}'.format(len(dataBuffer.data)))
        dataName, dataValue = dataBuffer.getDataTerm()
        # print('dataName = {}'.format(dataName))
        dataFileContent[dataName] = dataValue
    
    return dataFileContent

if __name__ == '__main__':
    from qdmdealer.settingLoader import loadSetting
    import os
    settings = loadSetting()

    filename = "test1631464238/1631496683/para1631496683-6.dat"

    absFilename = os.path.join(settings['root'], filename)
    print(absFilename)
