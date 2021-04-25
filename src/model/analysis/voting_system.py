'''
Created on Mar 10, 2021

Module that contains the VoteClassifier class.

This module is based on the work of Harrison Kinsley. You can find the original code by visiting the following link:
https://pythonprogramming.net/combine-classifier-algorithms-nltk-tutorial/?completed=/sklearn-scikit-learn-nltk-tutorial/
@author: yann
'''

import concurrent.futures
import gc
from os.path import sep
from statistics import mode
import time

from classify import Classifier
from nltk import NaiveBayesClassifier
from nltk.classify.scikitlearn import SklearnClassifier  # basically a wrapper for scikit in nltk
from preprocessing import (_preprocess_movie_reviews_dataset, _preprocess_short_reviews_dataset,
                           _preprocess_allocine_dataset,
                           _preprocess_twitter_samples_dataset, _preprocess_french_tweets_dataset,
                           _get_training_data_from_pickle)
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.svm import LinearSVC  #  , NuSVC

import multiprocessing as mp
import pandas as pd

PICKLE_FOLDER = "model" + sep + "resources" + sep + "pickle" + sep  # source folder where to store the PICKLE files
IMDB_FOLDER = PICKLE_FOLDER + "imdb" + sep
TWITTER_FOLDER = PICKLE_FOLDER + "twitter" + sep
EN_FOLDER = "en" + sep
FR_FOLDER = "fr" + sep

# Each model (for each dataset and each language) has to have its own pickle file.
WORDS_IMDB_EN_LONG = IMDB_FOLDER + "words_imdb_long_en.pickle"
WORDS_FEATURES_IMDB_EN_LONG = IMDB_FOLDER + "words_features_imdb_long_en.pickle"
FEATURE_SETS_IMDB_EN_LONG = IMDB_FOLDER + "features_sets_imdb_long_en.pickle"

IMDB_NLTK_NB_EN_LONG_REVIEWS_PICKLE = IMDB_FOLDER + EN_FOLDER + "imdb_nltk_nb_en_long.pickle"
IMDB_MNB_BAYES_EN_LONG_REVIEWS_PICKLE = IMDB_FOLDER + EN_FOLDER + "imdb_mnb_en_long.pickle"
IMDB_BERNOULLI_EN_LONG_REVIEWS_PICKLE = IMDB_FOLDER + EN_FOLDER + "imdb_bernoulli_en_long.pickle"
IMDB_LR_EN_LONG_REVIEWS_PICKLE = IMDB_FOLDER + EN_FOLDER + "imdb_lr_en_long.pickle"
IMDB_SGDC_EN_LONG_REVIEWS_PICKLE = IMDB_FOLDER + EN_FOLDER + "imdb_sgdc_en_long.pickle"
IMDB_LSVC_EN_LONG_REVIEWS_PICKLE = IMDB_FOLDER + EN_FOLDER + "imdb_lsvc_en_long.pickle"

# Each model for the english language, trained on the short reviews IMDb dataset
WORDS_IMDB_EN_SHORT = IMDB_FOLDER + EN_FOLDER + "words_imdb_short_en.pickle"
WORDS_FEATURES_IMDB_EN_SHORT = IMDB_FOLDER + EN_FOLDER + "words_features_imdb_short_en.pickle"
FEATURE_SETS_IMDB_EN_SHORT = IMDB_FOLDER + EN_FOLDER + "features_sets_imdb_short_en.pickle"

IMDB_NLTK_NB_EN_SHORT_REVIEWS_PICKLE = IMDB_FOLDER + EN_FOLDER + "imdb_nltk_nb_en_short.pickle"
IMDB_MNB_BAYES_EN_SHORT_REVIEWS_PICKLE = IMDB_FOLDER + EN_FOLDER + "imdb_mnb_en_short.pickle"
IMDB_BERNOULLI_EN_SHORT_REVIEWS_PICKLE = IMDB_FOLDER + EN_FOLDER + "imdb_bernoulli_en_short.pickle"
IMDB_LR_EN_SHORT_REVIEWS_PICKLE = IMDB_FOLDER + EN_FOLDER + "imdb_lr_en_short.pickle"
IMDB_SGDC_EN_SHORT_REVIEWS_PICKLE = IMDB_FOLDER + EN_FOLDER + "imdb_sgdc_en_short.pickle"
IMDB_LSVC_EN_SHORT_REVIEWS_PICKLE = IMDB_FOLDER + EN_FOLDER + "imdb_lsvc_en_short.pickle"

# Each model for the english language, trained on the short reviews IMDb dataset
WORDS_IMDB_FR = IMDB_FOLDER + FR_FOLDER + "words_imdb_fr.pickle"
WORDS_FEATURES_IMDB_FR = IMDB_FOLDER + FR_FOLDER + "words_features_imdb_fr.pickle"
FEATURE_SETS_IMDB_FR = IMDB_FOLDER + FR_FOLDER + "features_sets_imdb_fr.pickle"

IMDB_NLTK_NB_FR_REVIEWS_PICKLE = IMDB_FOLDER + FR_FOLDER + "imdb_nltk_nb_fr.pickle"
IMDB_MNB_BAYES_FR_REVIEWS_PICKLE = IMDB_FOLDER + FR_FOLDER + "imdb_mnb_fr.pickle"
IMDB_BERNOULLI_FR_REVIEWS_PICKLE = IMDB_FOLDER + FR_FOLDER + "imdb_bernoulli_fr.pickle"
IMDB_LR_FR_REVIEWS_PICKLE = IMDB_FOLDER + FR_FOLDER + "imdb_lr_fr.pickle"
IMDB_SGDC_FR_REVIEWS_PICKLE = IMDB_FOLDER + FR_FOLDER + "imdb_sgdc_fr.pickle"
IMDB_LSVC_FR_REVIEWS_PICKLE = IMDB_FOLDER + FR_FOLDER + "imdb_lsvc_fr.pickle"

# Each model for the english language, trained on the twitter_samples dataset
WORDS_TWITTER_EN = TWITTER_FOLDER + EN_FOLDER + "words_twitter_en.pickle"
WORDS_FEATURES_TWITTER_EN = TWITTER_FOLDER + EN_FOLDER + "words_features_twitter_en.pickle"
FEATURE_SETS_TWITTER_EN = TWITTER_FOLDER + EN_FOLDER + "features_sets_twitter_en.pickle"

TWITTER_NLTK_NB_EN_PICKLE = TWITTER_FOLDER + EN_FOLDER + "twitter_nltk_nb_en.pickle"
TWITTER_MNB_BAYES_EN_PICKLE = TWITTER_FOLDER + EN_FOLDER + "twitter_mnb_en.pickle"
TWITTER_BERNOULLI_EN_PICKLE = TWITTER_FOLDER + EN_FOLDER + "twitter_bernoulli_en.pickle"
TWITTER_LR_EN_PICKLE = TWITTER_FOLDER + EN_FOLDER + "twitter_lr_en.pickle"
TWITTER_SGDC_EN_PICKLE = TWITTER_FOLDER + EN_FOLDER + "twitter_sgdc_en.pickle"
TWITTER_LSVC_EN_PICKLE = TWITTER_FOLDER + EN_FOLDER + "twitter_lsvc_en.pickle"

# Each model for the french language, trained on the twitter_samples dataset
WORDS_TWITTER_FR = TWITTER_FOLDER + FR_FOLDER + "words_twitter_fr.pickle"
WORDS_FEATURES_TWITTER_FR = TWITTER_FOLDER + FR_FOLDER + "words_features_twitter_fr.pickle"
FEATURE_SETS_TWITTER_FR = TWITTER_FOLDER + FR_FOLDER + "features_sets_twitter_fr.pickle"

TWITTER_NLTK_NB_FR_PICKLE = TWITTER_FOLDER + FR_FOLDER + "twitter_nltk_nb_fr.pickle"
TWITTER_MNB_BAYES_FR_PICKLE = TWITTER_FOLDER + FR_FOLDER + "twitter_mnb_fr.pickle"
TWITTER_BERNOULLI_FR_PICKLE = TWITTER_FOLDER + FR_FOLDER + "twitter_bernoulli_fr.pickle"
TWITTER_LR_FR_PICKLE = TWITTER_FOLDER + FR_FOLDER + "twitter_lr_fr.pickle"
TWITTER_SGDC_FR_PICKLE = TWITTER_FOLDER + FR_FOLDER + "twitter_sgdc_fr.pickle"
TWITTER_LSVC_FR_PICKLE = TWITTER_FOLDER + FR_FOLDER + "twitter_lsvc_fr.pickle"


class VoteClassifier:
    '''This class takes only one attribute : a list of trained Classifiers. Those classifiers will then be used
    to classify validedata and the VoteClassifier will concatenate those vote to pick the most voted result. From this poll,
    we can extract a confidence factor.
    '''

    def __init__(self, name):
        '''
        Constructor

        classifiers - list of Classifiers, can be empty but the classifiers have to be added later
        '''
        self.__name__ = name
        self._classifiers = []

    def get_nb_classifiers(self):
        return len(self._classifiers)

    def classify(self, features, colname="", pos_max_thresh=0.5, neg_max_thresh=0.5, multiprocessing=True, verbose=False):
        '''Classifies features and returns the mode of the different votes generated by each classifier

        features -- str or pd.DataFrame, contains the data to process
        returns the most voted value, will be either "pos" or "neg"
        '''

        if (pos_max_thresh + neg_max_thresh) > 1:
            raise ValueError("The thresholds can't add up to more than 1.")

        if not self._classifiers:
            raise AttributeError("There is no loaded classifier in the " + __name__ + " VoteClassifier")

        if isinstance(features, pd.DataFrame):
            if verbose:
                print("Beginning of classification with " + self.__name__)
            results = []
            if multiprocessing:  # if we choose to run the classifications in parallel
                pool = mp.Pool(mp.cpu_count())
                sentences = features[colname].values.tolist()

                result_objects = [pool.apply_async(self.classify, (sent, colname)) for sent in sentences]
                results = [r.get() for r in result_objects]

                pool.close()
                pool.join()  # postpones the execution of next line of code until all processes in the queue are

            else:  # a simpler way to do it without parallelism
                col = features[colname].values.tolist()
                for sentence in col:
                    results.append(self.classify(sentence, col))  # if call this function recursively with the str contained

        if isinstance(features, str):  # if this is a string
            votes = []
            for c in self._classifiers:  # for each classifier
                v = c.classify(features)  # take a vote
                votes.append(v)

            # here we decide, based on the various thresholds decided, if it's pos, neg or neu
            if (votes.count("pos") / len(votes)) > pos_max_thresh:
                results = "pos"
            elif (votes.count("neg") / len(votes)) > neg_max_thresh:
                results = "neg"
            else:
                results = "neu"

        if verbose and isinstance(features, str):
            print(results + " - " + features)

        return results

    def confidence(self, features):
        '''Returns the confidence factor of the classification
        '''
        votes = []  # will only contain 'neg' and 'pos' several occurrences
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)

        choice_votes = votes.count(mode(votes))  #  we count the number of time the most commun vote was mentioned
        conf = choice_votes / len(votes)  # and we divide by the number de classifiers
        return conf


def get_imdb_long_reviews_vc(vc):
    '''Function that instantiates a new VoteClassifier out of the pretrained pickle files found regarding
    the movie_reviews dataset.
    '''
    __instantiate_vc(vc, 'en', _preprocess_movie_reviews_dataset, WORDS_IMDB_EN_LONG, WORDS_FEATURES_IMDB_EN_LONG,
                     FEATURE_SETS_IMDB_EN_LONG,
                     IMDB_NLTK_NB_EN_LONG_REVIEWS_PICKLE, IMDB_MNB_BAYES_EN_LONG_REVIEWS_PICKLE,
                     IMDB_BERNOULLI_EN_LONG_REVIEWS_PICKLE, IMDB_LR_EN_LONG_REVIEWS_PICKLE,
                     IMDB_SGDC_EN_LONG_REVIEWS_PICKLE, IMDB_LSVC_EN_LONG_REVIEWS_PICKLE)


def get_imdb_short_reviews_vc(vc):
    '''Function that instantiates a new VoteClassifier out of the pretrained pickle files found regarding
    the short reviews dataset.
    '''
    __instantiate_vc(vc, 'en', _preprocess_short_reviews_dataset, WORDS_IMDB_EN_SHORT, WORDS_FEATURES_IMDB_EN_SHORT,
                     FEATURE_SETS_IMDB_EN_SHORT,
                     IMDB_NLTK_NB_EN_SHORT_REVIEWS_PICKLE, IMDB_MNB_BAYES_EN_SHORT_REVIEWS_PICKLE,
                     IMDB_BERNOULLI_EN_SHORT_REVIEWS_PICKLE, IMDB_LR_EN_SHORT_REVIEWS_PICKLE,
                     IMDB_SGDC_EN_SHORT_REVIEWS_PICKLE, IMDB_LSVC_EN_SHORT_REVIEWS_PICKLE)


def get_imdb_allocine_vc(vc):
    '''Function that instantiates a new VoteClassifier out of the pretrained pickle files found regarding the
    allocine dataset.
    '''
    __instantiate_vc(vc, 'fr', _preprocess_allocine_dataset, WORDS_IMDB_FR, WORDS_FEATURES_IMDB_FR,
                     FEATURE_SETS_IMDB_FR,
                     IMDB_NLTK_NB_FR_REVIEWS_PICKLE, IMDB_MNB_BAYES_FR_REVIEWS_PICKLE,
                     IMDB_BERNOULLI_FR_REVIEWS_PICKLE, IMDB_LR_FR_REVIEWS_PICKLE,
                     IMDB_SGDC_FR_REVIEWS_PICKLE, IMDB_LSVC_FR_REVIEWS_PICKLE)


def get_twitter_en_vc(vc):
    '''Function that instantiates a new VoteClassifier out of the pretrained pickle files found regarding
    the twitter_samples dataset.
    A first estimation using the Condorcet Jury's theorem states that this model will predict with a ~89.6 %
    accuracy the sentiment related to a sentence.
    '''
    __instantiate_vc(vc, 'en', _preprocess_twitter_samples_dataset, WORDS_TWITTER_EN, WORDS_FEATURES_TWITTER_EN,
                     FEATURE_SETS_TWITTER_EN,
                     TWITTER_NLTK_NB_EN_PICKLE, TWITTER_MNB_BAYES_EN_PICKLE, TWITTER_BERNOULLI_EN_PICKLE,
                     TWITTER_LR_EN_PICKLE, TWITTER_SGDC_EN_PICKLE, TWITTER_LSVC_EN_PICKLE)


def get_twitter_fr_vc(vc):
    '''Function that instantiates a new VoteClassifier out of the pretrained pickle files found regarding the
    french tweets dataset.
    '''
    __instantiate_vc(vc, 'fr', _preprocess_french_tweets_dataset, WORDS_TWITTER_FR, WORDS_FEATURES_TWITTER_FR,
                     FEATURE_SETS_TWITTER_FR,
                     TWITTER_NLTK_NB_FR_PICKLE, TWITTER_MNB_BAYES_FR_PICKLE, TWITTER_BERNOULLI_FR_PICKLE,
                     TWITTER_LR_FR_PICKLE, TWITTER_SGDC_FR_PICKLE, TWITTER_LSVC_FR_PICKLE)


def __instantiate_vc(vc, lang, preprocess, words_pickle, words_features_pickle, feature_sets_pickle,
                     nltk_naive_bayes=None, mnb=None, bernoulli=None, logistic_regression=None,
                     sgdc=None, linear_svc=None, verbose=True, multithreading=True):
    '''Method that instantiates a new VoteClassifier. Ideally, this model just does the file loading, but
    if no file was found, it can load files and train new models.
    '''

    start = time.perf_counter()

    # Then we declare all the classifiers that will go in the VoteClassifier below

    # retrieves the words data
    words, _, _ = _get_training_data_from_pickle(preprocess, words_pickle=words_pickle)
    gc.collect(2)

    args = [
        ["NLTK_NaiveBayes_classifier", NaiveBayesClassifier, nltk_naive_bayes],
        ["MNB_classifier", SklearnClassifier(MultinomialNB()), mnb],
        ["BernoulliNB_classifier", SklearnClassifier(BernoulliNB()), bernoulli],
        ["LogisticRegression_classifier", SklearnClassifier(LogisticRegression(max_iter=150)), logistic_regression],
        ["SGDClassifier_classifier", SklearnClassifier(SGDClassifier()), sgdc],
        ["LinearSVC_classifier", SklearnClassifier(LinearSVC()), linear_svc]]

    for arg in args:
        # arg += [words, word_features, feature_sets, preprocess]
        arg += [lang, words, words_features_pickle, feature_sets_pickle, preprocess]

    # multithreading goes here
    if multithreading:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(__proxy_instantiate_model, arg) for arg in args]

            for f in concurrent.futures.as_completed(futures):
                vc._classifiers.append(f.result())

    else:  # if we don't want multithread computing
        for arg in args:
            # if verbose:
            #    print("Dealing with " + arg[0] + " for " + vc.__name__ + ".")
            vc._classifiers.append(__proxy_instantiate_model(arg))

    finish = time.perf_counter()

    if verbose:
        # print(vc.__name__, vc._classifiers)
        print(f'All {vc.__name__} models were loaded correctly ({vc.get_nb_classifiers()} models in {round(finish-start, 2)} second(s)).')


def __proxy_instantiate_model(args):  # this proxy is just to bundle the different arguments needed
    return __instantiate_model(*args)


def __instantiate_model(name, algorithm, model_pickle, lang, words, words_features, feature_sets, preprocess, verbose=False):
    start = time.perf_counter()
    trained_model = Classifier(name, algorithm, model_pickle, lang, words, words_features, feature_sets, preprocess)
    gc.collect(2)
    finish = time.perf_counter()
    if verbose:
        print(f'Loading of {name} finished in {round(finish-start, 2)} second(s)')
    return trained_model
