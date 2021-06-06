# -*- coding: utf-8 -*-

"""
Homophony due to liaison Project
Extraction of minimal pairs of Words2
Victor ANTOINE
"""

#
# Importing Libraries
#
import pandas as pd

#
# Constants
#
CONS = ['t', 'n', 'z', 'g', 'p', 'R', 'b', 'd', 'k', 'f', 'v', 's', 'S', 'Z', 'm', 'N', 'l', 'x', 'G']
VOY = ['a', 'i', 'y', 'u', 'o', 'O', 'e', 'E', '°', '2', '9', '5', '1', '@', '§', '3', 'j', '8', 'w']
H_ASP = pd.read_csv('resources\\h-asp.csv').ortho.to_list()

	# Columns of interest in Lexique
COLUMNS = ['ortho', 'phon', 'lemme', 'cgram', 'genre', 'nombre','infover','cgramortho','freqfilms2','islem','p_cvcv']
COLUMNS_1 = ['{}_1'.format(a) for a in COLUMNS] #Columns for one word of a minimal pair
COLUMNS_2 = ['{}_2'.format(a) for a in COLUMNS]	#Columns for the other word of a minimal pair

	# Cleaning Lexique
LEX = pd.read_csv('resources\\Lexique383.tsv', sep='\t')
LEX = LEX[COLUMNS]
LEX = LEX[~LEX.cgram.isin(['LIA','ONO'])]
LEX = LEX[~((LEX.ortho.str.len()==1) & ~((LEX.lemme.isin(['avoir','à'])) & (LEX.phon == 'a')))]
LEX.loc[LEX[LEX.ortho.isin(['au', 'aux', 'de', 'du'])].index,'cgram'] = 'PRE'
LEX.loc[LEX[LEX.phon == 'n@'].index,['ortho','lemme']] = 'nan'
LEX = LEX[~LEX.lemme.isin(H_ASP)]
LEX = LEX[LEX.freqfilms2>=1]
LEX = LEX.reset_index(drop=True)

# 
# Functions
#

# Function to retrieve all minimal pairs in Lexique
def extractPairs(df, cons):
	pairs = pd.DataFrame(columns = COLUMNS_1 + COLUMNS_2)
	
	for row in range(len(df)):
		if df.iloc[row].phon[0] in VOY:        
			for C in cons:
				dfSearchedPair = df.loc[df.phon == (C + df.iloc[row].phon)]
				dfSearchedPair = dfSearchedPair.add_suffix('_2')
				for row_2 in range(len(dfSearchedPair)):
					pairs = pairs.append(df.iloc[row].add_suffix('_1'), ignore_index=True)
					pairs.loc[pairs.index[-1], dfSearchedPair.columns] = dfSearchedPair.iloc[row_2]

	return pairs

# Function to eliminate unacceptable pairs (manually detected)
def filterPairs(df):
	UNACCEPT_ENTRIES = pd.read_csv('resources\\unacceptable-entries.csv')
	UNACCEPT_ENTRIES.fillna('nan', inplace=True)
	dropouts = []
	for idx, row in UNACCEPT_ENTRIES.iterrows():
		index = df[((df.lemme_1 == row.lemme) & (df.cgram_1 == row.cgram)) | \
				   ((df.lemme_2 == row.lemme) & (df.cgram_2 == row.cgram))].index.to_list()
		for i in index:
			dropouts.append(i)
	dropouts = list(set(dropouts))
	df = df.drop(dropouts)
	df = df.reset_index(drop=True) 
	return df

#
# Extraction of minimal pairs and saving them
#
minimalPairs = extractPairs(LEX, CONS)
minimalPairs = filterPairs(minimalPairs)
minimalPairs.to_csv('resources\\minimal-pairs.csv', index=False)