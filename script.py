import re
from nltk.stem.porter import PorterStemmer
import glob
import os
from math import *


def fileIndexing(file_path, n):
    with open(file_path, encoding='utf-8') as f:
        text = f.read()
        text = re.sub(r"\?|,|\.|:|!|[0-9]+", " ", text)  # aussi aussi.
        text = re.sub(r"\s+|\n", ' ', text).lower()
        # print(text)

        # removing stop_words
        text_without_stop_words = text
        for stop_word in stop_words_list:
            # \s{stop_word}\s: ni si d'abord
            # \s{stop_word}\s{stop_word}\s: vous vous
            # \s(d'|c'){stop_word}\s: d'une c'est
            text_without_stop_words = re.sub(
                rf"\s(d'|c'|t'|s'|l')?{stop_word}(\s{stop_word})?\s", " ", text_without_stop_words)
        text_without_stop_words = re.sub(
            r"d'|s'|t'|c'|l'", "", text_without_stop_words)  # d'or

        # print(text_without_stop_words)
        words_list_without_stop_words = text_without_stop_words.split()
        # print(words_list_without_stop_words)

        stemmer = PorterStemmer()
        stem_words_list = [stemmer.stem(token)
                           for token in words_list_without_stop_words]
        with open(f'stem_words_files/stem_words_of_doc{n}.txt', mode="w", encoding='utf-8') as d:
            for stem in stem_words_list:
                d.write(f'{stem}\n')
        return stem_words_list


def dictionnaire(file_path, n):

    stem_words_list = fileIndexing(file_path, n)
    my_dict = {}
    # set(list): supprine tous les occurences dans une liste
    for stem_word in set(stem_words_list):
        my_dict[stem_word] = stem_words_list.count(stem_word)
    # my_dict={"terme1":freq1,"terme2":freq2,..}
    # chaque terme existe une seule fois
    return my_dict


def dictionnaireGlobal(folder_name):
    file_list = glob.glob(os.path.join(os.getcwd(), "files", "*.txt"))
    terms = []

    n = 0
    docs = []
    for file_path in file_list:
        n = n + 1
        # en fait l'appel a la fonction dictionnaire pour chaque fichier
        doc_freq = dictionnaire(file_path, n)
        # chaque document a son doc_freq, doc_freq contient les termes de document avec leurs frequences dans le document
        # doc_freq__de_document1 = {"haifa":freq, "vacances":freq,..}
        # doc_freq__de_document2 = {"joue":freq, "vacances":freq,..}
        docs.append(doc_freq)
        # docs = [{"haifa":1, "vacances":1,..},{"joue":1, "vacances":1,..}]
        for key in doc_freq:
            terms.append(key)
    #terms = ["haifa","vacances","joue","vacances"]

    # calculer l'IDF de chaque terme exixtant dans le fichier inverse
    terms_IDF = {}
    # set(terms)= ["haifa","vacances","joue"]
    for term in set(terms):
        terms_IDF[term] = 1/terms.count(term)
    # termes_IDF = {"haifa":1 ,"vacances":2,"joue":1,...}
    # print(terms_IDF)

    dictGlo = {}
    n = 0
    with open("fichier_inverse.txt", mode="w", encoding='utf-8') as w:
        w.write('terme___doc(n)___freq___poids\n')
        # print(docs)
        for doc in docs:
            n = n + 1
            dictGlo[f'doc{n}'] = {}

            # calculer le poids de chaque terme dans chaque document
            # print(doc)
            for key in doc:

                weight = (dictGlo[f'doc{n}'])[key] = doc[key] * terms_IDF[key]
                w.write(f'{key}___doc{n}___{doc[key]}___{weight}\n')
        # print(dictGLo)
        # dictGlo = {"doc1":{"haifa":poids,"vacances":poids,..},"doc2":{"joue":poids,"vacances":poids}}
    return dictGlo


def requestIndexing(request):

    r = re.sub(r"\?|,|\.|:|!|[0-9]+", " ", request)  # aussi aussi.
    r = re.sub(r"\s+|\n", ' ', r).lower()

    request_without_stop_words = r
    for stop_word in stop_words_list:
        request_without_stop_words = re.sub(
            rf"\s(d'|c'|t'|s'|l')?{stop_word}(\s{stop_word})?\s", " ", request_without_stop_words)

    request_without_stop_words = re.sub(
        r"d'|s'|t'|c'|l'", "", request_without_stop_words)  # d'or
    words_list_without_stop_words = request_without_stop_words.split()

    stemmer = PorterStemmer()
    stem_words_list = [stemmer.stem(token)
                       for token in words_list_without_stop_words]
    return set(stem_words_list)


def similarity(request_words_list, doc_terms):

    doc_terms_list = set()
    for key in doc_terms:
        doc_terms_list.add(key)

    # termes communs entre les termes de la requete et les termes de document
    common_terms = doc_terms_list & request_words_list

    produit_scalaire = 0
    for common_term in common_terms:
        produit_scalaire = produit_scalaire + doc_terms[common_term]

    sum = 0
    # sum  va contenir la somme de ((poids de terme dans le document)**2)
    for key in doc_terms:
        sum = sum + (doc_terms[key])**2

    s = produit_scalaire / ((sqrt(len(request_words_list))) * sqrt(sum))
    return s


def search(request, folder_name):
    request_words_list = requestIndexing(request)
    print(request_words_list)

    dictGL = dictionnaireGlobal(folder_name)
    print("dictionnaire gloable")
    print(dictGL)
    docs = []
    for key in dictGL:
        s = similarity(request_words_list, dictGL[key])
        if s != 0:
            myDict = {}
            myDict["doc"] = key
            myDict["similarity"] = s
            docs.append(myDict)
    print("sorted documents based on their similarity with the request")
    print(docs)
    # return docs.sort(key=lambda x: x.get('similarity'))


# programme principale
with open("stop_words.txt", encoding='utf-8') as s:
    stop_words_text = s.read().replace("\n", " ")
stop_words_list = stop_words_text.split(", ")


request = input("entrer la requete: ")
search(request, "files")
# print(dictionnaireGlobal("files"))
