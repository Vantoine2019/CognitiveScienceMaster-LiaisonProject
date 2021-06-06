# -*- coding: utf-8 -*-

"""
Homophony due to liaison Project
Extraction of number of confusing sequences
Victor ANTOINE
"""

#
# Importing Libraries
# 

import pandas as pd
import os
import re

# 
# Constants
#

CONS = ['t', 'n', 'z', 'g', 'p', 'R', 'b', 'd', 'k', 'f', 'v', 's', 'S', 'Z', 'm', 'N', 'l', 'x', 'G']
VERBS_EN = pd.read_csv('resources\\verbs-en.csv').verb_en.to_list() #Verbs that can follow 'en'
VERBS_ETRE = pd.read_csv('resources\\verbs-etre.csv').verb_with_aux_etre.to_list() #Verbs using 'être' in passé composé
MODAUX = ['devoir','falloir','pouvoir','vouloir']

COLUMNS = ['ortho', 'phon', 'lemme', 'cgram', 'genre', 'nombre','infover','cgramortho','freqfilms2','islem','p_cvcv']
COLUMNS_0 = ['{}_0'.format(a) for a in COLUMNS] #Columns for the words 1 e.g. 'petit'
COLUMNS_1 = ['{}_1'.format(a) for a in COLUMNS] #Columns for one word of a minimal pair
COLUMNS_2 = ['{}_2'.format(a) for a in COLUMNS] #Columns for the other word of a minimal pair

    # Words1
W1_n = pd.read_csv('resources\\w1-n.csv')
W1_p = pd.read_csv('resources\\w1-p.csv')    
W1_R = pd.read_csv('resources\\w1-R.csv')    
W1_z = pd.read_csv('resources\\w1-z.csv')    
W1_t = pd.read_csv('resources\\w1-t.csv')    
W1_g = pd.read_csv('resources\\w1-g.csv') 

    # Minimal pairs of Words2
PAIRS = pd.read_csv('resources\\minimal-pairs.csv')
PAIRS.loc[PAIRS[PAIRS.phon_2 == 'n@'].index,['ortho_2','lemme_2']] = 'nan'

# 
# Helper functions for creation and selection of confusing sequences
# 

# df is DataFrame
# columns is a list of string (duplicates declared based on those columns)
# name is the name of the created column

def duplicate(df, columns, name='duplicate'):
    """ Adds a column filled with 0 and 1
    1 means the row is a duplicate """
    df[name] = df.duplicated(columns).astype(int)

    #
    # Functions for DataFrame of words 1
    #

# dfW1 is a DataFrame of Words1
# category is a string
# ortho is a list of string(s)
# lemme is list of strings(s)

def selectWords1(dfW1, category, ortho=None, lemme=None):
    """ Selects specific words 1 """
    w1 = dfW1[dfW1.cgram_0 == category]
    if ortho != None:
        w1 = w1[w1.ortho_0.isin(ortho)]
    if lemme != None:
        w1 = w1[w1.lemme_0.isin(lemme)]
    return w1

    #
    # Functions for DataFrame of minimal pairs of words 2
    #

# mp is a DataFrame of minimal pairs of Words 2
# categories is a list of strings
# category is a string
# modes is a string (possible regex)
# number is a string
# gender is a string

def catGram(mp, categories):
    """ Selects the grammatical categories of the minimal pairs """
    pairs = mp[mp.cgram_1.isin(categories) & mp.cgram_2.isin(categories)]
    return pairs

def catVerb(mp, modes):
    """ Selects the modes of a minimal pairs with at least one verb """
    pairs = mp[mp.infover_1.str.contains(modes,na=True) & mp.infover_2.str.contains(modes,na=True)]
    return pairs

def verbWithAuxAvoir(mp):
    """ Select the minimal pairs that use the auxiliary 'avoir' in passé composé """
    dropouts_1 = list(mp.loc[(mp.infover_1.str.contains('par:pas')) & (mp.lemme_1.isin(VERBS_ETRE))].index)
    dropouts_2 = list(mp.loc[(mp.infover_2.str.contains('par:pas')) & (mp.lemme_2.isin(VERBS_ETRE))].index)
    pairs = mp.drop(list(set(dropouts_1 + dropouts_2)))
    return pairs
 
def restrictGender(mp, category, gender):
    """ Selects the minimal pairs that have a given gender
    For example, allows one to only keep pairs with masculine entries """
    dropouts_1 = list(mp.loc[(mp.cgram_1 == category) & (~mp.genre_1.str.contains(gender,na=True))].index)
    dropouts_2 = list(mp.loc[(mp.cgram_2 == category) & (~mp.genre_2.str.contains(gender,na=True))].index)
    pairs = mp.drop(list(set(dropouts_1 + dropouts_2)))
    return pairs

def restrictNumber(mp, category, number):
    """ Selects the minimal pairs that have a given number
    For example, allows one to only keep pairs with plural entries """
    dropouts_1 = list(mp.loc[(mp.cgram_1 == category) & (~mp.nombre_1.str.contains(number,na=True))].index)
    dropouts_2 = list(mp.loc[(mp.cgram_2 == category) & (~mp.nombre_2.str.contains(number,na=True))].index)
    pairs = mp.drop(list(set(dropouts_1 + dropouts_2)))
    return pairs

def pairsAgreeGender(mp):
    """ Selects the minimal pairs that agree in gender, i.e. 
    the pairs with two entries of identical gender.
    For example amis (masc) / tamis (masc) is kept. """
    dropouts_1 = list(mp.loc[(mp.genre_1 == 'm') & (mp.genre_2 == 'f')].index)
    dropouts_2 = list(mp.loc[(mp.genre_1 == 'f') & (mp.genre_2 == 'm')].index)
    pairs = mp.drop(list(set(dropouts_1 + dropouts_2)))
    return pairs

def pairsAgreeNumber(mp):
    """ Selects the minimal pairs that agree in number, i.e. 
    the pairs with two entries of identical number.
    For example ami (sing) / tamis (sing) is kept. """
    dropouts_1 = list(mp.loc[(mp.nombre_1 == 's') & (mp.nombre_2 == 'p')].index)
    dropouts_2 = list(mp.loc[(mp.nombre_1 == 'p') & (mp.nombre_2 == 's')].index)
    pairs = mp.drop(list(set(dropouts_1 + dropouts_2)))
    return pairs

def pairsAgreeGperson(mp):
    """ Selects the minimal pairs that agree in grammatical person
    For example entre (3pers.sing) / rentre (3pers.sing) is kept. """
    p = re.compile('[123][sp]')
    mp = mp.reset_index(drop=True)
    dropouts = []
    for row in range(len(mp)):
        pair = mp.loc[row]
        gperson_1 = set(p.findall(pair.infover_1))
        gperson_2 = set(p.findall(pair.infover_2))
        if set(gperson_1).isdisjoint(gperson_2) == True:
            dropouts.append(row)
    pairs = mp.drop(dropouts)
    pairs = pairs.reset_index(drop=True)
    return pairs

    #
    # Functions for sequences (combination of a Word 1 + a minimal pair of Words 2)
    #
    
# dfW1 is a DataFrame of Words1
# mp is a DataFrame of minimal pairs of Words 2
# seq is a DataFrame of sequences

def createSequences(dfW1, mp):
    """ Create a DataFrame of sequences from a Dataframe 
    of Words 1 and a Dataframe of minimal pairs of Words 2 """
    sequences = pd.DataFrame(columns = COLUMNS_0 + COLUMNS_1 + COLUMNS_2)
    if len(mp) != 0:
        for w1 in range(len(dfW1)):
            row_w1 = pd.DataFrame([dfW1.iloc[w1]])
            df_w1 = pd.concat([row_w1]*len(mp),ignore_index=True)
            new_seqs = pd.DataFrame(df_w1).join(mp)
            sequences = sequences.append(new_seqs,sort=False,ignore_index=True)
    return sequences

def sequencesAgreeGender(seq):
    """ Selects the sequences for which word 1 agrees
    in gender with the words 2 of the minimal pair """
    dropouts_1 = list(seq.loc[(seq.genre_0 == 'm') & (seq.genre_1 == 'f')].index)
    dropouts_2 = list(seq.loc[(seq.genre_0 == 'm') & (seq.genre_2 == 'f')].index)
    dropouts_3 = list(seq.loc[(seq.genre_0 == 'f') & (seq.genre_1 == 'm')].index)
    dropouts_4 = list(seq.loc[(seq.genre_0 == 'f') & (seq.genre_2 == 'm')].index)
    pairs = seq.drop(list(set(dropouts_1 + dropouts_2 + dropouts_3 + dropouts_4)))
    return pairs

def sequencesAgreeNumber(seq):
    """ Selects the sequences for which word 1 agrees
    in number with the words 2 of the minimal pair """
    dropouts_1 = list(seq.loc[(seq.nombre_0 == 's') & (seq.nombre_1 == 'p')].index)
    dropouts_2 = list(seq.loc[(seq.nombre_0 == 's') & (seq.nombre_2 == 'p')].index)
    dropouts_3 = list(seq.loc[(seq.nombre_0 == 'p') & (seq.nombre_1 == 's')].index)
    dropouts_4 = list(seq.loc[(seq.nombre_0 == 'p') & (seq.nombre_2 == 's')].index)
    pairs = seq.drop(list(set(dropouts_1 + dropouts_2 + dropouts_3 + dropouts_4)))
    return pairs

def sequencesAgreeVerbWithAdjProPer(seq):
    """ Selects sequences where word 1 is a verb and word 2 is a personal pronoun that can follow it.
    For example, 'sont-ils' is possible in French but not *'sont-il' """
    p_sing = re.compile('[123]s')
    p_plural = re.compile('[123]p')
    seq = seq.reset_index(drop=True)
    dropouts = []
    for row in range(len(seq)):
        sequence = seq.loc[row]
        gperson_sing_w1 = set(p_sing.findall(sequence.infover_0))
        gperson_plural_w1 = set(p_plural.findall(sequence.infover_0))
        if (len(gperson_sing_w1) != 0) & (len(gperson_plural_w1) == 0):
            if ((sequence.cgram_1 in ['ADJ','PRO:per']) & (sequence.nombre_1 == 'p'))\
                |((sequence.cgram_2 in ['ADJ','PRO:per']) & (sequence.nombre_2 == 'p')):
                dropouts.append(row)
        if (len(gperson_plural_w1) != 0) & (len(gperson_sing_w1) == 0):
            if ((sequence.cgram_1 in ['ADJ','PRO:per']) & (sequence.nombre_1 == 's'))\
                |((sequence.cgram_2 in ['ADJ','PRO:per']) & (sequence.nombre_2 == 's')):
                dropouts.append(row)
    pairs = seq.drop(dropouts)
    pairs = pairs.reset_index(drop=True)
    return pairs

def sequencesAgreeProPerWithVerb(seq):
    """ Selects sequences where word 1 is a personal pronoun and word 2 is a verb that can follow it.
    For example, 'il aime' is possible in French but not *'il aiment' """
    seq = seq.reset_index(drop=True)
    dropouts = []
    p = re.compile('[123][sp]')
    if len(seq) != 0:
        for row in range(len(seq)):
            sequence = seq.loc[row]
            gpersons1= p.findall(sequence.infover_1)
            gpersons2= p.findall(sequence.infover_2)
            if sequence.ortho_0 == 'nous':
                if not (('1p' in gpersons1) & ('1p' in gpersons2)):
                    dropouts.append(row)
            if sequence.ortho_0 == 'vous':
                if not (('2p' in gpersons1) & ('2p' in gpersons2)):
                    dropouts.append(row)
            if (sequence.ortho_0 == 'ils') | (sequence.ortho_0 == 'elles'):
                if not (('3p' in gpersons1) & ('3p' in gpersons2)):
                    dropouts.append(row)
    pairs = seq.drop(dropouts)
    pairs = pairs.reset_index(drop=True)
    return pairs

    # 
    # Functions to select the confusing sequences for a given liaison consonant
    # 

# Each function creates and selects confusing sequences based on a given consonant
# e.g. sequences_R with cons='R' gives the confusing 
# sequences for real French (dernier achat / rachat)
# e.g. sequences_R with cons='f' gives the confusing
# sequences for an alternative French (dernier acteur / facteur)
# see appendix in thesis for more information

# df is a DataFrame of minimal pairs of Words 2
# cons is a string


def sequences_p(df, cons):
    pairs_p = df[df.phon_2.str[0] == cons]

    #Word 1 = ADV (trop, beaucoup)
    w1_p_ADV = selectWords1(W1_p, 'ADV')
        #combinations of ADJ(all)/PRE
    pairs_p1 = catGram(pairs_p, ['PRE','ADJ'])
    pairs_p1 = pairsAgreeGender(pairs_p1)
    pairs_p1 = pairsAgreeNumber(pairs_p1)
        #combinations of VER(inf)
    pairs_p2 = catGram(pairs_p, ['VER'])
    pairs_p2 = catVerb(pairs_p2, 'inf')
        #combinations of VER(par:pas)
    pairs_p3 = catGram(pairs_p, ['VER'])
    pairs_p3 = catVerb(pairs_p3, 'par:pas')
    pairs_p3 = restrictGender(pairs_p3, 'VER', 'm')
    pairs_p3 = restrictNumber(pairs_p3, 'VER', 's')
        #sequences
    pairs_ADV = pd.concat([pairs_p1,pairs_p2,pairs_p3],ignore_index=True)
    pairs_ADV = pairs_ADV.reset_index(drop=True)
    sequences_ADV = createSequences(w1_p_ADV,pairs_ADV)
    return sequences_ADV

def sequences_R(df, cons):
    pairs_R = df[df.phon_2.str[0] == cons]

    #Word 1 = ADJ (premier, dernier, léger)
    w1_R_ADJ = selectWords1(W1_R, 'ADJ')
        #combinations of NOM(m.s.)
    pairs_ADJ = catGram(pairs_R, ['NOM'])
    pairs_ADJ = restrictGender(pairs_ADJ,'NOM','m')
    pairs_ADJ = restrictNumber(pairs_ADJ,'NOM','s')
        #sequences
    pairs_ADJ = pairs_ADJ.reset_index(drop=True)
    sequences_ADJ = createSequences(w1_R_ADJ,pairs_ADJ)
    return sequences_ADJ

def sequences_g(df, cons):
    pairs_g = df[df.phon_2.str[0] == cons]
    
    #Word 1 = ADJ (long)
    w1_g_ADJ = selectWords1(W1_g, 'ADJ')
        #combinations of NOM(m.s.)
    pairs_ADJ = catGram(pairs_g, ['NOM'])
    pairs_ADJ = restrictGender(pairs_ADJ,'NOM','m')
    pairs_ADJ = restrictNumber(pairs_ADJ,'NOM','s')
        #sequences
    pairs_ADJ = pairs_ADJ.reset_index(drop=True)
    sequences_ADJ = createSequences(w1_g_ADJ,pairs_ADJ)
    return sequences_ADJ

def sequences_n(df, cons):
    pairs_n = df[df.phon_2.str[0] == cons]
    
    #Word 1 = ADJ
    w1_n_ADJ = selectWords1(W1_n, 'ADJ')
        #combinations of NOM(m.s.)
    pairs_ADJ = catGram(pairs_n, ['NOM'])
    pairs_ADJ = restrictGender(pairs_ADJ,'NOM','m')
    pairs_ADJ = restrictNumber(pairs_ADJ,'NOM','s')
        #sequences
    pairs_ADJ = pairs_ADJ.reset_index(drop=True)
    sequences_ADJ = createSequences(w1_n_ADJ,pairs_ADJ)
    
    #Word 1 = ADJ:ind
    w1_n_ADJind = selectWords1(W1_n, 'ADJ:ind')
        #combinations of NOM(m.s.)/ADJ(m.s.)(pre-nom)
    pairs_ADJind = catGram(pairs_n, ['NOM','ADJ'])
    pairs_ADJind = restrictGender(pairs_ADJind,'NOM','m')
    pairs_ADJind = restrictGender(pairs_ADJind,'ADJ','m')
    pairs_ADJind = restrictNumber(pairs_ADJind,'NOM','s')
    pairs_ADJind = restrictNumber(pairs_ADJind,'ADJ','s')
        #sequences
    pairs_ADJind = pairs_ADJind.reset_index(drop=True)
    sequences_ADJind = createSequences(w1_n_ADJind,pairs_ADJind)
    
    #Word 1 = ADJ:num
    w1_n_ADJnum = selectWords1(W1_n, 'ADJ:num')
        #combinations of NOM(m.s.)/ADJ(m.s.)(pre-nom)
    pairs_ADJnum = catGram(pairs_n, ['NOM','ADJ'])
    pairs_ADJnum = restrictGender(pairs_ADJnum,'NOM','m')
    pairs_ADJnum = restrictGender(pairs_ADJnum,'ADJ','m')
    pairs_ADJnum = restrictNumber(pairs_ADJnum,'NOM','s')
    pairs_ADJnum = restrictNumber(pairs_ADJnum,'ADJ','s')
        #sequences
    pairs_ADJnum = pairs_ADJnum.reset_index(drop=True)
    sequences_ADJnum = createSequences(w1_n_ADJnum,pairs_ADJnum)
    
    #Word 1 = ADJ:pos
    w1_n_ADJpos = selectWords1(W1_n, 'ADJ:pos')
        #combinations of NOM(m.s.)/ADJ(m.s.)(pre-nom)
    pairs_ADJpos = catGram(pairs_n, ['NOM','ADJ'])
    pairs_ADJpos = restrictGender(pairs_ADJpos,'NOM','m')
    pairs_ADJpos = restrictGender(pairs_ADJpos,'ADJ','m')
    pairs_ADJpos = restrictNumber(pairs_ADJpos,'NOM','s')
    pairs_ADJpos = restrictNumber(pairs_ADJpos,'ADJ','s')
        #sequences
    pairs_ADJpos = pairs_ADJpos.reset_index(drop=True)
    sequences_ADJpos = createSequences(w1_n_ADJpos,pairs_ADJpos)

    #Word 1 = ART:ind
    w1_n_ARTind = selectWords1(W1_n, 'ART:ind')
        #combinations of NOM(m.s.)/ADJ(m.s.)(pre-nom)
    pairs_ARTind = catGram(pairs_n, ['NOM','ADJ'])
    pairs_ARTind = restrictGender(pairs_ARTind,'NOM','m')
    pairs_ARTind = restrictGender(pairs_ARTind,'ADJ','m')
    pairs_ARTind = restrictNumber(pairs_ARTind,'NOM','s')
    pairs_ARTind = restrictNumber(pairs_ARTind,'ADJ','s')
        #sequences
    pairs_ARTind = pairs_ARTind.reset_index(drop=True)
    sequences_ARTind = createSequences(w1_n_ARTind,pairs_ARTind)

    #Word 1 = ADV (bien)
    w1_n_ADVbien = selectWords1(W1_n, 'ADV', lemme=['bien'])
        #combinations of ADJ(all)/PRE
    pairs_n1 = catGram(pairs_n, ['PRE','ADJ'])
    pairs_n1 = pairsAgreeGender(pairs_n1)
    pairs_n1 = pairsAgreeNumber(pairs_n1)
        #combinations of PRO:per
    pairs_n2 = catGram(pairs_n, ['PRO:per'])
        #combinations of VER(inf)
    pairs_n3 = catGram(pairs_n, ['VER'])
    pairs_n3 = catVerb(pairs_n3, 'inf')
        #combinations of VER(par:pas)
    pairs_n4 = catGram(pairs_n, ['VER'])
    pairs_n4 = catVerb(pairs_n4, 'par:pas')
    pairs_n4 = restrictGender(pairs_n4, 'VER', 'm')
    pairs_n4 = restrictNumber(pairs_n4, 'VER', 's')
        #sequences
    pairs_ADVbien = pd.concat([pairs_n1,pairs_n2,pairs_n3,pairs_n4],ignore_index=True)
    pairs_ADVbien = pairs_ADVbien.reset_index(drop=True)
    sequences_ADVbien = createSequences(w1_n_ADVbien,pairs_ADVbien)
    
    #Word 1 = ADV (non)
    w1_n_ADVnon = selectWords1(W1_n, 'ADV', lemme=['non'])
        #combinations of ADJ(all)
    pairs_ADVnon = catGram(pairs_n, ['ADJ'])
    pairs_ADVnon = pairsAgreeGender(pairs_ADVnon)
    pairs_ADVnon = pairsAgreeNumber(pairs_ADVnon)
        #sequences
    pairs_ADVnon = pairs_ADVnon.reset_index(drop=True)
    sequences_ADVnon = createSequences(w1_n_ADVnon,pairs_ADVnon)
    
    #Word 1 = PRE (en)
    w1_n_PRE = selectWords1(W1_n, 'PRE')
       #combinations of PRO:per/ADJ:ind/ART:ind/VER(par:pre)
    pairs_n1 = catGram(pairs_n, ['ADJ:ind','ART:ind','PRO:per','VER'])
    pairs_n1 = catVerb(pairs_n1, 'par:pre')
        #combinations of NOM(all)
    pairs_n2 = catGram(pairs_n, ['NOM'])
        #sequences
    pairs_PRE = pd.concat([pairs_n1,pairs_n2],ignore_index=True)
    pairs_PRE = pairs_PRE.reset_index(drop=True)
    sequences_PRE = createSequences(w1_n_PRE,pairs_PRE)
    
    #Word 1 = PRO:ind (rien)
    w1_n_PROind = selectWords1(W1_n, 'PRO:ind')
        #combinations of PRE
    pairs_n1 = catGram(pairs_n, ['PRE'])
        #combinations of VER(inf)
    pairs_n2 = catGram(pairs_n, ['VER'])
    pairs_n2 = catVerb(pairs_n2, 'inf')
        #combinations of VER(par:pas)
    pairs_n3 = catGram(pairs_n, ['VER'])
    pairs_n3 = catVerb(pairs_n3, 'par:pas')
    pairs_n3 = restrictGender(pairs_n3, 'VER', 'm')
    pairs_n3 = restrictNumber(pairs_n3, 'VER', 's')
        #sequences
    pairs_PROind = pd.concat([pairs_n1,pairs_n2,pairs_n3],ignore_index=True)
    pairs_PROind = pairs_PROind.reset_index(drop=True)
    sequences_PROind = createSequences(w1_n_PROind,pairs_PROind)

    #Word 1 = PRO:per (on)
    w1_n_PROperon = selectWords1(W1_n, 'PRO:per', lemme=['on'])
        #combinations of VER(≠par≠inf,3s)/AUX(≠par≠inf≠imp,3s)
    pairs_PROperon = catGram(pairs_n, ['VER','AUX'])
    pairs_PROperon = catVerb(pairs_PROperon, 'ind:[a-z]{3}:3s|cnd:[a-z]{3}:3s|sub:[a-z]{3}:3s')
        #sequences
    pairs_PROperon = pairs_PROperon.reset_index(drop=True)
    sequences_PROperon = createSequences(w1_n_PROperon,pairs_PROperon)
    
    #Word 1 = PRO:per (en)
    w1_n_PROperen = selectWords1(W1_n, 'PRO:per', lemme=['en'])
        #combinations of VER(≠par≠inf)/AUX(≠par≠inf≠imp)
    pairs_PROperen = catGram(pairs_n, ['VER','AUX'])
    pairs_PROperen = catVerb(pairs_PROperen, 'ind|cnd|sub')
    pairs_PROperen = pairs_PROperen[(pairs_PROperen.lemme_1.isin(VERBS_EN)) &\
                                    (pairs_PROperen.lemme_2.isin(VERBS_EN))]
    pairs_PROperen = pairsAgreeGperson(pairs_PROperen)
        #sequences
    pairs_PROperen = pairs_PROperen.reset_index(drop=True)
    sequences_PROperen = createSequences(w1_n_PROperen,pairs_PROperen)
    
    #All sequences
    sequences = pd.concat([sequences_ADJ,sequences_ADJind,sequences_ADJnum,\
                           sequences_ADJpos,sequences_ARTind,sequences_ADVbien,\
                           sequences_ADVnon,sequences_PRE,sequences_PROind,\
                           sequences_PROperon,sequences_PROperen],\
                           sort=False,ignore_index=True)
    return sequences

def sequences_t(df, cons):
    pairs_t = df[df.phon_2.str[0] == cons]
    
    #Word 1 = ADJ
    w1_t_ADJ = selectWords1(W1_t, 'ADJ')
        #combinations of NOM(m.s.)
    pairs_ADJ = catGram(pairs_t, ['NOM'])
    pairs_ADJ = restrictGender(pairs_ADJ,'NOM','m')
    pairs_ADJ = restrictNumber(pairs_ADJ,'NOM','s')
        #sequences
    pairs_ADJ = pairs_ADJ.reset_index(drop=True)
    sequences_ADJ = createSequences(w1_t_ADJ,pairs_ADJ)     

    #Word 1 = ADJ:ind (maint)
    w1_t_ADJindmaint = selectWords1(W1_t, 'ADJ:ind', lemme=['maint'])
        #combinations of NOM(m.s.)
    pairs_ADJindmaint = catGram(pairs_t, ['NOM'])
    pairs_ADJindmaint = restrictGender(pairs_ADJindmaint,'NOM','m')
    pairs_ADJindmaint = restrictNumber(pairs_ADJindmaint,'NOM','s')
        #sequences
    pairs_ADJindmaint = pairs_ADJindmaint.reset_index(drop=True)
    sequences_ADJindmaint = createSequences(w1_t_ADJindmaint,pairs_ADJindmaint)
    
    #Word 1 = ADJ:ind (tout)
    w1_t_ADJindtout = selectWords1(W1_t, 'ADJ:ind', lemme=['tout'])
        #combinations of NOM(m.s.)/ART:ind(m.s.)/ADJ(m.s.)(pre-nom)
    pairs_ADJindtout = catGram(pairs_t, ['NOM','ART:ind','ADJ'])
    for category in ['NOM','ART:ind','ADJ']:
        pairs_ADJindtout = restrictGender(pairs_ADJindtout,category,'m')
        pairs_ADJindtout = restrictNumber(pairs_ADJindtout,category,'s')
        #sequences
    pairs_ADJindtout = pairs_ADJindtout.reset_index(drop=True)
    sequences_ADJindtout = createSequences(w1_t_ADJindtout,pairs_ADJindtout)
    
    #Word 1 = ADV (quand)
    w1_t_ADVquand = selectWords1(W1_t, 'ADV', lemme=['quand'])
        #combinations of AUX(ind,cnd)
    pairs_ADVquand = catGram(pairs_t, ['AUX'])
    pairs_ADVquand = catVerb(pairs_ADVquand, 'ind|cnd')
        #sequences
    pairs_ADVquand = pairs_ADVquand.reset_index(drop=True)
    sequences_ADVquand = createSequences(w1_t_ADVquand,pairs_ADVquand)
    
    #Word 1 = ADV (tant)
    w1_t_ADVtant = selectWords1(W1_t, 'ADV', lemme=['tant'])
        #combinations of ADJ(all)
    pairs_t1 = catGram(pairs_t, ['ADJ'])
    pairs_t1 = pairsAgreeGender(pairs_t1)
    pairs_t1 = pairsAgreeNumber(pairs_t1)
        #combinations of VER(par:pas)
    pairs_t2 = catGram(pairs_t, ['VER'])
    pairs_t2 = catVerb(pairs_t2, 'par:pas')
    pairs_t2 = restrictGender(pairs_t2, 'VER', 'm')
    pairs_t2 = restrictNumber(pairs_t2, 'VER', 's')
        #sequences
    pairs_ADVtant = pd.concat([pairs_t1,pairs_t2],ignore_index=True)
    pairs_ADVtant = pairs_ADVtant.reset_index(drop=True)
    sequences_ADVtant = createSequences(w1_t_ADVtant,pairs_ADVtant)
    
    #Word 1 = ADV (tout)
    w1_t_ADVtout = selectWords1(W1_t, 'ADV', lemme=['tout'])
        #combinations of ADJ(all)/ADV/PRE
    pairs_t1 = catGram(pairs_t, ['ADJ','ADV','PRE'])
    pairs_t1 = pairsAgreeGender(pairs_t1)
    pairs_t1 = pairsAgreeNumber(pairs_t1)
        #combinations of VER(par:pas)
    pairs_t2 = catGram(pairs_t, ['VER'])
    pairs_t2 = catVerb(pairs_t2, 'par:pas')
    pairs_t2 = restrictGender(pairs_t2, 'VER', 'm')
    pairs_t2 = restrictNumber(pairs_t2, 'VER', 's')
        #sequences
    pairs_ADVtout = pd.concat([pairs_t1,pairs_t2],ignore_index=True)
    pairs_ADVtout = pairs_ADVtout.reset_index(drop=True)
    sequences_ADVtout = createSequences(w1_t_ADVtout,pairs_ADVtout)
    
    #Word 1 = PRO:rel (dont)
    w1_t_PROrel = selectWords1(W1_t, 'PRO:rel')
        #combinations of ADJ:ind/ADJ:num/ART:ind/PRO:ind/PRO:per/AUX(ind,cnd,3p)
    pairs_PROrel = catGram(pairs_t, ['ADJ:ind','ADJ:num','ART:ind','PRO:ind','PRO:per','AUX'])
    pairs_PROrel = catVerb(pairs_PROrel, 'ind|cnd')
    pairs_PROrel = catVerb(pairs_PROrel, '3p')
        #sequences
    pairs_PROrel = pairs_PROrel.reset_index(drop=True)
    sequences_PROrel = createSequences(w1_t_PROrel,pairs_PROrel)
    
    #Word 1 = CON (quand)
    w1_t_CON = selectWords1(W1_t, 'CON')
        #combinations of ADJ:ind/ADJ:num/ART:ind/PRO:ind/PRO:per
    pairs_CON = catGram(pairs_t, ['ADJ:ind','ADJ:num','ART:ind','PRO:ind','PRO:per'])
        #sequences 
    pairs_CON = pairs_CON.reset_index(drop=True)
    sequences_CON = createSequences(w1_t_CON,pairs_CON)
    
    #Word 1 = VER(≠par≠inf≠imp, not modaux)
    NOT_MODAUX = [lemme for lemme in list(set(W1_t.lemme_0.to_list())) if lemme not in MODAUX]
    w1_t_VERflexnotmod = selectWords1(W1_t, 'VER', lemme=NOT_MODAUX)
    w1_t_VERflexnotmod = w1_t_VERflexnotmod[w1_t_VERflexnotmod.infover_0.str.contains('ind|cnd|sub', na=True)]
        #combinations of PRO:per
    pairs_VERflexnotmod = catGram(pairs_t, ['PRO:per'])
        #sequences
    pairs_VERflexnotmod = pairs_VERflexnotmod.reset_index(drop=True)
    sequences_VERflexnotmod = createSequences(w1_t_VERflexnotmod,pairs_VERflexnotmod)
    sequences_VERflexnotmod = sequencesAgreeVerbWithAdjProPer(sequences_VERflexnotmod)
    
    #Word 1 = VER(≠par≠inf≠imp, modaux)
    w1_t_VERflexmod = selectWords1(W1_t, 'VER', lemme=MODAUX)
    w1_t_VERflexmod = w1_t_VERflexmod[w1_t_VERflexmod.infover_0.str.contains('ind|cnd|sub', na=True)]    
        #combinations of PRO:per
    pairs_t1 = catGram(pairs_t, ['PRO:per'])
        #combinations of VER(inf)
    pairs_t2 = catGram(pairs_t, ['VER'])
    pairs_t2 = catVerb(pairs_t2, 'inf')
        #sequences
    pairs_VERflexmod = pd.concat([pairs_t1,pairs_t2],ignore_index=True)
    pairs_VERflexmod = pairs_VERflexmod.reset_index(drop=True)
    sequences_VERflexmod = createSequences(w1_t_VERflexmod,pairs_VERflexmod)
    sequences_VERflexmod = sequencesAgreeVerbWithAdjProPer(sequences_VERflexmod)
    
    #Word 1 = VER(par:pre, not modaux)
    w1_t_VERparnotmod = selectWords1(W1_t, 'VER', lemme=NOT_MODAUX)
    w1_t_VERparnotmod = w1_t_VERparnotmod[w1_t_VERparnotmod.infover_0.str.contains('par:pre', na=True)]
        #combinations of ADJ:ind/ADJ:num/ART:ind/PRE
    pairs_VERparnotmod = catGram(pairs_t, ['ADJ:ind','ADJ:num','ART:ind','PRE'])
        #sequences
    pairs_VERparnotmod = pairs_VERparnotmod.reset_index(drop=True)
    sequences_VERparnotmod = createSequences(w1_t_VERparnotmod,pairs_VERparnotmod)
    
    #Word 1 = VER(par:pre, modaux)
    w1_t_VERparmod = selectWords1(W1_t, 'VER', lemme=MODAUX)
    w1_t_VERparmod = w1_t_VERparmod[w1_t_VERparmod.infover_0.str.contains('par:pre', na=True)]
        #combinations of ADJ:ind/ADJ:num/ART:ind/VER(inf)
    pairs_VERparmod = catGram(pairs_t, ['ADJ:ind','ADJ:num','ART:ind','VER'])
    pairs_VERparmod = catVerb(pairs_VERparmod, 'inf')
        #sequences
    pairs_VERparmod = pairs_VERparmod.reset_index(drop=True)
    sequences_VERparmod = createSequences(w1_t_VERparmod,pairs_VERparmod)
    
    #Word 1 = AUX (être)
    w1_t_AUXetre = selectWords1(W1_t, 'VER', lemme=['être'])
        #combinations of ADJ(all)/ADV/PRE/ART:ind
    pairs_AUXetre = catGram(pairs_t, ['ADJ','ADV','PRE','ART:ind'])
    pairs_AUXetre = pairsAgreeNumber(pairs_AUXetre)
    pairs_AUXetre = pairsAgreeGender(pairs_AUXetre)
        #sequences
    pairs_AUXetre = pairs_AUXetre.reset_index(drop=True)
    sequences_AUXetre = createSequences(w1_t_AUXetre,pairs_AUXetre)
    sequences_AUXetre = sequencesAgreeVerbWithAdjProPer(sequences_AUXetre)
    
    #Word 1 = AUX (avoir)
    w1_t_AUXavoir = selectWords1(W1_t, 'VER', lemme=['avoir'])
        #combinations of ADV/ART:ind/VER(par:pas)
    pairs_AUXavoir = catGram(pairs_t, ['VER','ADV','ART:ind'])
    pairs_AUXavoir = catVerb(pairs_AUXavoir, 'par:pas')
    pairs_AUXavoir = verbWithAuxAvoir(pairs_AUXavoir)
    pairs_AUXavoir = restrictGender(pairs_AUXavoir, 'VER', 'm')
    pairs_AUXavoir = restrictNumber(pairs_AUXavoir, 'VER', 's')
        #sequences 
    pairs_AUXavoir = pairs_AUXavoir.reset_index(drop=True)
    sequences_AUXavoir = createSequences(w1_t_AUXavoir,pairs_AUXavoir)
    
    #All sequences
    sequences = pd.concat([sequences_ADJ,sequences_ADJindmaint,sequences_ADJindtout,\
                           sequences_ADVquand,sequences_ADVtant,sequences_ADVtout,\
                           sequences_PROrel,sequences_CON,sequences_VERflexnotmod,\
                           sequences_VERflexmod,sequences_VERparnotmod,\
                           sequences_VERparmod,sequences_AUXetre,sequences_AUXavoir],\
                           ignore_index=True, sort=False)
    return sequences

def sequences_z(df, cons):
    pairs_z = df[df.phon_2.str[0] == cons]

    #Word 1 = ADJ
    w1_z_ADJ = selectWords1(W1_z, 'ADJ')
        #combinations of NOM(p.)
    pairs_ADJ = catGram(pairs_z, ['NOM'])
    pairs_ADJ = restrictNumber(pairs_ADJ,'NOM','p')
        #sequences
    pairs_ADJ = pairs_ADJ.reset_index(drop=True)
    sequences_ADJ = createSequences(w1_z_ADJ,pairs_ADJ)
    sequences_ADJ = sequencesAgreeGender(sequences_ADJ)
    
    #Word 1 = ADJ:ind
    w1_z_ADJind = selectWords1(W1_z, 'ADJ:ind')
        #combinations of ADJ(p.)(pre-nom)/NOM(p.)
    pairs_ADJind = catGram(pairs_z, ['NOM','ADJ'])
    pairs_ADJind = restrictNumber(pairs_ADJind, 'ADJ', 'p')
    pairs_ADJind = restrictNumber(pairs_ADJind, 'NOM', 'p')
        #sequences
    pairs_ADJind = pairs_ADJind.reset_index(drop=True)
    sequences_ADJind = createSequences(w1_z_ADJind,pairs_ADJind)
    sequences_ADJind = sequencesAgreeGender(sequences_ADJind)
    
    #Word 1 = ADJ:dem (ces)
    w1_z_ADJdem = selectWords1(W1_z, 'ADJ:dem')
        #combinations of ADJ(p.)(pre-nom)/NOM(p.)
    pairs_ADJdem = catGram(pairs_z, ['NOM','ADJ'])
    pairs_ADJdem = restrictNumber(pairs_ADJdem, 'ADJ', 'p')
    pairs_ADJdem = restrictNumber(pairs_ADJdem, 'NOM', 'p')
        #sequences
    pairs_ADJdem = pairs_ADJdem.reset_index(drop=True)
    sequences_ADJdem = createSequences(w1_z_ADJdem,pairs_ADJdem)
    
    #Word 1 = ADJ:num
    w1_z_ADJnum = selectWords1(W1_z, 'ADJ:num')
        #combinations of ADJ(p.)(pre-nom)/NOM(p.)
    pairs_ADJnum = catGram(pairs_z, ['NOM','ADJ'])
    pairs_ADJnum = restrictNumber(pairs_ADJnum, 'ADJ', 'p')
    pairs_ADJnum = restrictNumber(pairs_ADJnum, 'NOM', 'p')
        #sequences
    pairs_ADJnum = pairs_ADJnum.reset_index(drop=True)
    sequences_ADJnum = createSequences(w1_z_ADJnum,pairs_ADJnum)
    
    #Word 1 = ADJ:pos
    w1_z_ADJpos = selectWords1(W1_z, 'ADJ:pos')
        #combinations of ADJ(p.)(pre-nom)/NOM(p.)
    pairs_ADJpos = catGram(pairs_z, ['NOM','ADJ'])
    pairs_ADJpos = restrictNumber(pairs_ADJpos, 'ADJ', 'p')
    pairs_ADJpos = restrictNumber(pairs_ADJpos, 'NOM', 'p')
        #sequences
    pairs_ADJpos = pairs_ADJpos.reset_index(drop=True)
    sequences_ADJpos = createSequences(w1_z_ADJpos,pairs_ADJpos)
    
    #Word 1 = ART:def
    w1_z_ARTdef = selectWords1(W1_z, 'ART:def')
        #combinations of ADJ(p.)(pre-nom)/NOM(p.)
    pairs_ARTdef = catGram(pairs_z, ['NOM','ADJ'])
    pairs_ARTdef = restrictNumber(pairs_ARTdef, 'ADJ', 'p')
    pairs_ARTdef = restrictNumber(pairs_ARTdef, 'NOM', 'p')
        #sequences
    pairs_ARTdef = pairs_ARTdef.reset_index(drop=True)
    sequences_ARTdef = createSequences(w1_z_ARTdef,pairs_ARTdef)
        
    #Word 1 = ART:ind
    w1_z_ARTind = selectWords1(W1_z, 'ART:ind')
        #combinations of ADJ(p.)(pre-nom)/NOM(p.)
    pairs_ARTind = catGram(pairs_z, ['NOM','ADJ'])
    pairs_ARTind = restrictNumber(pairs_ARTind, 'ADJ', 'p')
    pairs_ARTind = restrictNumber(pairs_ARTind, 'NOM', 'p')
        #sequences
    pairs_ARTind = pairs_ARTind.reset_index(drop=True)
    sequences_ARTind = createSequences(w1_z_ARTind,pairs_ARTind)
       
    #Word 1 = ADJ:int
    w1_z_ADJint = selectWords1(W1_z, 'ADJ:int')
        #combinations of ADJ(p.)(pre-nom)/NOM(p.)/AUX(ind,cnd,3p)
    pairs_ADJint = catGram(pairs_z, ['NOM','ADJ','AUX'])
    pairs_ADJint = catVerb(pairs_ADJint, 'ind:[a-z]{3}:3p|cnd:[a-z]{3}:3p')
    pairs_ADJint = restrictNumber(pairs_ADJint, 'ADJ', 'p')
    pairs_ADJint = restrictNumber(pairs_ADJint, 'NOM', 'p')
        #sequences
    pairs_ADJint = pairs_ADJint.reset_index(drop=True)
    sequences_ADJint = createSequences(w1_z_ADJint,pairs_ADJint)
    sequences_ADJint = sequencesAgreeGender(sequences_ADJint)
    
    #Word 1 = ADV (pas)
    w1_z_ADVpas = selectWords1(W1_z, 'ADV', lemme=['pas'])
        #combinations of ADJ(all)/ART:ind
    pairs_z1 = catGram(pairs_z, ['ADJ','ART:ind'])
    pairs_z1 = pairsAgreeGender(pairs_z1)
    pairs_z1 = pairsAgreeNumber(pairs_z1)
        #combinations of VER(par:pas)/ART:ind
    pairs_z2 = catGram(pairs_z, ['VER','ART:ind'])
    pairs_z2 = catVerb(pairs_z2, 'par:pas')
    pairs_z2 = restrictGender(pairs_z2, 'VER', 'm')
    pairs_z2 = restrictNumber(pairs_z2, 'VER', 's')
        #sequences
    pairs_ADVpas = pd.concat([pairs_z1,pairs_z2],ignore_index=True)
    pairs_ADVpas = pairs_ADVpas.reset_index(drop=True)
    sequences_ADVpas = createSequences(w1_z_ADVpas,pairs_ADVpas)
    
    #Word 1 = ADV (not pas)
    not_pas = [lemme for lemme in list(set(W1_z.lemme_0.to_list())) if lemme != 'pas']    
    w1_z_ADVnotpas =  selectWords1(W1_z, 'ADV', lemme=not_pas)
        #combinations of ADJ(all)
    pairs_z1 = catGram(pairs_z, ['ADJ'])
    pairs_z1 = pairsAgreeGender(pairs_z1)
    pairs_z1 = pairsAgreeNumber(pairs_z1)
        #combinations of VER(par:pas)
    pairs_z2 = catGram(pairs_z, ['VER'])
    pairs_z2 = catVerb(pairs_z2, 'par:pas')
    pairs_z2 = restrictGender(pairs_z2, 'VER', 'm')
    pairs_z2 = restrictNumber(pairs_z2, 'VER', 's')
        #sequences
    pairs_ADVnotpas = pd.concat([pairs_z1,pairs_z2],ignore_index=True)
    pairs_ADVnotpas = pairs_ADVnotpas.reset_index(drop=True)
    sequences_ADVnotpas = createSequences(w1_z_ADVnotpas,pairs_ADVnotpas)
    
    #Word 1 = AUX (être)
    w1_z_AUXetre =  selectWords1(W1_z, 'AUX', lemme=['être'])
        #combinations of ADJ(all)/ADV/PRE/ART:ind
    pairs_AUXetre = catGram(pairs_z, ['ADJ','ADV','PRE','ART:ind'])
    pairs_AUXetre = pairsAgreeNumber(pairs_AUXetre)
        #sequences
    pairs_AUXetre = pairs_AUXetre.reset_index(drop=True)
    sequences_AUXetre = createSequences(w1_z_AUXetre,pairs_AUXetre)
    sequences_AUXetre = sequencesAgreeVerbWithAdjProPer(sequences_AUXetre)
        
    #Word 1 = AUX (avoir)
    w1_z_AUXavoir =  selectWords1(W1_z, 'AUX', lemme=['avoir'])
        #combinations of ADV/ART:ind/VER(par:pas)
    pairs_AUXavoir = catGram(pairs_z, ['ADV','VER','ART:ind'])
    pairs_AUXavoir = catVerb(pairs_AUXavoir, 'par:pas')
    pairs_AUXavoir = verbWithAuxAvoir(pairs_AUXavoir)
    pairs_AUXavoir = restrictGender(pairs_AUXavoir, 'VER', 'm')
    pairs_AUXavoir = restrictNumber(pairs_AUXavoir, 'VER', 's')
        #sequences
    pairs_AUXavoir = pairs_AUXavoir.reset_index(drop=True)
    sequences_AUXavoir = createSequences(w1_z_AUXavoir,pairs_AUXavoir)
    
    #Word 1 = CON (mais)
    w1_z_CON =  selectWords1(W1_z, 'CON')
        #combinations of ADJ:ind/ADJ:num/ART:ind/PRE/VER(inf)/PRO:per/PRO:ind
    pairs_CON = catGram(pairs_z, ['ADJ:ind','ADJ:num','ART:ind','PRE','VER','PRO:per','PRO:ind'])
    pairs_CON = catVerb(pairs_CON, 'inf')
        #sequences
    pairs_CON = pairs_CON.reset_index(drop=True)
    sequences_CON = createSequences(w1_z_CON,pairs_CON)
    
    #Word 1 = NOM
    w1_z_NOM =  selectWords1(W1_z, 'NOM')
        #combinations of ADJ(p.)(post-nom)
    pairs_NOM = catGram(pairs_z, ['ADJ'])
    pairs_NOM = restrictNumber(pairs_NOM, 'ADJ', 'p')
        #sequences
    pairs_NOM = pairs_NOM.reset_index(drop=True)
    sequences_NOM = createSequences(w1_z_NOM,pairs_NOM)
    sequences_NOM = sequencesAgreeGender(sequences_NOM)
    
    #Word 1 = PRE (chez, dans, sous, depuis, après)
    w1_z_PRE = selectWords1(W1_z, 'PRE', lemme=['chez','dans','sous','depuis','après'])
        #combinations of ADJ:ind/ADJ:num/ART:ind
    pairs_PRE = catGram(pairs_z, ['ADJ:ind','ADJ:num','ART:ind'])
        #sequences
    pairs_PRE = pairs_PRE.reset_index(drop=True)
    sequences_PRE = createSequences(w1_z_PRE,pairs_PRE)
    
    #Word 1 = PRE (sans)
    w1_z_PREsans = selectWords1(W1_z, 'PRE', lemme=['sans'])
        #combinations of ADJ:ind/ADJ:num/ART:ind/VER(inf)
    pairs_PREsans = catGram(pairs_z, ['ADJ:ind','ADJ:num','ART:ind','VER'])
    pairs_PREsans = catVerb(pairs_PREsans, 'inf')
        #sequences
    pairs_PREsans = pairs_PREsans.reset_index(drop=True)
    sequences_PREsans = createSequences(w1_z_PREsans,pairs_PREsans)
    
    #Word 1 = PRE (aux)
    w1_z_PREaux = selectWords1(W1_z, 'PRE', lemme=['aux'])
        #combinations of ADJ(p.)(pre-nom)/NOM(p.)/PRO:ind
    pairs_PREaux = catGram(pairs_z, ['ADJ','NOM','PRO:ind'])
    pairs_PREaux = restrictNumber(pairs_PREaux, 'ADJ', 'p')
    pairs_PREaux = restrictNumber(pairs_PREaux, 'NOM', 'p')
        #sequences
    pairs_PREaux = pairs_PREaux.reset_index(drop=True)
    sequences_PREaux = createSequences(w1_z_PREaux,pairs_PREaux)

    #Word 1 = PRO:per (nous, vous, ils, elles)
    w1_z_PROper = selectWords1(W1_z, 'PRO:per')
        #combinations of AUX(p.)(≠par≠inf)/VER(p.)(≠par≠inf≠imp)
    pairs_PROper = catGram(pairs_z, ['AUX','VER'])
    pairs_PROper = catVerb(pairs_PROper, 'ind:[a-z]{3}:[123]p|cnd:[a-z]{3}:[123]p|sub:[a-z]{3}:[123]p')
        #sequences
    pairs_PROper = pairs_PROper.reset_index(drop=True)
    sequences_PROper = createSequences(w1_z_PROper,pairs_PROper)
    sequences_PROper = sequencesAgreeProPerWithVerb(sequences_PROper)
    
    #Word 1 = VER (modaux)
    w1_z_VER = selectWords1(W1_z, 'VER', lemme=MODAUX)
        #combinations of VER(inf)
    pairs_VER = catGram(pairs_z, ['VER'])
    pairs_VER = catVerb(pairs_VER, 'inf')
        #sequences
    pairs_VER = pairs_VER.reset_index(drop=True)
    sequences_VER = createSequences(w1_z_VER,pairs_VER)
    
        #All sequences
    sequences = pd.concat([sequences_ADJ,sequences_ADJind,sequences_ADJdem,\
                           sequences_ADJnum,sequences_ADJpos,sequences_ARTdef,\
                           sequences_ARTind,sequences_ADJint,sequences_ADVpas,\
                           sequences_ADVnotpas,sequences_AUXetre,sequences_AUXavoir,\
                           sequences_CON,sequences_NOM,sequences_PRE,\
                           sequences_PREsans,sequences_PREaux,sequences_PROper,\
                           sequences_VER],ignore_index=True,sort=False)
    return sequences

    # 
    # Function to extract confusing sequences for each substitution
    # 

def extractResults(function):
    """ Creates a DataFrame with the number of confusing sequences for each substitution
    # function is a function to select confusing sequences (e.g. sequences_R) """
    liaisonCons = function.__name__[-1] 
    data = []
    for substitution in CONS:
        # extracting number of confusing sequences
        sequences = function(PAIRS, substitution)
        duplicate(sequences,['ortho_0','lemme_0','cgram_0',\
                             'ortho_1','lemme_1','cgram_1',\
                             'ortho_2','lemme_2','cgram_2'],\
                             'duplicate')
        numberSequences = len(sequences[sequences.duplicate== 0])

        # adding color for future plot
        if substitution == liaisonCons:
            color = 'navy'
        else:
            color = 'lightsteelblue'

        data.append([substitution, numberSequences, color])
    results = pd.DataFrame(data, columns = ['substitution', 'numberSequences','color'])
    results = results.sort_values(by=['substitution']).reset_index(drop=True)
    return results

# Results

results_g = extractResults(sequences_g)
results_n = extractResults(sequences_n)
results_p = extractResults(sequences_p)
results_R = extractResults(sequences_R)
results_t = extractResults(sequences_t)
results_z = extractResults(sequences_z)

    # Concatenating results and saving
results = pd.DataFrame({'substitution':sorted(CONS),
                        'g':results_g.numberSequences, 'n':results_n.numberSequences,
                        'p':results_p.numberSequences, 'R':results_R.numberSequences,
                        't':results_t.numberSequences, 'z':results_z.numberSequences})
results.to_csv('results\\results-number-confusing-doublets.csv', index=False)

# Adding Google tags and saving doublets to future frequency analysis

def addGoogleTags(sequences):
    """ Adds Google Tags to a DataFrame of sequences.
    These tags will be used for frequency analysis """
    gtags = pd.read_csv('resources\\google-tags.csv', sep=';')
    gtags.fillna('nan', inplace=True)
    gtags = gtags.values.tolist()

    for idx, row in sequences.iterrows():
        row_word0 = row[['ortho_0','lemme_0','cgram_0']].tolist()
        row_word1 = row[['ortho_1','lemme_1','cgram_1']].tolist()
        row_word2 = row[['ortho_2','lemme_2','cgram_2']].tolist()
        for id, tags in enumerate(gtags):
            if row_word0 == tags[0:3]:
                sequences.loc[idx, 'gtag_0'] = tags[3]
            if row_word1 == tags[0:3]:
                sequences.loc[idx, 'gtag_1'] = tags[3]
            if row_word2 == tags[0:3]:
                sequences.loc[idx, 'gtag_2'] = tags[3]
    return sequences

def saveDoublets(path):
    """ Saves all doublets in different .csv files
    for each liaison consonant and each substitution """
    if not os.path.exists(path):
            os.makedirs(path)

    columns = ['ortho_0','lemme_0','gtag_0','ortho_1',
               'lemme_1','gtag_1','ortho_2','lemme_2','gtag_2']
    for selectionFunction in [sequences_g, sequences_n, sequences_p,\
                     sequences_R, sequences_t, sequences_z]:
        for cons in CONS:
            doublets = selectionFunction(PAIRS, cons)
            if len(doublets) > 0:
                doublets = addGoogleTags(doublets)
                duplicate(doublets,columns,'duplicate_google')
                doublets = doublets[doublets.duplicate_google == 0]
                doublets = doublets[columns]
            else:
                doublets = pd.DataFrame(columns=columns)

            if cons.isupper() == True:
                cons = cons + '-'
            name = 'doublets_' + '_'.join([selectionFunction.__name__[-1], cons]) + '.csv'
            doublets.to_csv(os.path.join(path,name), index=False, sep=';')

saveDoublets('doublets')