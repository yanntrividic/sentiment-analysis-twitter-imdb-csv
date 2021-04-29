'''
Created on Mar 10, 2021

@author: yann
'''

from os.path import sep
import pickle
import random

from file_reader import load_pickle, read_csv_to_df
from file_writer import save_pickle
from nlp_utils import tokenize_and_remove_stopwords, convert_lang_format, lemmatize_words
import nltk
from nltk.corpus import movie_reviews, twitter_samples
from nltk.tokenize import word_tokenize

TRAINING_DATA_FOLDER = "model" + sep + "resources" + sep + "training_data" + sep

POS_SHORT_REVIEWS_FILEPATH = TRAINING_DATA_FOLDER + "positive_imdb_reviews.txt"
NEG_SHORT_REVIEWS_FILEPATH = TRAINING_DATA_FOLDER + "negative_imdb_reviews.txt"

NEG_FRENCH_TWEETS_FILEPATH = TRAINING_DATA_FOLDER + "french_tweets_neg.csv"
POS_FRENCH_TWEETS_FILEPATH = TRAINING_DATA_FOLDER + "french_tweets_pos.csv"

NEG_ALLOCINE_FILEPATH = TRAINING_DATA_FOLDER + "french_allocine_neg.csv"
POS_ALLOCINE_FILEPATH = TRAINING_DATA_FOLDER + "french_allocine_pos.csv"


def _preprocess_french_tweets_dataset():
    '''Extracts data from the french_tweets.csv dataset and processes it to match the classifiers
    The dataset used here can be found at this location: https://www.kaggle.com/hbaflast/french-twitter-sentiment-analysis/

    returns :
    words -- List of words used for the classification
    word_features -- the first n words most used in the dataset and their frequency
    feature_sets -- list of presence or absence of each word of word_features in a sample and the polarity of the sample
    '''

    neg_tweets_df = read_csv_to_df(NEG_FRENCH_TWEETS_FILEPATH)
    pos_tweets_df = read_csv_to_df(POS_FRENCH_TWEETS_FILEPATH)

    documents, tweets_pos, tweets_neg = ([] for i in range(3))  # initialization of three empty lists

    for _, row in neg_tweets_df.iterrows():
        txt = row['text']
        documents.append((txt, "neg"))
        tweets_neg += word_tokenize(txt, language="french")

    for _, row in pos_tweets_df.iterrows():
        txt = row['text']
        documents.append((txt, "pos"))
        tweets_pos += word_tokenize(txt, language="french")

    return __preprocess_into_training_data(documents, tweets_pos, tweets_neg, 3000, "fr")


def _preprocess_twitter_samples_dataset():
    '''Extracts data from the twitter_samples dataset and processes it to match the classifiers

    returns :
    words -- List of words used for the classification
    word_features -- the first n words most used in the dataset and their frequency
    feature_sets -- list of presence or absence of each word of word_features in a sample and the polarity of the sample
    '''
    documents, tweets_pos, tweets_neg = ([] for i in range(3))  # initialization of three empty lists

    for t in twitter_samples.strings("positive_tweets.json"):
        documents.append((t, "pos"))
        tweets_pos += lemmatize_words(tokenize_and_remove_stopwords(t, "en"))

    for t in twitter_samples.strings("negative_tweets.json"):
        documents.append((t, "neg"))
        tweets_neg += lemmatize_words(tokenize_and_remove_stopwords(t, "en"))

    return __preprocess_into_training_data(documents, tweets_pos, tweets_neg, 5000, "en")


def _preprocess_movie_reviews_dataset():
    '''Movie Reviews is the most accessible dataset about film reviews in english. This dataset is not adapted
    to work on short reviews.
    Here, we preprocess the data for it to be used in the classifiers.

    returns :
    words -- List of words used for the classification
    word_features -- the first n words most used in the dataset and their frequency
    feature_sets -- list of presence or absence of each word of word_features in a sample and the polarity of the sample
    '''
    # documents is a list of length 2 and contains the words in the dataset alongside their features
    # at index 0 are the words contained in negative movie reviews
    # at index 1 are the words contained in positive movie reviews
    documents = [(list(movie_reviews.words(fileid)), category)
                 for category in movie_reviews.categories()
                 for fileid in movie_reviews.fileids(category)]

    random.shuffle(documents)  # the data is ordered. We need to shuffle it to unbias it

    all_words = []  # will contain all the words of the dataset without their associated features
    for w in movie_reviews.words():
        all_words.append(w.lower())  # we word_totokenize_and_remove_stopwordskenizedon't care about the case

    all_words = nltk.FreqDist(all_words)  #  gets the frequency distribution of the words

    word_features = list(all_words.keys())[:3000]  # we extract the most frequent words from all_words
    # Basically, this line marks each of the 3000 most common words as present or absent in each 2000 document

    feature_sets = [(__find_features(set(rev), word_features), category) for (rev, category) in documents]

    return all_words, word_features, feature_sets


def _preprocess_short_reviews_dataset():
    '''The dataset used for here has been found at this link :
    https://pythonprogramming.net/static/downloads/short_reviews

    It is composed of 10600~ short movie reviews separated in two files (pos and neg).
    Here, we preprocess the data for it to be used in the classifiers.

    returns :
    words -- List of words used for the classification
    word_features -- the first n words most used in the dataset and their frequency
    feature_sets -- list of presence or absence of each word of word_features in a sample and the polarity of the sample
    '''
    short_pos = open(POS_SHORT_REVIEWS_FILEPATH, "r").read()
    short_neg = open(NEG_SHORT_REVIEWS_FILEPATH, "r").read()

    documents = []

    for r in short_pos.split('\n'):
        documents.append((r, "pos"))

    for r in short_neg.split('\n'):
        documents.append((r, "neg"))

    short_pos_words = lemmatize_words(tokenize_and_remove_stopwords(short_pos, "en"))
    short_neg_words = lemmatize_words(tokenize_and_remove_stopwords(short_neg, "en"))

    return __preprocess_into_training_data(documents, short_pos_words, short_neg_words, 5000, "en")


def _preprocess_allocine_dataset():
    '''The dataset used for here has been found at this link :
    https://www.kaggle.com/djilax/allocine-french-movie-reviews

    It is composed of 160k~ movie reviews in french in a CSV file.
    Here, we preprocess the data for it to be used in the classifiers.

    returns :
    words -- List of words used for the classification
    word_features -- the first n words most used in the dataset and their frequency
    feature_sets -- list of presence or absence of each word of word_features in a sample and the polarity of the sample
    '''

    neg_reviews_df = read_csv_to_df(NEG_ALLOCINE_FILEPATH)
    pos_reviews_df = read_csv_to_df(POS_ALLOCINE_FILEPATH)
#    print(neg_reviews_df)

    documents, reviews_pos, reviews_neg = ([] for i in range(3))  # initialization of three empty lists

    for _, row in neg_reviews_df.iterrows():
        txt = row['review']
        documents.append((txt, "neg"))
        reviews_neg += word_tokenize(txt, language="french")
    print(len(reviews_neg))
    print(str(reviews_neg[:10]))

    for _, row in pos_reviews_df.iterrows():
        txt = row['review']
        documents.append((txt, "pos"))
        reviews_pos += word_tokenize(txt, language="french")
    print(len(reviews_pos))
    print(str(reviews_pos[:10]))

    return __preprocess_into_training_data(documents, reviews_pos, reviews_neg, 3000, "fr")


def _get_training_data_from_pickle(preprocess, words_pickle=None, word_features_pickle=None, feature_sets_pickle=None):
    '''Tries to load the PICKLE file that contains the words used by the classifiers. It it fails,
    preprocesses the data and saves it into the words_pickle file

    words_pickle -- str Path to the PICKLE file
    preprocess -- Function used for the preprocessing of the data (used if the PICKLE file could not be loaded)

    returns
    words_pickle -- PICKLE fileList of words used for the classification
    word_features_pickle -- the first n words most used in the dataset and their frequency
    feature_sets_pickle -- list of presence or absence of each word of word_features in a sample and the polarity of the sample
    '''

    to_fill = [[None, words_pickle], [None, word_features_pickle], [None, feature_sets_pickle]]

    for element in range(len(to_fill)):  # for now, we comment it and load the two other objects only when needed

        if to_fill[element][1]:
            try:
                to_fill[element][0] = load_pickle(to_fill[element][1])

            except (FileNotFoundError, EOFError, pickle.PickleError):  #  if we can't read it, then we train a new model
                print(to_fill[element][1] + " coult not be loaded. New data will be generated and saved.")

                if(to_fill[element][0] is None):
                    to_fill[0][0], to_fill[1][0], to_fill[2][0] = preprocess()

                    # we save new versions of the files for it to be coherent
                    for e in range(len(to_fill)):
                        if to_fill[e][1]:
                            save_pickle(to_fill[e][0], to_fill[e][1])
                    return to_fill[0][0], to_fill[1][0], to_fill[2][0]

    return to_fill[0][0], to_fill[1][0], to_fill[2][0]


def __preprocess_into_training_data(documents, pos_words, neg_words, nb_words, lang):
    '''Common preprocessing function to preprocessdocuments into training data for the models of the project

    documents -- list of sentences
    pos_words -- list of all the positive words
    neg_words -- list of all the negative words
    nb_words -- the maximum amount of words to process
    lang -- the language is which the data is
    '''
    all_words = []
    random.shuffle(documents)

    for w in pos_words:
        all_words.append(w.lower())

    for w in neg_words:
        all_words.append(w.lower())

    all_words = nltk.FreqDist(all_words)

    word_features = list(all_words.keys())[:nb_words]
    # print(word_features[:10])
    # print(all_words.most_common(20))

    feature_sets = [(__find_features(word_tokenize(rev, language=convert_lang_format(lang, 'en_name')),
                                     word_features), category) for (rev, category) in documents]

    random.shuffle(feature_sets)

    return all_words, word_features, feature_sets


def __find_features(document, word_features):
    '''Extracts all the features for a document
    '''
    words = document  # all the words contained in one document
    features = {}
    for w in word_features:  # for each 3000 most common words
        features[w] = (w in words)  # we put a new dict entry in features to mark its presence or absence
    return features
