# -*- coding: utf-8 -*

"""
Homophony due to liaison Project
Renaming frequency data files
Victor ANTOINE
"""

#
# Importing libraries
#

import os
import pandas as pd

#
# Creating Dataframe for mapping 
# the file number to the query
# 

queries = pd.DataFrame(columns=['query'])
idQuery = 0

#
# Renaming all files with a shorter name
#

longPathFix = '\\\\?\\'
wd = os.path.realpath('./')

for root, dirs, files in os.walk('doublets\\raw-frequency-data'):
    for file in files:
        queries.loc[idQuery] = file
        os.rename(longPathFix + os.path.join(wd,root, file),\
                  longPathFix + os.path.join(wd,root, str(idQuery)+'.csv'))
        idQuery += 1
queries['idFile'] = list(range(len(queries)))
queries.to_csv('resources\\queries.csv', index=False)
