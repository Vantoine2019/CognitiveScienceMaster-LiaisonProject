# -*- coding: utf-8 -*

"""
Homophony due to liaison Project
Cleaning of frequency data for all doublets
Victor ANTOINE
"""

#
# Importing libraries
#

import re
import os
import numpy as np
import pandas as pd
import unicodedata
from itertools import combinations

#
# Constants
#
dfQueries = pd.read_csv('resources\\queries.csv')
dfQueries = dfQueries.set_index('idFile')

total2Ngrams = pd.read_csv('resources\\2ngram-total-count.csv')
total2Ngrams = total2Ngrams[total2Ngrams.year >= 1800]
total2Ngrams = total2Ngrams.reset_index(drop=True)

total4Ngrams = pd.read_csv('resources\\4ngram-total-count.csv')
total4Ngrams = total4Ngrams[total4Ngrams.year >= 1800]
total4Ngrams = total4Ngrams.reset_index(drop=True)

#
# Functions to clean the raw frequency data of Google Ngram Viewer
#

def removeDiacritics(text):
    """
    Returns a string with all diacritics (aka non-spacing marks) removed.
    For example "Héllô" will become "Hello".
    Useful for comparing strings in an accent-insensitive fashion.
    """
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")

def countDiacritics(text):
    """ Counts the number of accents in a word """
    normalized = unicodedata.normalize("NFKD", text)
    diacritics = "".join(c for c in normalized if unicodedata.category(c) == "Mn")
    return len(diacritics)

def retrieveQueries(queryFile):
    """ Retrieves the queries done on Google Ngram Viewer
    from the name of the .csv file """
    queries = []
    nameFile = queryFile.split('-fre')[0]

    if re.search(r'([A-Z]{3,4})', queryFile) != None:
        nameFile = nameFile.split('_')
        if '[' in queryFile:
            for idx, el in enumerate(nameFile):
                if el.startswith('['):
                    queries.append([re.sub(r'\[|\]', '', el)])
                    nameFile.remove(el)
        i, stop = 0, len(nameFile)
        while i < stop:
            queries.append(nameFile[i:i+3])
            i += 3
        for idx, el in enumerate(queries):
            queries[idx] = ''.join([el for el in el])
    else:
        nameFile = re.sub(r'\[|\]', '', nameFile)
        queries = nameFile.split('_')
    return queries
        
def wordsInQuery(queryFile):
    """ Counts the number of word in queries for a given .csv file
    Enable to distinguish simple cases vs cases with hyphens
    Google considers 'beau-fils' as 3 words """
    numberWordsQuery = {}
    queries = retrieveQueries(queryFile)
    for query in queries:
        numberHyphen = query.count('-')
        query = query.replace(' ','')
        query = query.replace('-','')
        query = query.replace('_','')
        query = removeDiacritics(query)
        if query not in numberWordsQuery:
            if numberHyphen == 0:
                numberWordsQuery[query] = 2
            elif numberHyphen == 1:
                numberWordsQuery[query] = 4
            elif numberHyphen == 2:
                numberWordsQuery[query] = None
    return numberWordsQuery

def concatenateColumnsName(df):
    """ Renames column names of a DataFrame by removing spaces, underscores and dashes.
    A column named 'Exam-ple_Colu-mn' will become 'ExampleColumn' """
    renamed_cols = []
    for col in df.columns.to_list():
        newColName = col.replace(' ','')
        newColName = newColName.replace('-','')
        newColName = newColName.replace('_','')
        renamed_cols.append(newColName)
    df.columns = renamed_cols
    return df

def organizeDataFrame(df):
    """ Returns a DataFrame containing the proportion data with 
    one column per query """
    queries = retrieveQueries(queryFile)    
    for query1, query2 in combinations(queries, 2):
        if removeDiacritics(query1) == removeDiacritics(query2):
            if query1[0] == query2[0]:
                if countDiacritics(query1) > countDiacritics(query2):
                    queries.remove(query2)
                else:
                    queries.remove(query1)
    for idx, query in enumerate(queries):
        queries[idx] = query.replace('-','')
    data = pd.DataFrame(index=list(range(0,220)), columns=queries)
    data['year'] = list(range(1800,2020))
    for col in queries:
        if col in df.columns:
            data[col] = df[col]
        else:
            data[col] = 0
    return data

def retrieveMatchCount(df):
    """ Adds to the DataFrame containing only the proportion data
    the raw data i.e. the number of occurrences for each query """
    for col in df:
        if col != 'year':
            key = removeDiacritics(col)
            if numberWordsQuery[key] == 2:
                df[col + '_count'] = df[col] * total2Ngrams['match_count']
            if numberWordsQuery[key] == 4:
                df[col + '_count'] = df[col] * total4Ngrams['match_count']
            if numberWordsQuery[key] == None:
                df[col + '_count'] = np.nan

    """ Sums the data of columns that differ only by an accent at the beginning of a word
    For example, sums the data of the columns 'ôté' and 'oté' """
    for col1, col2 in combinations([col for col in df.columns if col.endswith('count')], 2):
        if removeDiacritics(col1) == removeDiacritics(col2):
            df[col1] = df[col1] + df[col2]
            df = df.drop([col2], axis=1)
    return df
               
#
# Cleaning and saving data
#

if not os.path.exists('doublets\\cleaned-frequency-data'):
   os.makedirs('doublets\\cleaned-frequency-data')

for root, dirs, files in os.walk('doublets\\raw-frequency-data'):
    # Creating folders to store cleaned data
    for dir in dirs:
        folderCleanData = os.path.join('doublets\\cleaned-frequency-data', dir)
        if not os.path.exists(folderCleanData):
            os.makedirs(folderCleanData)

    # Cleaning data and storing in previously created folders
    for file in files:
        queryFile = dfQueries.loc[int(file[:-4]),'query']
        folderCleanData = re.search('doublets_[A-Za-z]_[A-Za-z]-?', os.path.join(root, file))[0]
        cleanedData = pd.read_csv(os.path.join(root, file), encoding='utf-8')
        numberWordsQuery = wordsInQuery(queryFile)
        cleanedData = concatenateColumnsName(cleanedData)
        cleanedData = organizeDataFrame(cleanedData)
        cleanedData = retrieveMatchCount(cleanedData)
        cleanedData = cleanedData.drop([col for col in cleanedData.columns if not col.endswith('count')], 1)     
        cleanedData.to_csv(os.path.join('doublets\\cleaned-frequency-data', folderCleanData,'-'.join(cleanedData.columns) + '.csv'), index = False)
