def settingDecoder(data):
    # data can be: 
    # raw string
    # list of strings
    data = data.strip()
    if (len(data) > 1) and (data[0] == '[') and (data[-1] == ']'):
        data = [x.strip() for x in data[1:-1].split(',')]
    return data
def loadSetting(filename = "SETTINGS"):
    res = dict()
    with open(filename, 'r') as f:
        for line in f:
            sline = line.strip()
            if sline.startswith('#'):
                continue
            if sline.find('=') != -1:
                eIdx = sline.find('=')
                res[line[:eIdx]] = settingDecoder(sline[(eIdx + 1):])

    return res

settings = loadSetting()

def getSetting(key, value = None):
    if key in settings:
        return settings[key]
    else:
        return value

if __name__ == '__main__':
    print(loadSetting())