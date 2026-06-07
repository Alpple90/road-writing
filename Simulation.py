import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
from shapely.geometry import LineString, Point

import test
import Interpolations


DEFAULT_METHODS = ['linear', 'quadratic', 'cubicspline', 'quartic', 'quintic', 'pchip', 'akima']


def _workerInit():
    import matplotlib
    matplotlib.use('Agg')


def clusterDropout(cerpms, clusterSize, rng):
    n = len(cerpms)
    if n == 0 or clusterSize <= 0:
        return list(cerpms)
    start = rng.integers(0, n)
    dropping = {start + i for i in range(clusterSize) if start + i < n}
    return [c for i, c in enumerate(cerpms) if i not in dropping]


def measureError(estimatedPts, true_x, true_y):
    trueLine = LineString(list(zip(true_x, true_y)))
    errors = [trueLine.distance(Point(p)) for p in estimatedPts]
    return float(np.mean(errors)), float(np.max(errors))


def _runRandomTrial(args):
    seed, leftCERPMs, rightCERPMs, dropoutRate, nOut, true_x, true_y, methods = args
    crng = np.random.default_rng(seed)

    nLeft = len(leftCERPMs)
    nTotal = nLeft + len(rightCERPMs)
    mask = crng.random(nTotal) >= dropoutRate

    leftSurv = [c for c, keep in zip(leftCERPMs, mask[:nLeft]) if keep]
    rightSurv = [c for c, keep in zip(rightCERPMs, mask[nLeft:]) if keep]

    nan_result = {m: (np.nan, np.nan) for m in methods}
    if len(leftSurv) < 2 or len(rightSurv) < 2:
        return nan_result

    out = {}
    for m in methods:
        try:
            leftRecon = Interpolations.interpolate(leftSurv, nOut, m)
            rightRecon = Interpolations.interpolate(rightSurv, nOut, m)

            pts = np.array(leftRecon + rightRecon)
            if not np.isfinite(pts).all():
                raise ValueError("non-finite reconstruction")

            c_x, c_y = test.calCenterline(leftRecon, rightRecon)
            mean_err, max_err = measureError(list(zip(c_x, c_y)), true_x, true_y)
            out[m] = (mean_err, max_err)
        except Exception:
            out[m] = (np.nan, np.nan)
    return out


def _runClusteredTrial(args):
    seed, leftCERPMs, rightCERPMs, clusterSize, nOut, true_x, true_y, methods = args
    crng = np.random.default_rng(seed)
    dropSeed, sideSeed = crng.integers(0, 2**31, 2)

    if np.random.default_rng(int(sideSeed)).integers(0, 2) == 0:
        leftSurv = clusterDropout(leftCERPMs, clusterSize, np.random.default_rng(int(dropSeed)))
        rightSurv = list(rightCERPMs)
    else:
        leftSurv = list(leftCERPMs)
        rightSurv = clusterDropout(rightCERPMs, clusterSize, np.random.default_rng(int(dropSeed)))

    nan_result = {m: (np.nan, np.nan) for m in methods}
    if len(leftSurv) < 2 or len(rightSurv) < 2:
        return nan_result

    out = {}
    for m in methods:
        try:
            leftRecon = Interpolations.interpolate(leftSurv, nOut, m)
            rightRecon = Interpolations.interpolate(rightSurv, nOut, m)

            pts = np.array(leftRecon + rightRecon)
            if not np.isfinite(pts).all():
                raise ValueError("non-finite reconstruction")

            c_x, c_y = test.calCenterline(leftRecon, rightRecon)
            mean_err, max_err = measureError(list(zip(c_x, c_y)), true_x, true_y)
            out[m] = (mean_err, max_err)
        except Exception:
            out[m] = (np.nan, np.nan)
    return out


def _collectResults(trial_results, methods):
    results = {m: {'mean': [], 'max': []} for m in methods}
    for trial in trial_results:
        for m in methods:
            mean_err, max_err = trial[m]
            results[m]['mean'].append(mean_err)
            results[m]['max'].append(max_err)
    for m in methods:
        results[m]['mean'] = np.array(results[m]['mean'])
        results[m]['max'] = np.array(results[m]['max'])
    return results


def runMonteCarloRandom(leftWay, rightWay, nRuns=500, cerpmInterval=1.0, dropoutRate=0.1,
                        methods=None, baseSeed=0, maxWorkers=None):
    if methods is None:
        methods = DEFAULT_METHODS
    methods = list(methods)

    true_x, true_y = test.calCenterline(leftWay, rightWay)
    leftCERPMs = test.resample(leftWay, cerpmInterval)
    rightCERPMs = test.resample(rightWay, cerpmInterval)
    nOut = len(true_x)

    rng = np.random.default_rng(baseSeed)
    runSeeds = [int(s) for s in rng.integers(0, 2**31, nRuns)]

    args_list = [
        (runSeeds[i], leftCERPMs, rightCERPMs, dropoutRate, nOut, true_x, true_y, methods)
        for i in range(nRuns)
    ]

    print(f"Random (rate={dropoutRate}) - {nRuns} trials ({len(methods)} methods)...")
    trial_results = [None] * nRuns
    with ProcessPoolExecutor(max_workers=maxWorkers, initializer=_workerInit) as executor:
        futures = {executor.submit(_runRandomTrial, args): i for i, args in enumerate(args_list)}
        done = 0
        reportEvery = max(1, nRuns // 10)
        for future in as_completed(futures):
            i = futures[future]
            trial_results[i] = future.result()
            done += 1
            if done % reportEvery == 0:
                print(f"  {done}/{nRuns}")

    print("Done.\n")
    return _collectResults(trial_results, methods)


def runMonteCarloClusteredSingle(leftWay, rightWay, nRuns=500, cerpmInterval=1.0, clusterSize=5,
                                  methods=None, baseSeed=0, maxWorkers=None):
    if methods is None:
        methods = DEFAULT_METHODS
    methods = list(methods)

    true_x, true_y = test.calCenterline(leftWay, rightWay)
    leftCERPMs = test.resample(leftWay, cerpmInterval)
    rightCERPMs = test.resample(rightWay, cerpmInterval)
    nOut = len(true_x)

    if clusterSize >= len(leftCERPMs) or clusterSize >= len(rightCERPMs):
        print(f"Clustered (size={clusterSize}) - cluster exceeds road length, all trials N/A.")
        return {m: {'mean': np.full(nRuns, np.nan), 'max': np.full(nRuns, np.nan)} for m in methods}

    rng = np.random.default_rng(baseSeed)
    runSeeds = [int(s) for s in rng.integers(0, 2**31, nRuns)]

    args_list = [
        (runSeeds[i], leftCERPMs, rightCERPMs, clusterSize, nOut, true_x, true_y, methods)
        for i in range(nRuns)
    ]

    print(f"Clustered (size={clusterSize}) - {nRuns} trials ({len(methods)} methods)...")
    trial_results = [None] * nRuns
    with ProcessPoolExecutor(max_workers=maxWorkers, initializer=_workerInit) as executor:
        futures = {executor.submit(_runClusteredTrial, args): i for i, args in enumerate(args_list)}
        done = 0
        reportEvery = max(1, nRuns // 10)
        for future in as_completed(futures):
            i = futures[future]
            trial_results[i] = future.result()
            done += 1
            if done % reportEvery == 0:
                print(f"  {done}/{nRuns}")

    print("Done.\n")
    return _collectResults(trial_results, methods)