import qdmdealer.funcs.funcs as funcs
import warnings

parameterEPS = 1e-7

class ParameterSet:

    def __init__(self):
        self.para = dict()
    
    def appendPara(self, name, typeName, value, exclude = False):
        if name in self.para:
            warnings.warn(funcs.warningMessage('para {} has already existed, overwritting {} to {}'.format(name, self.para[name]['value'], value), loc = 'ParameterSet.__init__'))
        
        self.para[name] = {'type': typeName, 'value': value, 'exclude': exclude}

    def generateFilter(self):
        # make a filter of describers according to this parameter set
        # typeName: value, set, range

        filters = []
        validTypeNames = ['value', 'fvalue', 'set', 'fset', 'range']
        for key in self.para:
            typeName = self.para[key]['type']
            value = self.para[key]['value']
            exclude = self.para[key]['exclude']
            # print('processing {}, {}, {}'.format(key, value, typeName))

            if not typeName in validTypeNames:
                warnings.warn(funcs.warningMessage('para type name {} is not valid: should be one of {}'.format(typeName, validTypeNames), loc = 'ParameterSet.generateFilter'))

            if typeName == 'value':
                def makeClosure(key, value, typeName, exclude):
                    def filter(x):
                        return x[key] == value
                    return filter

                filters.append(funcs.makeFilter(makeClosure(key, value, typeName, exclude), key, exclude))
            elif typeName == 'fvalue':
                def makeClosure(key, value, typeName, exclude):
                    def filter(x):
                        # print(key, value)
                        return funcs.floatEqual(x[key], value, eps = parameterEPS)
                    return filter
                # print(key, typeName, value, exclude)
                filters.append(funcs.makeFilter(makeClosure(key, value, typeName, exclude), key, exclude))
            elif typeName == 'set':
                def makeClosure(key, value, typeName, exclude):
                    def filter(x):
                        return x[key] in value
                    return filter
                filters.append(funcs.makeFilter(makeClosure(key, value, typeName, exclude), key, exclude))
            elif typeName == 'fset':
                def makeClosure(key, value, typeName, exclude):
                    def filter(x):
                        for y in value:
                            if funcs.floatEqual(x[key], y, eps = parameterEPS):
                                return True
                        return False
                    return filter

                filters.append(funcs.makeFilter(makeClosure(key, value, typeName, exclude), key, exclude))
            elif typeName == 'range':
                def makeClosure(key, value, typeName, exclude):
                    def filter(x):
                        if value[0] is not None and x[key] < value[0] - parameterEPS:
                            return False
                        if value[1] is not None and x[key] > value[1] + parameterEPS:
                            return False
                        return True
                    return filter
                filters.append(funcs.makeFilter(makeClosure(key, value, typeName, exclude), key, exclude))

        return funcs.allFilter(filters)

    def __repr__(self):
        return 'ParameterSet(para = {})'.format(self.para)