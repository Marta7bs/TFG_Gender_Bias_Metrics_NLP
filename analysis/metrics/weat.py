# Import necessary libraries

from bs4.element import NavigableString
import pandas as pd
import numpy as np
import spacy
import pickle
import requests
from bs4 import BeautifulSoup
import re
import gensim
import random
from gensim.models import Word2Vec
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# load model MARCA
ES_defs = [["mujer", "hombre"], ["nina", "nino"], ["ella", "él"], ["madre", "padre"], ["hija", "hijo"], ["chica", "chico"], ["femenino", "masculino"], ["hermana", "hermano"], ["maría", "juan"]]
w2v_model = Word2Vec.load(r"C:\Users\marta\OneDrive - Universidad Carlos III de Madrid\documentos\UC3M4\TFG\TFG\.ipynb_checkpoints\models\marca\sportword2vec.model")
PATH_VOCAB = r"C:\Users\marta\OneDrive - Universidad Carlos III de Madrid\documentos\UC3M4\TFG\TFG\.ipynb_checkpoints\models\marca\pipe7-vocab"
# load model AS
#w2v_model = Word2Vec.load(r"C:\Users\marta\OneDrive - Universidad Carlos III de Madrid\documentos\UC3M4\TFG\TFG\.ipynb_checkpoints\models\as\AsWord2Vec.model")
#PATH_VOCAB = r"C:\Users\marta\OneDrive - Universidad Carlos III de Madrid\documentos\UC3M4\TFG\TFG\.ipynb_checkpoints\models\as\As-vocab"
# load model MUNDO DEPOTIVO
#PATH_VOCAB =  r"C:\Users\marta\OneDrive - Universidad Carlos III de Madrid\documentos\UC3M4\TFG\TFG\.ipynb_checkpoints\models\mundoDeportivo\MD-vocab"
#w2v_model = Word2Vec.load(r"C:\Users\marta\OneDrive - Universidad Carlos III de Madrid\documentos\UC3M4\TFG\TFG\.ipynb_checkpoints\models\mundoDeportivo\MDWord2Vec.model")

################################################
###############################################

# check similarity, how well do the gender pairs capture GENDER
#gender_pairs = [("ella", "él"),("mujer", "hombre"), ("maría", "josé"), ("hija", "hijo"), ("madre", "padre"), ("nina", "nino"), ("chica", "chico"), ("hembra", "macho")]
ES_defs_trunc = [("ella", "él"),("maría", "josé"), ("mujer", "hombre"), ("madre", "padre"), ("hija", "hijo"), ("femenino", "masculino"), ("hermana", "hermano"), ("nina", "nino"),
                ("chica", "chico")]
'''She_he_classifier returns a list of gender paired words who describe gender by cheking proximity to reference words él y ella'''
def she_he_classifier(gender_pairs):
    pairs_check = []
    for (female_word, male_word) in gender_pairs:
        # compute cosine similarities
        d1 = w2v_model.wv.similarity(female_word, 'ella')
        d2 = w2v_model.wv.similarity(female_word, 'él')
        d3 = w2v_model.wv.similarity(male_word, 'ella')
        d4 = w2v_model.wv.similarity(male_word, 'él')
        if (d1 > d2) and (d3 < d4):
            pairs_check.append((female_word, male_word))
            print("Word "+female_word+" captures gender: "+str(d1)+" "+str(d2))
            print("Word "+male_word+" captures gender: "+str(d2)+" "+str(d1))
    return pairs_check
        
gender_pairs_filtered = she_he_classifier(ES_defs_trunc)

#####################################################
#####################################################

#------------ WEAT SCORE ------------
''' Conjuntos de palabras objetivo neutras (hipothesis):
    - X: anticipa sesgo hacia A
    - Y: anticipa sesgo hacia B
    
    Conjuntos sesgados:
    - A: sesgo masculino
    - B: sesgo femenino
     
    Interpretación de los resultados:
     Valor positivo indica que las palabras de X se inclinan hacia A y las
     palabras de Y se inclinan hacia B -> se confirma sesgo ''' 
    
set_A = [ male_word for (female_word, male_word) in ES_defs_trunc]
set_B = [ female_word for (female_word, male_word) in ES_defs_trunc]

''' calculates s(w,A,B) for each w in X or Y'''
def word_individual_bias(word, A, B):
    n = len(A)
    b1 = 0
    b2 = 0
    for w in A:
        b1 += w2v_model.wv.similarity(word, w)
    for w in B:
        b2 += w2v_model.wv.similarity(word, w)
    return (1/n) * b1 - (1/n) * b2

''' calculates s(w, A, B) in gendered words'''
def individual_bias_gender(word_f, word_m, A, B):
    return abs((abs(word_individual_bias(word_m, A, B))-abs(word_individual_bias(word_f, A, B))))

''' computes WEAT score for gendered languages given sets X, Y, A, B'''
def weat_score_gender(X, Y, A, B):
    resX = []
    resY = []

    for word in X:
        if isinstance(word, str):
            b = abs(word_individual_bias(word, A, B))
            print(word+ ": "+ str(b))
            resX.append(b)
        if isinstance(word, tuple):
            (f_w, m_w) = word
            b = individual_bias_gender(f_w, m_w, A, B)
            print(str(word) + ": "+ str(b))
            resX.append(b)

    for word in Y:
        if isinstance(word,str):
            resY.append(abs(word_individual_bias(word, A, B)))
        if isinstance(word, tuple):
            (f_w, m_w) = word
            b = individual_bias_gender(f_w, m_w, A, B)
            print(str(word) + ": "+ str(b))
            resY.append(b)
    return sum(resX) - sum(resY)
    #return (np.mean(resX)-np.mean(resY)) / np.std(resX+resY)

''' Computes weat score given sets X, Y, A, B'''
def weat_score(X, Y, A, B):
    resX = [word_individual_bias(word, A, B) for word in X]
    resY = [word_individual_bias(word, A, B) for word in Y]
    return sum(resX) - sum(resY)  # segun un vid de youtube este es el weat SCORE https://www.youtube.com/watch?v=eTenkUPsjko&ab_channel=AIAnytime
    #return (np.mean(resX)-np.mean(resY)) / np.std(resX+resY)

#########################################################
#########################################################

'''Experiment building'''
exp = []
# EXPERIMENTO 1: deportes
set_X = ["fútbol", "baloncesto", "rugby", "ciclismo", "motociclismo", "automovilismo", "boxeo"]
set_Y = ["tenis", "voleibol", "natación", "atletismo", "gimnasia", "patinaje"]
exp.append((set_X, set_Y))
# EXPERIMENTO 2: familiarización
set_X = ["partido", "equipo", "casa", "logro", "copa", "estadio"]
set_Y = ["pareja", "familia", "hogar", "cuidado", "relación", "sentimental"]
exp.append((set_X, set_Y))
# EXPERIMENTO 3: sexualización
set_X = ["fuerte", "valiente", "piernas", "inteligente", "brillante"]
set_Y = ["cuerpo", "modelo", "belleza", "labios", "sensual", "sentimental"]
exp.append((set_X, set_Y))

"""WEAT neutro"""
for (x,y) in exp:
    print("------------------")
    print(weat_score(x,y,set_A,set_B))

############################################################
############################################################

# get all permutations possible by combining list of "female" and "male" hypothetical
# lists of the experiments
import itertools
import random

exp2_x = exp[1][0] 
exp2_y = exp[1][1]
mixed_sets = exp2_x + exp2_y

permutations_exp1 = list(itertools.permutations(mixed_sets,6))
random.shuffle(permutations_exp1)
#print(permutations_exp1)
weat_score_base = weat_score(exp2_x, exp2_y, set_A, set_B)

##################################################
################################################
iter = len(permutations_exp1) // 2
print(iter)
p_test = []
print("entro")
for i in range(0, len(permutations_exp1) // 2, 2):
    e1 = permutations_exp1[i]
    print(i)
    e2 = permutations_exp1[i+1]
    # if weat_score is greater than calculated weat (mal asunto, ahí es cuando se cuenta)
    p_test.append(weat_score(tuple(e1), tuple(e2), set_A, set_B))

p_test = np.array(p_test)

perms_with_more_bias = (p_test > weat_score_base).sum()
percent = (perms_with_more_bias/len(permutations_exp1))*100
print(percent)