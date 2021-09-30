class DataLabel:

    def __init__(self, seed, port, setNo = None):
        self.setNo = setNo
        self.seed = seed 
        self.port = port

    def seedStr(self):
        if self.setNo is None:
            return str(self.seed)
        else:
            return '{}-{}'.format(self.setNo, self.seed)

def decodeSetSeed(s):
    idx = s.find('-')
    if idx == -1:
        return None, s
    else:
        return s[:idx], s[(idx + 1):]
def encodeSetSeed(setNo, seed):
    if setNo is None:
        return str(seed)
    else:
        return str(setNo) + '-' + str(seed)