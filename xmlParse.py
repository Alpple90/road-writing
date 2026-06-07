import itertools
import os
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

import test
import Simulation


METHODS = ['linear', 'quadratic', 'cubicspline', 'quartic', 'quintic', 'pchip', 'akima']

METHOD_COLORS = {
    'linear':      'crimson',
    'quadratic':   'darkorange',
    'cubicspline': 'olivedrab',
    'quartic':     'deepskyblue',
    'quintic':     'hotpink',
    'pchip':       'mediumseagreen',
    'akima':       'mediumpurple',
}

DEFAULT_CLUSTER_SIZES = (2, 5, 10, 15, 20)
DEFAULT_DROPOUT_RATES = (0.01, 0.05, 0.1, 0.15, 0.2)


def parseOSM(path):
    tree = ET.parse(path)
    root = tree.getroot()
    nodes = test.getNodes(root)
    ways = test.getWays(root, nodes)
    return test.getLanelets(root, ways)


def _annotateCells(ax, data, fontsize=6, fmt='.4f'):
    for r in range(data.shape[0]):
        for c in range(data.shape[1]):
            val = data[r, c]
            if np.isfinite(val):
                if fmt == 'pct':
                    label = f'{val:.0f}%'
                elif fmt == 'd':
                    label = f'{int(val)}'
                else:
                    label = f'{val:{fmt}}'
                ax.text(c, r, label, ha='center', va='center', fontsize=fontsize, color='black')


def _runSweepRandom(leftWay, rightWay, nRuns, intervals, dropoutRates, baseSeed, failureThreshold=0.2):
    intervals = list(intervals)
    dropoutRates = list(dropoutRates)
    shape = (len(intervals), len(dropoutRates))

    sweepIQR  = {m: np.full(shape, np.nan) for m in METHODS}
    sweepP25  = {m: np.full(shape, np.nan) for m in METHODS}
    sweepP75  = {m: np.full(shape, np.nan) for m in METHODS}
    sweepFail = {m: np.full(shape, np.nan) for m in METHODS}

    combinations = list(itertools.product(intervals, dropoutRates))
    print(f"\nRandom sweep: {len(intervals)} intervals x {len(dropoutRates)} dropout rates = {len(combinations)} combinations\n")

    for idx, (interval, dropoutRate) in enumerate(combinations):
        iRow = intervals.index(interval)
        iCol = dropoutRates.index(dropoutRate)
        print(f"[{idx+1}/{len(combinations)}]  interval={interval}m  dropout={dropoutRate}")

        mcResults = Simulation.runMonteCarloRandom(
            leftWay, rightWay,
            nRuns=nRuns,
            cerpmInterval=interval,
            dropoutRate=dropoutRate,
            methods=METHODS,
            baseSeed=baseSeed + idx,
        )

        for m in METHODS:
            meanArr = mcResults[m]['mean']
            maxArr  = mcResults[m]['max']

            validMean = meanArr[~np.isnan(meanArr)]
            if len(validMean) >= 2:
                p25, p75 = np.percentile(validMean, [25, 75])
                sweepIQR[m][iRow, iCol] = p75 - p25
                sweepP25[m][iRow, iCol] = p25
                sweepP75[m][iRow, iCol] = p75
            # else remains nan

            nTotal = len(maxArr)
            nFail  = int(np.sum(np.isnan(maxArr) | (maxArr > failureThreshold)))
            sweepFail[m][iRow, iCol] = 100.0 * nFail / nTotal if nTotal > 0 else np.nan

    return sweepIQR, sweepP25, sweepP75, sweepFail


def _runSweepClustered(leftWay, rightWay, nRuns, intervals, clusterSizes, baseSeed, failureThreshold=0.2):
    intervals    = list(intervals)
    clusterSizes = list(clusterSizes)
    shape = (len(intervals),)

    sweepIQR  = {cs: {m: np.full(shape, np.nan) for m in METHODS} for cs in clusterSizes}
    sweepP25  = {cs: {m: np.full(shape, np.nan) for m in METHODS} for cs in clusterSizes}
    sweepP75  = {cs: {m: np.full(shape, np.nan) for m in METHODS} for cs in clusterSizes}
    sweepFail = {cs: {m: np.full(shape, np.nan) for m in METHODS} for cs in clusterSizes}

    combinations = list(itertools.product(intervals, clusterSizes))
    print(f"\nClustered sweep: {len(intervals)} intervals x {len(clusterSizes)} cluster sizes = {len(combinations)} combinations\n")

    for idx, (interval, cs) in enumerate(combinations):
        iRow = intervals.index(interval)
        print(f"[{idx+1}/{len(combinations)}]  interval={interval}m  clusterSize={cs}")

        mcResults = Simulation.runMonteCarloClusteredSingle(
            leftWay, rightWay,
            nRuns=nRuns,
            cerpmInterval=interval,
            clusterSize=cs,
            methods=METHODS,
            baseSeed=baseSeed + idx,
        )

        for m in METHODS:
            meanArr = mcResults[m]['mean']
            maxArr  = mcResults[m]['max']

            validMean = meanArr[~np.isnan(meanArr)]
            if len(validMean) >= 2:
                p25, p75 = np.percentile(validMean, [25, 75])
                sweepIQR[cs][m][iRow] = p75 - p25
                sweepP25[cs][m][iRow] = p25
                sweepP75[cs][m][iRow] = p75
            # else remains nan

            nTotal = len(maxArr)
            nFail  = int(np.sum(np.isnan(maxArr) | (maxArr > failureThreshold)))
            sweepFail[cs][m][iRow] = 100.0 * nFail / nTotal if nTotal > 0 else np.nan

    return sweepIQR, sweepP25, sweepP75, sweepFail


def plotRandomIQRHeatmap(sweepP25, sweepP75, intervals, dropoutRates, nRuns=None):
    intervals    = list(intervals)
    dropoutRates = list(dropoutRates)
    dropoutLabels  = [f'{int(r*100)}%' for r in dropoutRates]
    intervalLabels = [f'{v}m' for v in intervals]

    allIQR = [sweepP75[m] - sweepP25[m] for m in METHODS]
    vmax = float(np.nanmax(allIQR)) if any(np.isfinite(a).any() for a in allIQR) else 1.0

    fig, axes = plt.subplots(1, len(METHODS), figsize=(6 * len(METHODS), 7))

    for col, m in enumerate(METHODS):
        ax   = axes[col]
        p25  = sweepP25[m]
        p75  = sweepP75[m]
        iqr  = p75 - p25
        ax.imshow(iqr, aspect='auto', cmap='RdYlGn_r', vmin=0, vmax=vmax)
        ax.set_xticks(range(len(dropoutRates)))
        ax.set_xticklabels(dropoutLabels, rotation=45, ha='right', fontsize=7)
        ax.set_yticks(range(len(intervals)))
        ax.set_yticklabels(intervalLabels if col == 0 else [], fontsize=7)
        ax.set_xlabel('Dropout rate', fontsize=7)
        if col == 0:
            ax.set_ylabel('CERPM interval', fontsize=7)
        ax.set_title(m, fontsize=9, fontweight='bold')
        for r in range(len(intervals)):
            for c in range(len(dropoutRates)):
                v25 = p25[r, c]
                v75 = p75[r, c]
                if np.isfinite(v25) and np.isfinite(v75):
                    med = (v25 + v75) / 2.0
                    ax.text(c, r, f'{med:.3f}\n(IQR {v25:.3f} - {v75:.3f})',
                            ha='center', va='center', fontsize=6, color='black')

    title = 'Random dropout - IQR centreline error (P25 - P75) (m)'
    if nRuns:
        title += f'  n={nRuns} runs each'
    fig.suptitle(title, fontsize=11, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show(block=False)


def plotClusteredIQRHeatmap(sweepP25, sweepP75, intervals, clusterSizes=None, nRuns=None):
    intervals    = list(intervals)
    clusterSizes = list(clusterSizes if clusterSizes is not None else sweepP25.keys())
    nI  = len(intervals)
    nCS = len(clusterSizes)
    nM  = len(METHODS)

    allIQR = [sweepP75[cs][m] - sweepP25[cs][m] for cs in clusterSizes for m in METHODS]
    vmax = float(np.nanmax(allIQR)) if any(np.isfinite(a).any() for a in allIQR) else 1.0

    cellH  = 0.75
    gapH   = 0.2
    titleH = 0.4
    figH   = titleH + nCS * (nI * cellH + gapH)
    figW   = nM * 3.5

    fig = plt.figure(figsize=(figW, figH))
    gs  = gridspec.GridSpec(nCS, nM, figure=fig, hspace=gapH / (nI * cellH), wspace=0.05,
                            left=0.07, right=0.98, top=1 - titleH / figH, bottom=0.02)

    for row, cs in enumerate(clusterSizes):
        for col, m in enumerate(METHODS):
            ax   = fig.add_subplot(gs[row, col])
            p25  = sweepP25[cs][m].reshape(-1, 1)
            p75  = sweepP75[cs][m].reshape(-1, 1)
            iqr  = p75 - p25
            ax.imshow(iqr, aspect='auto', cmap='RdYlGn_r', vmin=0, vmax=vmax)
            for spine in ax.spines.values():
                spine.set_edgecolor('black')
                spine.set_linewidth(1.2)
            ax.set_xticks([])
            ax.set_yticks(range(nI))
            if col == 0:
                ax.set_yticklabels([f'{iv}m' for iv in intervals], fontsize=6)
                ax.set_ylabel(f'cs={cs}', fontsize=7, fontweight='bold', labelpad=4)
            else:
                ax.set_yticklabels([])
            if row == 0:
                ax.set_title(m, fontsize=8, fontweight='bold', pad=3)
            for r in range(nI):
                v25 = sweepP25[cs][m][r]
                v75 = sweepP75[cs][m][r]
                if np.isfinite(v25) and np.isfinite(v75):
                    med = (v25 + v75) / 2.0
                    ax.text(0, r, f'{med:.3f}\n(IQR {v25:.3f} - {v75:.3f})',
                            ha='center', va='center', fontsize=6, color='black')

    title = 'Clustered dropout - IQR centreline error (P25 - P75) (m)'
    if nRuns:
        title += f'  n={nRuns} runs each'
    fig.suptitle(title, fontsize=11, fontweight='bold', y=0.995)
    plt.show(block=False)


def plotRandomIQRBands(sweepP25, sweepP75, intervals, dropoutRates, nRuns=None):
    intervals     = list(intervals)
    dropoutRates  = list(dropoutRates)
    nM  = len(METHODS)
    nDR = len(dropoutRates)

    fig, axes = plt.subplots(nM, nDR, figsize=(3 * nDR, 2.5 * nM), sharey=True, sharex=True)

    for row, m in enumerate(METHODS):
        color = METHOD_COLORS[m]
        for col, dr in enumerate(dropoutRates):
            ax  = axes[row, col]
            p25 = sweepP25[m][:, col]
            p75 = sweepP75[m][:, col]
            med = (p25 + p75) / 2.0

            ax.plot(intervals, med, color=color, linewidth=1.5, marker='o', markersize=3)
            ax.fill_between(intervals, p25, p75, alpha=0.3, color=color)
            ax.grid(True, linewidth=0.4, alpha=0.5)

            if row == 0:
                ax.set_title(f'{int(dr*100)}%', fontsize=9, fontweight='bold')
            if col == 0:
                ax.set_ylabel(m, fontsize=8, fontweight='bold')
            if row == nM - 1:
                ax.set_xlabel('CERPM interval (m)', fontsize=7)
            ax.tick_params(labelsize=6)

    title = 'Random dropout - IQR band per method  |  band = IQR (P25-P75)'
    if nRuns:
        title += f'  |  n={nRuns} runs'
    fig.suptitle(title, fontsize=11, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.show(block=False)


def plotClusteredIQRBands(sweepP25, sweepP75, intervals, clusterSizes=None, nRuns=None):
    intervals    = list(intervals)
    clusterSizes = list(clusterSizes if clusterSizes is not None else sweepP25.keys())
    nM  = len(METHODS)
    nCS = len(clusterSizes)

    fig, axes = plt.subplots(nM, nCS, figsize=(3 * nCS, 2.5 * nM), sharey=True, sharex=True)

    for row, m in enumerate(METHODS):
        color = METHOD_COLORS[m]
        for col, cs in enumerate(clusterSizes):
            ax  = axes[row, col]
            p25 = sweepP25[cs][m]
            p75 = sweepP75[cs][m]
            med = (p25 + p75) / 2.0

            ax.plot(intervals, med, color=color, linewidth=1.5, marker='o', markersize=3)
            ax.fill_between(intervals, p25, p75, alpha=0.3, color=color)
            ax.grid(True, linewidth=0.4, alpha=0.5)

            if row == 0:
                ax.set_title(f'Cluster size {cs}', fontsize=9, fontweight='bold')
            if col == 0:
                ax.set_ylabel(m, fontsize=8, fontweight='bold')
            if row == nM - 1:
                ax.set_xlabel('CERPM interval (m)', fontsize=7)
            ax.tick_params(labelsize=6)

    title = 'Clustered dropout - IQR band per method  |  band = IQR (P25-P75)'
    if nRuns:
        title += f'  |  n={nRuns} runs'
    fig.suptitle(title, fontsize=11, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.show(block=False)


def plotRandomFailureRate(sweepFail, intervals, dropoutRates, failureThreshold=0.2, nRuns=None):
    intervals    = list(intervals)
    dropoutRates = list(dropoutRates)
    dropoutLabels  = [f'{int(r*100)}%' for r in dropoutRates]
    intervalLabels = [f'{v}m' for v in intervals]

    fig, axes = plt.subplots(1, len(METHODS), figsize=(4 * len(METHODS), 4))

    for col, m in enumerate(METHODS):
        ax = axes[col]
        data = sweepFail[m]
        ax.imshow(data, aspect='auto', cmap='RdYlGn_r', vmin=0, vmax=100)
        ax.set_xticks(range(len(dropoutRates)))
        ax.set_xticklabels(dropoutLabels, rotation=45, ha='right', fontsize=7)
        ax.set_yticks(range(len(intervals)))
        ax.set_yticklabels(intervalLabels if col == 0 else [], fontsize=7)
        ax.set_xlabel('Dropout rate', fontsize=7)
        if col == 0:
            ax.set_ylabel('CERPM interval', fontsize=7)
        ax.set_title(m, fontsize=9, fontweight='bold')
        _annotateCells(ax, data, fontsize=6, fmt='pct')

    title = f'Random dropout - failure rate (max error > {failureThreshold} m) (%)'
    if nRuns:
        title += f'  n={nRuns} runs each'
    fig.suptitle(title, fontsize=11, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show(block=False)


def plotRandomRankingHeatmap(sweepIQR, intervals, dropoutRates):
    intervals    = list(intervals)
    dropoutRates = list(dropoutRates)
    dropoutLabels  = [f'{int(r*100)}%' for r in dropoutRates]
    intervalLabels = [f'{v}m' for v in intervals]

    ranks = {m: np.full((len(intervals), len(dropoutRates)), np.nan) for m in METHODS}
    for r in range(len(intervals)):
        for c in range(len(dropoutRates)):
            vals = [(sweepIQR[m][r, c], m) for m in METHODS]
            sortedVals = sorted(vals, key=lambda x: x[0] if np.isfinite(x[0]) else float('inf'))
            for rank, (_, m) in enumerate(sortedVals, start=1):
                ranks[m][r, c] = rank

    fig, axes = plt.subplots(1, len(METHODS), figsize=(4 * len(METHODS), 4))

    for col, m in enumerate(METHODS):
        ax = axes[col]
        data = ranks[m]
        ax.imshow(data, aspect='auto', cmap='RdYlGn_r', vmin=1, vmax=len(METHODS))
        ax.set_xticks(range(len(dropoutRates)))
        ax.set_xticklabels(dropoutLabels, rotation=45, ha='right', fontsize=7)
        ax.set_yticks(range(len(intervals)))
        ax.set_yticklabels(intervalLabels if col == 0 else [], fontsize=7)
        ax.set_xlabel('Dropout rate', fontsize=7)
        if col == 0:
            ax.set_ylabel('CERPM interval', fontsize=7)
        ax.set_title(m, fontsize=9, fontweight='bold')
        _annotateCells(ax, data, fontsize=8, fmt='d')

    fig.suptitle('Random dropout - method ranking by IQR (1 = lowest)', fontsize=11, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show(block=False)


def randomSummaryTable(sweepIQR, intervals, dropoutRates):
    intervals    = list(intervals)
    dropoutRates = list(dropoutRates)
    nCells = len(intervals) * len(dropoutRates)

    print(f"\n{'='*78}")
    print(f"  Random dropout - IQR range (P75-P25) centreline error across all conditions")
    print(f"{'='*78}")
    print(f"  {'Method':<14} {'Median IQR range':>16} {'Best (rank 1)':>14} {'Worst (last)':>14} {'% cells won':>12}")
    print(f"  {'-'*72}")

    cellRanks = {m: [] for m in METHODS}
    for r in range(len(intervals)):
        for c in range(len(dropoutRates)):
            vals = [(sweepIQR[m][r, c], m) for m in METHODS]
            sortedVals = sorted(vals, key=lambda x: x[0] if np.isfinite(x[0]) else float('inf'))
            for rank, (_, m) in enumerate(sortedVals, start=1):
                cellRanks[m].append(rank)

    rows = []
    for m in METHODS:
        allVals = [sweepIQR[m][r, c] for r in range(len(intervals)) for c in range(len(dropoutRates))]
        valid = [v for v in allVals if np.isfinite(v)]
        overallMed = np.median(valid) if valid else float('nan')
        nFirst = cellRanks[m].count(1)
        nLast  = cellRanks[m].count(len(METHODS))
        pctWon = 100 * nFirst / nCells
        rows.append((overallMed, m, nFirst, nLast, pctWon))

    for overallMed, m, nFirst, nLast, pctWon in sorted(rows):
        print(f"  {m:<14} {overallMed:>16.4f} {nFirst:>14} {nLast:>14} {pctWon:>11.1f}%")

    print(f"\n{'='*78}\n")


def plotClusteredFailureRate(sweepFail, intervals, clusterSizes=None, failureThreshold=0.2, nRuns=None):
    intervals    = list(intervals)
    clusterSizes = list(clusterSizes if clusterSizes is not None else sweepFail.keys())
    nI  = len(intervals)
    nCS = len(clusterSizes)
    nM  = len(METHODS)

    cellH  = 0.45
    gapH   = 0.15
    titleH = 0.4
    figH   = titleH + nCS * (nI * cellH + gapH)
    figW   = nM * 2.2

    fig = plt.figure(figsize=(figW, figH))
    gs  = gridspec.GridSpec(nCS, nM, figure=fig, hspace=gapH / (nI * cellH), wspace=0.05,
                            left=0.07, right=0.98, top=1 - titleH / figH, bottom=0.02)

    for row, cs in enumerate(clusterSizes):
        for col, m in enumerate(METHODS):
            ax   = fig.add_subplot(gs[row, col])
            data = sweepFail[cs][m].reshape(-1, 1)
            ax.imshow(data, aspect='auto', cmap='RdYlGn_r', vmin=0, vmax=100)
            for spine in ax.spines.values():
                spine.set_edgecolor('black')
                spine.set_linewidth(1.2)
            ax.set_xticks([])
            ax.set_yticks(range(nI))
            if col == 0:
                ax.set_yticklabels([f'{iv}m' for iv in intervals], fontsize=6)
                ax.set_ylabel(f'cs={cs}', fontsize=7, fontweight='bold', labelpad=4)
            else:
                ax.set_yticklabels([])
            if row == 0:
                ax.set_title(m, fontsize=8, fontweight='bold', pad=3)
            _annotateCells(ax, data, fontsize=8, fmt='pct')

    title = f'Clustered dropout - failure rate (max error > {failureThreshold} m) (%)'
    if nRuns:
        title += f'  n={nRuns} runs each'
    fig.suptitle(title, fontsize=11, fontweight='bold', y=0.995)
    plt.show(block=False)


def plotClusteredRankingHeatmap(sweepIQR, intervals, clusterSizes=None):
    intervals    = list(intervals)
    clusterSizes = list(clusterSizes if clusterSizes is not None else sweepIQR.keys())
    nI  = len(intervals)
    nCS = len(clusterSizes)
    nM  = len(METHODS)

    allRanks = {}
    for cs in clusterSizes:
        ranks = {m: np.full(nI, np.nan) for m in METHODS}
        for r in range(nI):
            vals = [(sweepIQR[cs][m][r], m) for m in METHODS]
            sortedVals = sorted(vals, key=lambda x: x[0] if np.isfinite(x[0]) else float('inf'))
            for rank, (_, m) in enumerate(sortedVals, start=1):
                ranks[m][r] = rank
        allRanks[cs] = ranks

    cellH  = 0.45
    gapH   = 0.15
    titleH = 0.4
    figH   = titleH + nCS * (nI * cellH + gapH)
    figW   = nM * 2.2

    fig = plt.figure(figsize=(figW, figH))
    gs  = gridspec.GridSpec(nCS, nM, figure=fig, hspace=gapH / (nI * cellH), wspace=0.05,
                            left=0.07, right=0.98, top=1 - titleH / figH, bottom=0.02)

    for row, cs in enumerate(clusterSizes):
        for col, m in enumerate(METHODS):
            ax   = fig.add_subplot(gs[row, col])
            data = allRanks[cs][m].reshape(-1, 1)
            ax.imshow(data, aspect='auto', cmap='RdYlGn_r', vmin=1, vmax=nM)
            for spine in ax.spines.values():
                spine.set_edgecolor('black')
                spine.set_linewidth(1.2)
            ax.set_xticks([])
            ax.set_yticks(range(nI))
            if col == 0:
                ax.set_yticklabels([f'{iv}m' for iv in intervals], fontsize=6)
                ax.set_ylabel(f'cs={cs}', fontsize=7, fontweight='bold', labelpad=4)
            else:
                ax.set_yticklabels([])
            if row == 0:
                ax.set_title(m, fontsize=8, fontweight='bold', pad=3)
            _annotateCells(ax, data, fontsize=8, fmt='d')

    fig.suptitle('Clustered dropout - method ranking by IQR (1 = lowest)', fontsize=11, fontweight='bold', y=0.995)
    plt.show(block=False)


def clusteredSummaryTable(sweepIQR, intervals, clusterSizes=None):
    intervals    = list(intervals)
    clusterSizes = list(clusterSizes if clusterSizes is not None else sweepIQR.keys())
    nCells = len(intervals)

    print(f"\n{'='*78}")
    print(f"  Clustered dropout - IQR range (P75-P25) centreline error across all conditions")
    print(f"{'='*78}")

    for cs in clusterSizes:
        print(f"\n  Cluster size: {cs}")
        print(f"  {'Method':<14} {'Median IQR range':>16} {'Best (rank 1)':>14} {'Worst (last)':>14} {'% cells won':>12}")
        print(f"  {'-'*72}")

        cellRanks = {m: [] for m in METHODS}
        for r in range(len(intervals)):
            vals = [(sweepIQR[cs][m][r], m) for m in METHODS]
            sortedVals = sorted(vals, key=lambda x: x[0] if np.isfinite(x[0]) else float('inf'))
            for rank, (_, m) in enumerate(sortedVals, start=1):
                cellRanks[m].append(rank)

        rows = []
        for m in METHODS:
            allVals = [sweepIQR[cs][m][r] for r in range(len(intervals))]
            valid = [v for v in allVals if np.isfinite(v)]
            overallMed = np.median(valid) if valid else float('nan')
            nFirst = cellRanks[m].count(1)
            nLast  = cellRanks[m].count(len(METHODS))
            pctWon = 100 * nFirst / nCells
            rows.append((overallMed, m, nFirst, nLast, pctWon))

        for overallMed, m, nFirst, nLast, pctWon in sorted(rows):
            print(f"  {m:<14} {overallMed:>16.4f} {nFirst:>14} {nLast:>14} {pctWon:>11.1f}%")

    print(f"\n{'='*78}\n")


def _saveFigs(outputDir):
    os.makedirs(outputDir, exist_ok=True)
    figNames = [
        'random_ranking_heatmap',
        'random_iqr_heatmap',
        'random_iqr_bands',
        'random_failure_rate',
        'clustered_ranking_heatmap',
        'clustered_iqr_heatmap',
        'clustered_iqr_bands',
        'clustered_failure_rate',
    ]
    figNums = plt.get_fignums()
    for i, figNum in enumerate(figNums):
        fig  = plt.figure(figNum)
        name = figNames[i] if i < len(figNames) else f'figure_{i+1}'
        savePath = os.path.join(outputDir, f'{name}.png')
        fig.savefig(savePath, dpi=150, bbox_inches='tight')
        print(f'  Saved: {savePath}')
    plt.close('all')


def fullAnalysis(nRuns=500, intervals=(0.5, 1.0, 2.0, 3.0, 5.0), dropoutRates=(0.01, 0.05, 0.1, 0.15, 0.2),
                 clusterSizes=(2, 5, 10, 15, 20), baseSeed=0, failureThreshold=0.2,
                 path='Maps/PowerPoint/Town07PowerPoint.osm'):
    lanelets = parseOSM(path)
    leftWay, rightWay = test.combineWays(lanelets)

    rIQR, rP25, rP75, rFail = _runSweepRandom(
        leftWay, rightWay, nRuns, intervals, dropoutRates,
        baseSeed, failureThreshold=failureThreshold)

    cIQR, cP25, cP75, cFail = _runSweepClustered(
        leftWay, rightWay, nRuns, intervals,
        clusterSizes, baseSeed, failureThreshold=failureThreshold)

    randomSummaryTable(rIQR, intervals, dropoutRates)
    clusteredSummaryTable(cIQR, intervals)

    plotRandomRankingHeatmap(rIQR, intervals, dropoutRates)
    plotRandomIQRHeatmap(rP25, rP75, intervals, dropoutRates, nRuns=nRuns)
    plotRandomIQRBands(rP25, rP75, intervals, dropoutRates, nRuns=nRuns)
    plotRandomFailureRate(rFail, intervals, dropoutRates,
                          failureThreshold=failureThreshold, nRuns=nRuns)

    plotClusteredRankingHeatmap(cIQR, intervals)
    plotClusteredIQRHeatmap(cP25, cP75, intervals, clusterSizes, nRuns=nRuns)
    plotClusteredIQRBands(cP25, cP75, intervals, clusterSizes, nRuns=nRuns)
    plotClusteredFailureRate(cFail, intervals,
                             failureThreshold=failureThreshold, nRuns=nRuns)

    mapName  = os.path.splitext(os.path.basename(path))[0]
    outputDir = os.path.join('Results', mapName)
    print(f'\nSaving graphs to {outputDir}/ ...')
    _saveFigs(outputDir)
    print(f'All graphs saved for {mapName}.\n')


def plotRoads(leftWay, rightWay):
    lx = [p[0] for p in leftWay]
    ly = [p[1] for p in leftWay]
    rx = [p[0] for p in rightWay]
    ry = [p[1] for p in rightWay]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.plot(ly, lx, color='steelblue', lw=1)
    ax.plot(ry, rx, color='steelblue', lw=1)
    ax.scatter(ly, lx, color='steelblue', s=10, zorder=4)
    ax.scatter(ry, rx, color='steelblue', s=10, zorder=4)
    ax.set_aspect('equal')
    plt.show()


if __name__ == '__main__':
    lanelets = parseOSM('Maps/PowerPoint/Town07PowerPoint.osm')
    leftWay, rightWay = test.combineWays(lanelets)
    plotRoads(leftWay, rightWay)

    leftprint  = test.resample(leftWay, 2)
    rightprint = test.resample(rightWay, 2)
    plotRoads(leftprint, rightprint)

    MAPS = [
        'Maps/PowerPoint/Town07PowerPoint.osm',
        'Maps/PowerPoint/Town041.osm',
        'Maps/PowerPoint/Town042.osm',
        'Maps/PowerPoint/Town043.osm',
        'Maps/PowerPoint/Town044.osm',
    ]

    for mapPath in MAPS:
        print(f'\n{"="*78}')
        print(f'  Running full analysis on: {mapPath}')
        print(f'{"="*78}\n')
        fullAnalysis(
            nRuns=2000,
            intervals=(0.5, 1.0, 2.0, 3.0, 5.0),
            dropoutRates=(0.01, 0.05, 0.1, 0.15, 0.2),
            clusterSizes=(2, 5, 10, 15, 20),
            failureThreshold=0.2,
            path=mapPath,
        )