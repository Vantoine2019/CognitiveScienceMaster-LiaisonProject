# -*- coding: utf-8 -*

"""
Homophony due to liaison Project
Analysis of frequency data
(i) CDF of ratio and sum of frequency values of doublets
(ii) Extraction of the number of troublesome doublets (ratio & sum > perc. 50)
Victor ANTOINE
"""

#
# Importing libraries
#

import re
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import math
from collections import defaultdict

#
# Constants
#

CONS = ['z','Z','g','n','S','l','b','v','d','f','k','t','m','p','R','s']
CONS_LIAISON = ['g', 'n', 'p', 'R', 't', 'z']

#
# Extraction of the 50 percentiles of sum and ratio (from our 30689 doublets)
# Plotting CDF for ration and log(sum)
#

    # Percentiles
resultsRatio = []
resultsSum = []
for root, dirs, files in os.walk('doublets\\cleaned-frequency-data'):
    for file in files:        
        # Reading data
        df = pd.read_csv(os.path.join(root, file))
        df['year'] = list(range(1800,2020))
        df = df[df.year >= 1950]
        ngram1, ngram2 = list(df.columns)[0], list(df.columns)[1]
		# Extracting ratio and sum
        data = [round(sum(df[ngram1]))+1, round(sum(df[ngram2]))+1]
        ratio = min(data) / max(data)
        tot = sum(data)
        resultsRatio.append(ratio)
        resultsSum.append(tot)
resultsSumLog = [math.log(tot,10) for tot in resultsSum]

p50Ratio = np.percentile(resultsRatio, 50)
p50Sum = np.percentile(resultsSum, 50)
p50SumLog = np.percentile(resultsSumLog, 50)


    # CDF
indexPlotRatio = np.arange(1,len(resultsRatio)+1) / len(resultsRatio)
resultsRatio = sorted(resultsRatio)
indexPlotSumLog = np.arange(1,len(resultsSumLog)+1) / len(resultsSumLog)
resultsSumLog = sorted(resultsSumLog)

plt.style.use('default')
fig, axs = plt.subplots(1,2, figsize=(8.5,3))

axs[0].step(resultsRatio, indexPlotRatio)
axs[0].grid(axis='y', alpha=0.75)
axs[0].axvline(x=p50Ratio, color='black', linestyle='dashed')
axs[0].set_xlabel('Ratio')
axs[0].set_ylabel('CDF')
axs[0].set_title('Cumulative distribution function\n of ratio of frequency values the doublets', fontdict={'fontsize': 11})
axs[0].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

axs[1].step(resultsSumLog, indexPlotSumLog)
axs[1].grid(axis='y', alpha=0.75)
axs[1].axvline(x=p50SumLog, color='black', linestyle='dashed')
axs[1].set_xlabel('Log(Sum)')
axs[1].set_title('Cumulative distribution function of log of\n the sum of frequency values of the doublets', fontdict={'fontsize': 11})
axs[1].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

fig.tight_layout()
fig.savefig('plots\\plot-CDF-ratio-sum-frequency-data.png', facecolor='w')


    # Number of troublesome doublets (> 50 perc. for both ratio and sum)
dictTrblDoublets = defaultdict(list)
for root, dirs, files in os.walk('doublets\\cleaned-frequency-data'):
    for file in files:

 		# Extracting the key from the file name
        key = re.search('doublets_[A-Za-z]_[A-Za-z]-?', os.path.join(root, file))[0]
        key = re.search('[A-Za-z]_[A-Za-z]-?$', key)[0]
        
        # Reading data
        df = pd.read_csv(os.path.join(root, file))
        df['year'] = list(range(1800,2020))
        df = df[df.year >= 1950]
        ngram1, ngram2 = list(df.columns)[0], list(df.columns)[1]
        
		# Calculating the score
        data = [round(sum(df[ngram1]))+1, round(sum(df[ngram2]))+1]
        ratio = min(data) / max(data)
        tot = sum(data)
        score = ratio * tot
        if (ratio >= p50Ratio) & (tot >= p50Sum):
            dictTrblDoublets[key].append(score)
dictTrblDoublets = dict(dictTrblDoublets)

nbrTrblDoublets = pd.DataFrame(index = CONS, columns = CONS_LIAISON)
for key in dictTrblDoublets:
    liaisonCons = key.split('_')[0]
    substitutionCons = key.split('_')[1]
    if substitutionCons[0].isupper():
        substitutionCons = substitutionCons[0]
    data = len(dictTrblDoublets[key])
    nbrTrblDoublets.loc[substitutionCons, liaisonCons] = data
nbrTrblDoublets['substitution'] = CONS
nbrTrblDoublets.to_csv("results\\results-number-troublesome-doublets.csv", index=False)   
