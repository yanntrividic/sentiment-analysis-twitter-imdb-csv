'''
Created on Mar 10, 2021

Toolkit to use basic NLP methods specific to our usecase.
@author: yann
'''

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# conversion table between various language
# TODO: remove comments once the following languages are implemented
EN = {'name': 'english', 'en_name': 'english', '639-1': 'en'}
FR = {'name': 'français', 'en_name': 'french', '639-1': 'fr'}
# DE = {'name': 'deutsch', 'en_name': 'german', '639-1': 'de'}
# ES = {'name': 'español', 'en_name': 'spanish', '639-1': 'es'}

SUPPORTED_LANG = [EN, FR]  # , DE, ES]


def convert_lang_format(to_convert, target='639-1'):
    '''Converts the argument to its equivalent in the specified target format code and returns this value.
    Raises an error if the language is not found in SUPPORTED_LANG

    to_convert -- str to convert
    target -- target format (default value : '639-1')
    '''
    for lang in SUPPORTED_LANG:  # we iterate through the supported languages
        for key in lang:
            if to_convert.lower() == lang[key]:
                return lang[target]
    raise ValueError("The language you try to use is not supported by this program.")


def tokenize_and_remove_stopwords(sent, lang):
    '''Tokenizing means to separate semantic groups of words. Stopwords are words that holds no semantic meaning,
    for example 'the', 'of', etc., are stopwords for the english language.

    sent -- A sentence in natural language
    lang -- The language of the sentence
    '''

    if not(isinstance(sent, str)):
            raise ValueError("This parameter has to be a sentence.")

    lang = convert_lang_format(lang, "en_name")

    stop_words = set(stopwords.words(lang))
    word_tokens = word_tokenize(sent)

    return [w for w in word_tokens if w not in stop_words]


def stem_words(words):
    '''Stemming consists in reducing words to their word stem (i.e. base or root form)
    The Porter stemmer is english specific. For french, an option could be the 'spacy' module and its lemma_ attribute.
    https://stackoverflow.com/questions/13131139/lemmatize-french-text

    words -- a list of english words
    return a list of stemmed words
    '''
    ps = PorterStemmer()
    stemmed = []
    for w in words:
        stemmed.append(ps.stem(w))
    return stemmed


def lemmatize_words(words):
    '''Lemmatizing is similar to stemming as it changes words without changing the essence of the words.
    Like stem_words, models for other languages than english are more difficult to find, this function
    only works with english words for now (WordNet is an english database).

    words -- a list of english words
    return a list of lemmatized words
    '''

    lemmatizer = WordNetLemmatizer()
    lemmatized = []
    for w in words:
        lemmatized.append(lemmatizer.lemmatize(w))
        # will do a better job if we give it the POS tagging as a second parameter
    return lemmatized


def words_in_sentence(sentence, words):
    print(sentence)
    lsent = sentence.lower()
    for word in words:
        word = word.lower()

    for word in words:
        if word in lsent:
            return True

    return False
