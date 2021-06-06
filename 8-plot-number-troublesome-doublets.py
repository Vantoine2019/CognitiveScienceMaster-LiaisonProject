# -*- coding: utf-8 -*

"""
Homophony due to liaison Project
Plotting number of troublesome doublets
Victor ANTOINE
"""

#
# Importing libraries
#

import pandas as pd
import matplotlib.pyplot as plt

# 
# Constants
#

FIGSIZE = (8.5,7)

#
# Importing results
#

results = pd.read_csv('results\\results-number-troublesome-doublets.csv')
results = results.fillna(0)
results.loc[results.substitution == 'S', 'substitution'] = 'ʃ'
results.loc[results.substitution == 'R', 'substitution'] = 'ʁ'
results.loc[results.substitution == 'Z', 'substitution'] = 'ʒ'
results = results.rename(columns={'R':'ʁ'})

pValues = {'g':['','= 0.0890','V = 48'],
           'n':['*','< 0.001','V = 115'],
           'p':['','= 0.9816','V = 24'],
           'ʁ':['','= 0.9993','V = 4'],
           't':['*','< 0.003','V = 109'],
           'z':['*','< 0.001','V = 120']}

#
# Functions
#

def retrieveResultsNumber(liaisonCons):
    """ Returns a DataFrame of results for a given liaison consonant
    with the number of data points for all substitutions
    and appropriate colors for the final plot """
    data = pd.DataFrame(columns = ['substitution','numberDifficultDoublets','color'])
    for idx, res in results[['substitution', liaisonCons]].iterrows():
        if res.substitution == liaisonCons:
            color = 'blue'
            substitution = 'Fr'
        else:
            substitution = res.substitution
            color = 'grey'
        numberDifficultDoublets = res[liaisonCons]
        data = data.append({'substitution':substitution,
                            'numberDifficultDoublets':numberDifficultDoublets,
                            'color':color}, ignore_index=True)
        data = data.sort_values(['numberDifficultDoublets'])
        data = data.reset_index(drop=True)
    return data


def createSubplotNumber(liaisonCons, ax, ylabel = False):
    """ Create a subplot for a given liaison consonant """
    data = retrieveResultsNumber(liaisonCons)
    subplot = ax.bar(data.substitution,\
                     data.numberDifficultDoublets,\
                     color=data.color)
    subplot = ax.set_title('Liaison consonant : [' + liaisonCons + ']',fontsize=12)
    if ylabel == True:
        subplot = ax.set_ylabel('Number of \ntroublesome doublets', fontsize=12)
    subplot = ax.tick_params('x', labelsize=11)
    subplot = ax.tick_params('y', labelsize=10)
    #Adding p-value & '*' if significant
    idxFre = data[data.substitution == 'Fr'].index.to_list()[0]
    valueFre = data.loc[idxFre, 'numberDifficultDoublets']
    asterisk, pValue, V = pValues[liaisonCons]
    subplot = ax.text(idxFre, valueFre+  (data.numberDifficultDoublets.max()/100),\
                      asterisk, size=30, ha='center')
    subplot =  ax.annotate('p '+pValue, xy=(0, 1), xycoords='axes fraction', fontsize=12,\
                           xytext=(10, -10), textcoords='offset points', ha='left', va='top')
    subplot =  ax.annotate(V, xy=(0, 1), xycoords='axes fraction', fontsize=12,\
                           xytext=(10, -30), textcoords='offset points', ha='left', va='top')
    return subplot

#
# Plotting results
#

plt.style.use('seaborn-whitegrid')
fig, ax = plt.subplots(3, 2, figsize=FIGSIZE)
ax = ax.flatten()    
createSubplotNumber('t', ax[0], ylabel = True)
createSubplotNumber('z', ax[1])
createSubplotNumber('n', ax[2], ylabel = True)
createSubplotNumber('ʁ', ax[3])
createSubplotNumber('p', ax[4], ylabel = True)
createSubplotNumber('g', ax[5])
fig.tight_layout()
fig.savefig('plots\\plot-number-troublesome-doublets.png', facecolor='w')
