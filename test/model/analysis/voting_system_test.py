'''
Created on Mar 11, 2021

@author: yann
'''

import os
from os.path import sep

from classify import Classifier
from file_reader import load_pickle
from preprocessing import (_preprocess_twitter_samples_dataset, _preprocess_short_reviews_dataset,
                           _preprocess_movie_reviews_dataset)
import pytest
from voting_system import (WORDS_IMDB_EN_SHORT,
                           WORDS_FEATURES_IMDB_EN_SHORT,
                           FEATURE_SETS_IMDB_EN_SHORT,
                           IMDB_NLTK_NB_EN_SHORT_REVIEWS_PICKLE,
                           IMDB_MNB_BAYES_EN_SHORT_REVIEWS_PICKLE,
                           IMDB_BERNOULLI_EN_SHORT_REVIEWS_PICKLE,
                           IMDB_LR_EN_SHORT_REVIEWS_PICKLE,
                           IMDB_SGDC_EN_SHORT_REVIEWS_PICKLE,
                           IMDB_LSVC_EN_SHORT_REVIEWS_PICKLE)
from voting_system import (WORDS_IMDB_FR,
                           WORDS_FEATURES_IMDB_FR,
                           FEATURE_SETS_IMDB_FR,
                           IMDB_NLTK_NB_FR_REVIEWS_PICKLE,
                           IMDB_MNB_BAYES_FR_REVIEWS_PICKLE,
                           IMDB_BERNOULLI_FR_REVIEWS_PICKLE,
                           IMDB_LR_FR_REVIEWS_PICKLE,
                           IMDB_SGDC_FR_REVIEWS_PICKLE,
                           IMDB_LSVC_FR_REVIEWS_PICKLE)
from voting_system import (WORDS_TWITTER_EN,
                           WORDS_FEATURES_TWITTER_EN,
                           FEATURE_SETS_TWITTER_EN,
                           TWITTER_NLTK_NB_EN_PICKLE,
                           TWITTER_MNB_BAYES_EN_PICKLE,
                           TWITTER_BERNOULLI_EN_PICKLE,
                           TWITTER_LR_EN_PICKLE,
                           TWITTER_SGDC_EN_PICKLE,
                           TWITTER_LSVC_EN_PICKLE)
from voting_system import (WORDS_TWITTER_FR,
                           WORDS_FEATURES_TWITTER_FR,
                           FEATURE_SETS_TWITTER_FR,
                           TWITTER_NLTK_NB_FR_PICKLE,
                           TWITTER_MNB_BAYES_FR_PICKLE,
                           TWITTER_BERNOULLI_FR_PICKLE,
                           TWITTER_LR_FR_PICKLE,
                           TWITTER_SGDC_FR_PICKLE,
                           TWITTER_LSVC_FR_PICKLE)
from voting_system import VoteClassifier, get_imdb_short_reviews_vc, get_twitter_en_vc

files_imdb_short = [WORDS_IMDB_EN_SHORT,
                    WORDS_FEATURES_IMDB_EN_SHORT,
                    FEATURE_SETS_IMDB_EN_SHORT,
                    IMDB_NLTK_NB_EN_SHORT_REVIEWS_PICKLE,
                    IMDB_MNB_BAYES_EN_SHORT_REVIEWS_PICKLE,
                    IMDB_BERNOULLI_EN_SHORT_REVIEWS_PICKLE,
                    IMDB_LR_EN_SHORT_REVIEWS_PICKLE,
                    IMDB_SGDC_EN_SHORT_REVIEWS_PICKLE,
                    IMDB_LSVC_EN_SHORT_REVIEWS_PICKLE]

files_imdb_fr = [WORDS_IMDB_FR,
                 WORDS_FEATURES_IMDB_FR,
                 FEATURE_SETS_IMDB_FR,
                 IMDB_NLTK_NB_FR_REVIEWS_PICKLE,
                 IMDB_MNB_BAYES_FR_REVIEWS_PICKLE,
                 IMDB_BERNOULLI_FR_REVIEWS_PICKLE,
                 IMDB_LR_FR_REVIEWS_PICKLE,
                 IMDB_SGDC_FR_REVIEWS_PICKLE,
                 IMDB_LSVC_FR_REVIEWS_PICKLE]

files_twitter_fr = [WORDS_TWITTER_EN,
                    WORDS_FEATURES_TWITTER_EN,
                    FEATURE_SETS_TWITTER_EN,
                    TWITTER_NLTK_NB_EN_PICKLE,
                    TWITTER_MNB_BAYES_EN_PICKLE,
                    TWITTER_BERNOULLI_EN_PICKLE,
                    TWITTER_LR_EN_PICKLE,
                    TWITTER_SGDC_EN_PICKLE,
                    TWITTER_LSVC_EN_PICKLE]

files_twitter_en = [WORDS_TWITTER_FR,
                    WORDS_FEATURES_TWITTER_FR,
                    FEATURE_SETS_TWITTER_FR,
                    TWITTER_NLTK_NB_FR_PICKLE,
                    TWITTER_MNB_BAYES_FR_PICKLE,
                    TWITTER_BERNOULLI_FR_PICKLE,
                    TWITTER_LR_FR_PICKLE,
                    TWITTER_SGDC_FR_PICKLE,
                    TWITTER_LSVC_FR_PICKLE]

os.chdir(os.getcwd())
os.chdir(os.path.realpath('..' + sep + 'src'))

files = files_imdb_short + files_twitter_fr + files_twitter_fr + files_twitter_en


@pytest.mark.parametrize("test_file", files)
def test_existence_pickles(test_file):
    try:
        load_pickle(test_file)
    except FileNotFoundError as exc:
        pytest.fail(exc)


vc_twitter_en = VoteClassifier("")
get_twitter_en_vc(vc_twitter_en)

pos_sentences = ["It was a very good movie. I loved it :)", "such a nice weather today!", "I love it"]


@pytest.mark.parametrize("sentence", pos_sentences)
def test_pos_tweets_vote_classifier(sentence):
    assert vc_twitter_en.classify(sentence, pos_max_thresh=0.5, neg_max_thresh=0.5) == "pos"


neg_sentences = ["It was a very bad movie. I hated it :(", "such a bummer... That sucks so hard",
                 "I hate it, thanks asshole.."]


@pytest.mark.parametrize("sentence", neg_sentences)
def test_neg_tweets_vote_classifier(sentence):
    assert vc_twitter_en.classify(sentence, pos_max_thresh=1, neg_max_thresh=0) == "neg"
    # with those settings, anything we test should be neg


# ## IMDB SHORT REVIEWS
vc_imdb_en = VoteClassifier("")
get_imdb_short_reviews_vc(vc_imdb_en)

pos_review = ["I loved this movie! Great acting!", "Incredible skills, kudos to the directors",
              "I love this movie it was so good! Fantastic performance! Amazing!",
              "I luved dis movie t'was so gud bruh",
              "Good movie. Great acting. Explores mundane roman animation as none has ever done."]


@pytest.mark.parametrize("sentence", pos_review)
def test_pos_review_vote_classifier(sentence):
    res = vc_imdb_en.classify(sentence, pos_max_thresh=0, neg_max_thresh=1)
    assert res == "pos" or res == "neu"


neg_review = ["This movie sucked. I hated it.",
              "This movie was pure shit", "Never seen anything so bad in my life"]


@pytest.mark.parametrize("sentence", neg_review)
def test_neg_review_vote_classifier(sentence):
    assert vc_imdb_en.classify(sentence, pos_max_thresh=0.5, neg_max_thresh=0.5) == "neg"
