import numpy as np

def weightedBootstrapEstimateFunctionalByFunc(f, weights, *args):
    print(weights, args)
    n = len(args[0])
    if n == 1:
        print("Error: bootstrap with only 1 dataset, return only average.")
        sampleData = [arg[0] for arg in args]
        res = {'value': f(*sampleData)}
        return res

    weights = np.array(weights) / np.sum(np.array(weights))
    args = [np.array(arg) for arg in args]
    # print(weights, args[0])
    # n = min(len(args[0]), 10000)
    B = 50

    # print('bootstrap n = {}'.format(n))
    # print('bootstrap data = {}'.format(args))

    fDistribution = []
    for loop in range(B):
        print('bootstrap loop = {} / {}'.format(loop + 1, B))
        # bSample = np.random.random_integers(n, size = n) - 1
        bSample = np.random.choice(n, size = n, p = weights)
        # print(bSample)
        sampleData = []
        for arg in args:
            localData = arg[bSample]
            # print('local data = {}'.format(localData))
            # print(localData)
            # for bSampleIdx in bSample:
            # 	# localData.append(arg[bSampleIdx]())
            # 	localData.append(arg[bSampleIdx])
            sampleData.append(np.average(np.array(localData)))
        # sampleData = [np.average(arg[bSample]) for arg in args]
        sampleRes = f(*sampleData)
        # print(sampleData)
        fDistribution.append(sampleRes)

    fDistribution = np.array(fDistribution)

    return {'value': np.average(fDistribution), 'error': np.std(fDistribution) * np.sqrt(n / (n - 1))}