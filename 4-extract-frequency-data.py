#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
Homophony due to liaison Project
Extraction of frequency data for all doublets
from Google Ngram Viewer
Victor ANTOINE
"""

# 1st part of the script to retrieve data from
# Google Ngram Viewer : https://github.com/econpy/google-ngrams

#
# Importing Libraries
#

from ast import literal_eval
from pandas import DataFrame  # http://github.com/pydata/pandas
import re
import requests               # http://github.com/kennethreitz/requests
import subprocess
import time
import os
import pandas as pd
import unicodedata

#
# Functions to retrive data from Google Ngram Viewer
#

corpora = dict(eng_us_2012=17, eng_us_2009=5, eng_us_2019=28,
               eng_gb_2012=18, eng_gb_2009=6, eng_gb_2019=26,
               chi_sim_2019=34, chi_sim_2012=23, chi_sim_2009=11,
               eng_2012=15, eng_2009=0,
               eng_fiction_2012=16, eng_fiction_2009=4, eng_1m_2009=1,
               fre_2019=30, fre_2012=19, fre_2009=7,
               ger_2019=31, ger_2012=20, ger_2009=8,
               heb_2012=24,
               heb_2009=9,
               spa_2019=32, spa_2012=21, spa_2009=10,
               rus_2019=36, rus_2012=25, rus_2009=12,
               ita_2019=33, ita_2012=22)


def getNgrams(query, corpus, startYear, endYear, smoothing, caseInsensitive):
    params = dict(content=query, year_start=startYear, year_end=endYear,
                  corpus=corpora[corpus], smoothing=smoothing,
                  case_insensitive=caseInsensitive)
    if params['case_insensitive'] is False:
        params.pop('case_insensitive')
    if '?' in params['content']:
        params['content'] = params['content'].replace('?', '*')
    if '@' in params['content']:
        params['content'] = params['content'].replace('@', '=>')

    exp = 3
    req = requests.get('http://books.google.com/ngrams/graph', params=params)
    while req.status_code !=200:	
    	exp += 1
    	WaitingTime = 2 ** exp
    	print('Waiting ' + str(WaitingTime) +'s ...' )
    	time.sleep(WaitingTime)
    	req = requests.get('http://books.google.com/ngrams/graph', params=params)
    res = re.findall('ngrams.data = .*\];', req.text)
    assert(len(res)==1)

    if res:
        dataDict = literal_eval(res[0].replace(
            "ngrams.data = ", "").replace(";", ""))
        data = {qry['ngram']: qry['timeseries']
                for qry in dataDict}
        df = DataFrame(data)
        df.insert(0, 'year', list(range(startYear, endYear + 1)))
    else:
        df = DataFrame()
    return req.url, params['content'], df

def trimSpaceNearComma(argumentString):
    while (argumentString.find(', ')>=0):
        argumentString = argumentString.replace(', ',',')
    while (argumentString.find(' ,')>=0):
        argumentString = argumentString.replace(' ,',',')
    return argumentString

def runQuery(argumentString):    
    arguments = trimSpaceNearComma(argumentString).split()
    query = ' '.join([arg for arg in arguments if not arg.startswith('-')])
    if '-' in query:
        query = query.replace('-',' - ')
    if '?' in query:
        query = query.replace('?', '*')
    if '@' in query:
        query = query.replace('@', '=>')
    params = [arg for arg in arguments if arg.startswith('-')]
    corpus, startYear, endYear, smoothing = 'eng_2012', 1800, 2000, 3
    printHelp, caseInsensitive, allData = False, False, False
    toSave, toPrint, toPlot = True, True, False
    # parsing the query parameters
    for param in params:
        if '-nosave' in param:
            toSave = False
        elif '-noprint' in param:
            toPrint = False
        elif '-plot' in param:
            toPlot = True
        elif '-corpus' in param:
            corpus = param.split('=')[1].strip()
        elif '-startYear' in param:
            startYear = int(param.split('=')[1])
        elif '-endYear' in param:
            endYear = int(param.split('=')[1])
        elif '-smoothing' in param:
            smoothing = int(param.split('=')[1])
        elif '-caseInsensitive' in param:
            caseInsensitive = True
        elif '-alldata' in param:
            allData = True
        elif '-help' in param:
            printHelp = True
        else:
            print(('Did not recognize the following argument: %s' % param))
    if printHelp:
        print('See README file.')
    else:
        if '*' in query and caseInsensitive is True:
            caseInsensitive = False
            notifyUser = True
            warningMessage = "*NOTE: Wildcard and case-insensitive " + \
                             "searches can't be combined, so the " + \
                             "case-insensitive option was ignored."
        elif '_INF' in query and caseInsensitive is True:
            caseInsensitive = False
            notifyUser = True
            warningMessage = "*NOTE: Inflected form and case-insensitive " + \
                             "searches can't be combined, so the " + \
                             "case-insensitive option was ignored."
        else:
            notifyUser = False
        url, urlquery, df = getNgrams(query, corpus, startYear, endYear,
                                      smoothing, caseInsensitive)
        if not allData:
            if caseInsensitive is True:
                for col in df.columns:
                    if col.count('(All)') == 1:
                        df[col.replace(' (All)', '')] = df.pop(col)
                    elif col.count(':chi_') == 1 or corpus.startswith('chi_'):
                        pass
                    elif col.count(':ger_') == 1 or corpus.startswith('ger_'):
                        pass
                    elif col.count(':heb_') == 1 or corpus.startswith('heb_'):
                        pass
                    elif col.count('(All)') == 0 and col != 'year':
                        if '[' in urlquery:
                            urlquery = urlquery.replace('[','')
                            urlquery = urlquery.replace(']','')
                        if col not in urlquery.split(','):
                            df.pop(col)

            if '_INF' in query:
                for col in df.columns:
                    if '_INF' in col:
                        df.pop(col)
            if '*' in query:
                for col in df.columns:
                    if '*' in col:
                        df.pop(col)
        if toPrint:
            print((','.join(df.columns.tolist())))
            for row in df.iterrows():
                try:
                    print(('%d,' % int(row[1].values[0]) +
                           ','.join(['%.12f' % s for s in row[1].values[1:]])))
                except:
                    print((','.join([str(s) for s in row[1].values])))
        queries = ''.join(urlquery.replace(',', '_').split())
        if '*' in queries:
            queries = queries.replace('*', 'WILDCARD')
        if caseInsensitive is True:
            word_case = 'cI'
        else:
            word_case = 'cS'
        filename = '%s-%s-%d-%d-%d-%s.csv' % (queries, corpus, startYear,
                                              endYear, smoothing, word_case)
        if toSave:
            for col in df.columns:
                if '&gt;' in col:
                    df[col.replace('&gt;', '>')] = df.pop(col)
            df.to_csv(filename, index=False)
            print(('Data saved to %s' % filename))
        if toPlot:
            try:
                subprocess.call(['python', 'xkcd.py', filename])
            except:
                if not toSave:
                    print(('Currently, if you want to create a plot you ' +
                           'must also save the data. Rerun your query, ' +
                           'removing the -nosave option.'))
                else:
                    print(('Plotting Failed: %s' % filename))
        if notifyUser:
            print(warningMessage)
            
#
# Functions to read all our doublets .csv files
# and run + save queries from Google Ngram Viewer
#

def removeDiacritics(text):
    """
    Returns a string with all diacritics (aka non-spacing marks) removed.
    For example "Héllô" will become "Hello".
    Useful for comparing strings in an accent-insensitive fashion.
    """
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")

def wordToQuery(row):
    """ Convert a row from our doublets .csv files
    to queries on Google Ngram Viewer """
    words0 = [row.ortho_0]
    words1 = [row.ortho_1]
    words2 = [row.ortho_2]
    doublets = []
    
    for list in [words0,words1,words2]:
        for word in list:
            if word[0] != removeDiacritics(word[0]):
                list.append(removeDiacritics(word[0])+word[1:]) 
    
    for word0 in words0:

        for word1 in words1:
            if ('-' in word0) | ('-' in word1):
                if len(word0.split('-')) > 1:
                    string0 = '-'.join(word0.split('-'))
                else:
                    string0 = word0
                if len(word1.split('-')) > 1:
                    string1 = '-'.join(word1.split('-'))
                else:
                    string1 = word1
                doublets.append('[' + string0 + ' ' + string1 + ']')
            else:
                if row.ortho_0 in ['quels','quelles']:
                    if (row.gtag_1 == 'VERB') & (row.lemme_1 == 'avoir'):
                        row.gtag_0 = 'PRON'
                    if (row.gtag_1 == 'VERB') & (row.lemme_1 == 'être'):
                        row.gtag_0 = 'ADJ'
                    if (row.gtag_1 == 'NOUN'):
                        row.gtag_0 = 'DET'
                    if (row.gtag_1 == 'ADJ'):
                        row.gtag_0 = 'DET'
                doublets.append(word0 + '_' + row.gtag_0 + ' ' + word1 + '_' + row.gtag_1)
        
        for word2 in words2:
            if ('-' in word0) | ('-' in word2):
                if len(word0.split('-')) > 1:
                    string0 = '-'.join(word0.split('-'))
                else:
                    string0 = word0
                if len(word2.split('-')) > 1:
                    string2 = '-'.join(word2.split('-'))
                else:
                    string2 = word2
                doublets.append('[' + string0 + ' ' + string2 + ']')
            else:
                if row.ortho_0 in ['quels','quelles']:
                    if (row.gtag_2 == 'VERB') & (row.lemme_2 == 'avoir'):
                        row.gtag_0 = 'PRON'
                    if (row.gtag_2 == 'VERB') & (row.lemme_2 == 'être'):
                        row.gtag_0 = 'ADJ'
                    if (row.gtag_2 == 'NOUN'):
                        row.gtag_0 = 'DET'
                    if (row.gtag_2 == 'ADJ'):
                        row.gtag_0 = 'DET'
                doublets.append(word0 + '_' + row.gtag_0 + ' ' + word2 + '_' + row.gtag_2)

    return doublets

def getFrequenciesDoublets(): #path with doublets .csv files
    """ Runs queries on Google Ngram Viewer
    and saves data in individual files for each doublet """
    path = os.path.join(os.getcwd(), 'doublets')
    for root, dirs, files in os.walk(path):
        for file in files:
            doublets = pd.read_csv(os.path.join(path, file), keep_default_na=False, na_values=[''], sep=';')
            if len(doublets) > 0:
                for idx, row in doublets.iterrows():
                    queries = wordToQuery(row)
                    googleReq = ', '.join([query for query in queries]) +\
                                 ' '.join([' -corpus=fre_2019','-caseInsensitive','-endYear=2019','-smoothing=0'])
                    pathSave = os.path.join(path, 'raw-frequency-data', file[:-4])
                    if not os.path.exists(pathSave):
                        os.makedirs(pathSave)
                    os.chdir(pathSave)
                    runQuery(googleReq)
                    time.sleep(4)

getFrequenciesDoublets()