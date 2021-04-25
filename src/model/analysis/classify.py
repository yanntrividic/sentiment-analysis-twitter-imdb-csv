'''
Created on Mar 5, 2021

@author: yann

Module that contains the Classifier class.
This module is based on the work of Harrison Kinsley. You can find the original code by visiting the following link:
https://pythonprogramming.net/tokenizing-words-sentences-nltk-tutorial/
'''

import pickle

from file_reader import load_pickle
from file_writer import save_pickle
from nlp_utils import convert_lang_format
from nltk import NaiveBayesClassifier
import nltk
from nltk.classify.scikitlearn import SklearnClassifier
from nltk.tokenize import word_tokenize
from preprocessing import _get_training_data_from_pickle


# from nltk.tokenize import word_tokenize
class Classifier:
    '''
    This class is a generic class for classifying textual data with sklearn Classifiers. The data must be preprocessed
    in order for the training to work properly.
    '''

    def __init__(self, name, algorithm, model_pickle, lang, words, word_features_pickle, feature_sets_pickle, preprocess):
        '''
        Constructor

        algorithm -- Either an SklearnClassifier or the NaiveBayesClassifier
        model_pickle -- Path to the PICKLE file used to load the model (SklearnClassifier or NaiveBayesClassifier object)
        words -- List of words used for the classification
        word_features_pickle -- PICKLE file that contains the first n words most used in the dataset and their frequency
        feature_sets_pickle -- PICKLE file that contains the list of presence or absence of each word of word_features
        in a sample and the polarity of the sample
        preprocess -- Function used for the preprocessing of the data (used if the PICKLE file could not be loaded)
        '''

        self.__name__ = name
        self.lang = lang
        self.model_pickle = model_pickle
        self.algorithm = algorithm
        self.words = words

        try:  # first we try to read the files
            self.classifier = load_pickle(model_pickle, self.__name__)
            if not isinstance(self.classifier, (NaiveBayesClassifier, SklearnClassifier)):
                raise ValueError("The loaded PICKLE file is not an instance of Classifier.")

        except (FileNotFoundError, EOFError, pickle.PickleError, ValueError):  #  if we can't read it, then we train a new model
            print(self.model_pickle + " coult not be loaded. " +
                  "A new model will be trained and saved.")

            # _get_training_data_from_pickle either loads the data if it has found the file,
            # or it generates new features.
            _, self.word_features, self.feature_sets = _get_training_data_from_pickle(preprocess, None,
                                                                                      word_features_pickle=word_features_pickle,
                                                                                      feature_sets_pickle=feature_sets_pickle)

            self.__training_set, self.__testing_set = self.__divide_feature_sets()  # division in a training and a testing set
            self.__train_classifier()  #  training of the model
            save_pickle(self.classifier, self.model_pickle, self.__name__, True)

    def __repr__(self):
        return self.__name__ + "(model_pickle:" + self.model_pickle + ")"

    def __train_classifier(self):
        self.classifier = self.algorithm.train(self.__training_set)  # where the training actually happens
        self.print_accuracy()
        if isinstance(self.classifier, NaiveBayesClassifier):
            self.classifier.show_most_informative_features(10)  # Only the NaiveBayesClassifier has this method implemented

    def __divide_feature_sets(self):
        last_five_percent_index = len(self.feature_sets) - len(self.feature_sets) // 20  # retrieves a 20th of the dataset
        return self.feature_sets[:last_five_percent_index], self.feature_sets[last_five_percent_index:]

    def print_accuracy(self):
        '''Prints the accuracy of the classifier that just got trained.
        '''
        print(self.__name__ + " accuracy percent: ", (nltk.classify.accuracy(self.classifier, self.__testing_set)) * 100)

    def classify(self, data, verbose=False):
        '''Classifies data as "pos" or "neg". The model has to be operational beforehand.

        data -- str or pd.DataFrame. Contains the data to classify (as sentences)
        colname -- str in the case the argument passed is a dataframe, the column name where the text to classify is has
        to be specified
        '''
        features = {}

        tokenized = word_tokenize(data, language=convert_lang_format(self.lang, 'en_name'))
        for word in self.words:
            features[word] = (word in tokenized)
        result = self.classifier.classify(features)
        if verbose:
            print(result + " - \"" + data + "\" (" + self.__name__ + ")")
        return result
