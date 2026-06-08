import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
from shapely.geometry import LineString, Point

import test
import Interpolations


DEFAULT_METHODS = ['linear', 'quadratic', 'cubicspline', 'quartic', 'quintic', 'pchip', 'akima']


def _workerInit():
    import matplotlib
    matplotlib.use('Agg')



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
    start, side, leftCERPMs, rightCERPMs, clusterSize, nOut, true_x, true_y, methods = args

    if side == 0:
        dropping = set(range(start, min(start + clusterSize, len(leftCERPMs))))
        leftSurv  = [c for i, c in enumerate(leftCERPMs) if i not in dropping]
        rightSurv = list(rightCERPMs)
    else:
        dropping  = set(range(start, min(start + clusterSize, len(rightCERPMs))))
        leftSurv  = list(leftCERPMs)
        rightSurv = [c for i, c in enumerate(rightCERPMs) if i not in dropping]

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

    rng = np.random.SeedSequence(baseSeed)
    runSeeds = [int(s.generate_state(1)[0]) for s in rng.spawn(nRuns)]

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
        return {m: {'mean': np.full(1, np.nan), 'max': np.full(1, np.nan)} for m in methods}

    # Enumerate every valid cluster start position on each side — no repetition possible.
    # side=0: drop from left way; side=1: drop from right way.
    args_list = [
        (start, side, leftCERPMs, rightCERPMs, clusterSize, nOut, true_x, true_y, methods)
        for side, cerpms in ((0, leftCERPMs), (1, rightCERPMs))
        for start in range(len(cerpms) - clusterSize + 1)
    ]
    nTrials = len(args_list)

    print(f"Clustered (size={clusterSize}) - {nTrials} unique positions ({len(methods)} methods)...")
    trial_results = [None] * nTrials
    with ProcessPoolExecutor(max_workers=maxWorkers, initializer=_workerInit) as executor:
        futures = {executor.submit(_runClusteredTrial, args): i for i, args in enumerate(args_list)}
        done = 0
        reportEvery = max(1, nTrials // 10)
        for future in as_completed(futures):
            i = futures[future]
            trial_results[i] = future.result()
            done += 1
            if done % reportEvery == 0:
                print(f"  {done}/{nTrials}")

    print("Done.\n")
    return _collectResults(trial_results, methods)


def runMonteCarloGapLength(leftWay, rightWay, nRuns=500, cerpmInterval=1.0, gapLength=5.0,
                            methods=None, baseSeed=0, maxWorkers=None):
    if methods is None:
        methods = DEFAULT_METHODS
    methods = list(methods)

    true_x, true_y = test.calCenterline(leftWay, rightWay)
    leftCERPMs = test.resample(leftWay, cerpmInterval)
    rightCERPMs = test.resample(rightWay, cerpmInterval)
    nOut = len(true_x)

    clusterSize = max(1, round(gapLength / cerpmInterval))

    if clusterSize >= len(leftCERPMs) or clusterSize >= len(rightCERPMs):
        print(f"Gap length (gap={gapLength}m -> {clusterSize} markers) - exceeds road length, all trials N/A.")
        return {m: {'mean': np.full(1, np.nan), 'max': np.full(1, np.nan)} for m in methods}

    args_list = [
        (start, side, leftCERPMs, rightCERPMs, clusterSize, nOut, true_x, true_y, methods)
        for side, cerpms in ((0, leftCERPMs), (1, rightCERPMs))
        for start in range(len(cerpms) - clusterSize + 1)
    ]
    nTrials = len(args_list)

    print(f"Gap length (gap={gapLength}m -> {clusterSize} markers) - {nTrials} positions ({len(methods)} methods)...")
    trial_results = [None] * nTrials
    with ProcessPoolExecutor(max_workers=maxWorkers, initializer=_workerInit) as executor:
        futures = {executor.submit(_runClusteredTrial, args): i for i, args in enumerate(args_list)}
        done = 0
        reportEvery = max(1, nTrials // 10)
        for future in as_completed(futures):
            i = futures[future]
            trial_results[i] = future.result()
            done += 1
            if done % reportEvery == 0:
                print(f"  {done}/{nTrials}")

    print("Done.\n")
    return _collectResults(trial_results, methods)