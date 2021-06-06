# -*- coding: utf-8 -*-

"""
Homophony due to liaison Project
Plotting number of confusing sequences
Victor ANTOINE
"""

#
# Importing Libraries
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

results = pd.read_csv('results\\results-number-confusing-doublets.csv')
results = results[~results.substitution.str.contains('G|N|x')] #removing loaned phonemes
results.loc[results.substitution == 'S', 'substitution'] = 'ʃ'
results.loc[results.substitution == 'R', 'substitution'] = 'ʁ'
results.loc[results.substitution == 'Z', 'substitution'] = 'ʒ'
results = results.rename(columns={'R':'ʁ'})

pValues = {'g':['*','< 0.008','V = 91.5'],
           'n':['*','< 0.004','V = 106'],
           'p':['','= 0.8093','V = 33.5'],
           'ʁ':['','= 0.9996','V = 1'],
           't':['*','< 0.04','V = 93'],
           'z':['*','< 0.001','V = 120']}

#
# Functions
#

def retrieveResults(liaisonCons):
    """ Returns a DataFrame of results for a given liaison consonant
    with the number of confusing sequences for all substitutions
    and appropriate colors for the final plot """
    data = pd.DataFrame(columns = ['substitution','numberConfusingSequences','color'])
    for idx, res in results[['substitution', liaisonCons]].iterrows():
        if res.substitution == liaisonCons:
            color = 'blue'
            substitution = 'Fr'
        else:
            substitution = res.substitution
            color = 'grey'
        numberConfusingSequences = res[liaisonCons]
        data = data.append({'substitution':substitution,
                            'numberConfusingSequences':numberConfusingSequences,
                            'color':color}, ignore_index=True)
        data = data.sort_values(['numberConfusingSequences'])
        data = data.reset_index(drop=True)
    return data


def createSubplot(liaisonCons, ax, ylabel = False):
    """ Create a subplot for a given liaison consonant """
    data = retrieveResults(liaisonCons)
    subplot = ax.bar(data.substitution,\
                     data.numberConfusingSequences,\
                     color=data.color)
    subplot = ax.set_title('Liaison consonant : [' + liaisonCons + ']',fontsize=12)
    if ylabel == True:
        subplot = ax.set_ylabel('Number of \nconfusing doublets', fontsize=12)
    subplot = ax.tick_params('x', labelsize=11)
    subplot = ax.tick_params('y', labelsize=10)
    #Adding p-value & '*' if significant
    idxFre = data[data.substitution == 'Fr'].index.to_list()[0]
    valueFre = data.loc[idxFre, 'numberConfusingSequences']
    asterisk, pValue, V = pValues[liaisonCons]
    subplot = ax.text(idxFre, valueFre+  (data.numberConfusingSequences.max()/100),\
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
createSubplot('z', ax[0], ylabel = True)
createSubplot('t', ax[1])
createSubplot('n', ax[2], ylabel = True)
createSubplot('p', ax[3])
createSubplot('ʁ', ax[4], ylabel = True)
createSubplot('g', ax[5])
fig.tight_layout()
fig.savefig('plots\\plot-number-confusing-doublets.png', facecolor='w')
