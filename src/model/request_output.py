'''
Created on Apr 8, 2021

@author: yann

Module that contains the RequestOutput class.
'''

import re

from nlp_utils import tokenize_and_remove_stopwords
import nltk
from nltk.tokenize import RegexpTokenizer
import pandas as pd

DATES_PATTERN = r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'  # will match yyyy-mm-dd and also yyyy-m-d


class RequestOutput():
    '''Class used to stored a review of a request and its results
    '''

    def __init__(self, str_request: str, interpreted_request: dict, raw_data: pd.DataFrame, pol_col: str):
        '''Constructor of the class
        '''
        self.str_request = str_request
        self.interpreted_request = interpreted_request
        self.raw_data = raw_data
        self.pol_col = pol_col
        self.statistics = self.__compute_statistics()

    def __repr__(self):
        s = "\nRequestOutput:\n"
        s += "\t* Raw request: \"" + self.str_request + "\"\n"
        s += "\t* Interpreted request: " + str(self.interpreted_request) + "\n"
        s += "\t* Raw data head:\n" + str(self.raw_data.head(10)) + "\n"
        s += "\t* Statistics:"

        for k in self.statistics.keys():
            s += "\n\n" + k + ": " + str(self.statistics[k])

        return s

    def get_colnames(self, as_list=True):
        '''Returns the names of the columns of the dataframe.

        as_list -- boolean, returns the value as a list by default, otherwise, it will be an Index object.
        '''
        if as_list:
            return self.raw_data.columns.values.tolist()
        else:
            return self.raw_data.columns

    def get_polarity_data(self, as_list=True):
        '''Returns the polarity data of the dataframe.

        as_list -- boolean, returns the value as a list by default, otherwise, it will be a pandas' Dataframe.
        '''
        if as_list:
            return self.raw_data[self.pol_col].values.tolist()
        else:
            return self.raw_data[self.pol_col]

    def get_textual_data(self, as_list=True):
        '''Returns the textual data of the dataframe.

        as_list -- boolean, returns the value as a list by default, otherwise, it will be a pandas' Dataframe.
        '''
        if as_list:
            return self.raw_data[self.get_textual_data_colname()].values.tolist()
        else:
            return self.raw_data[self.get_textual_data_colname()]

    def get_src_langs(self, as_list=True):
        '''Returns the source languages of the dataframe if it exists. Returns None otherwise

        as_list -- boolean, returns the value as a list by default, otherwise, it will be a pandas' Dataframe.
        '''
        if 'src_lang' in self.raw_data:
            if as_list:
                return self.raw_data['src_lang'].values.tolist()
            else:
                return self.raw_data['src_lang']
        else:
            return None

    def get_polarity_colname(self):
        '''Returns the polarity column name
        '''
        return self.pol_col

    def get_textual_data_colname(self):
        '''Returns the textual data column name of the dataframe as a str.
        '''
        return self.interpreted_request['colname'][0]

    def __compute_statistics(self):
        stats = {}
        stats['word_frequencies'] = self.__compute_words_frequencies()

        try:
            stats['pol_data_per_day'] = self.__compute_pol_data_per_period('day')
            stats['pol_data_per_month'] = self.__compute_pol_data_per_period('month')
            stats['pol_data_per_year'] = self.__compute_pol_data_per_period('year')

        except ValueError as e:  #  in the event there is no date column
            # FIXME: treat this possibily more elegantly
            print(str(e))

        return stats

    def __compute_words_frequencies(self):
        '''Returns the most common words with their frequency without the 'excluded' words

        excluded -- a list of words to forget exclude from the results
        sentences -- a list of sentences in which we want to count occurrences
        '''

        excluded = self.interpreted_request['search'] + self.interpreted_request['hashtag']
        sentences = self.get_textual_data()
        langs = self.get_src_langs()

        # if we don't have data about the source language, we use the first language specified by the user
        if langs is None:
            langs = [self.interpreted_request['lang'][0] for _ in range(len(sentences))]

        tokenizer = RegexpTokenizer(r'\w+')  # will remove punctuation
        all_words = []

        for idx, sent in enumerate(sentences):
            tmp = tokenize_and_remove_stopwords(sent.lower(), langs[idx])
            for word in tmp:
                tok = tokenizer.tokenize(word)
                if tok:
                    if len(tok[0]) > 2:  # only adds "big" words
                        all_words += tok

        freqs = nltk.FreqDist(all_words)

        for key in list(freqs.keys()):
            if key in excluded:
                del freqs[key]

        return freqs

    def __compute_pol_data_per_period(self, period):
        if period not in ['day', 'month', 'year']:
            raise AttributeError("The period you asked for is invalid.")

        date_col = None

        dates_possible_colname = ['date', 'dates', 'datetime', 'time']
        for s in dates_possible_colname:
            if s in self.get_colnames(True):
                date_col = s

        # FIXME: do more test and add regex patterns
        if not date_col:
            # FIXME: see discord's error trace
            date_col = search_column(self.raw_data, regex=DATES_PATTERN)

        results = {}

        if date_col:
            dates = self.raw_data[[date_col, self.pol_col]]

            regex = re.compile(DATES_PATTERN)

            for _, row in dates.iterrows():
                if re.match(regex, row['date']):

                    if period == 'day':
                        d = row['date']
                    if period == 'month':
                        tmp = row['date'].split('-')
                        d = "-".join(tmp[:2])
                    if period == 'year':
                        d = row['date'].split('-')[0]

                    if d not in results:
                        results[d] = [("pos", 0), ("neu", 0), ("neg", 0)]
                    for idx, tuple in enumerate(results[d]):
                        key, value = tuple
                        if row[self.pol_col] == key:
                            results[d][idx] = (key, value + 1)

        return results

    def get_comprehensive_request_summary(self):
        '''Function to get a comprehensive summmary of the user's search out of the interpreted request
        '''
        request = self.interpreted_request

        summary = ""
        summary += " ".join(request['search'])
        if request['film']:
            summary += (" " if summary else "") + " ".join(request['film'])

        if request['id']:
            summary += (" tt" if summary else "") + " tt".join(request['id'])

        if request['year']:
            summary += (" " if summary else "") + " ".join(request['year'])

        if request['hashtag']:
            summary += "#" + " #".join(request['hashtag']) + (" " if summary else "")

        if request['user']:
            summary += "@" + " @".join(request['user']) + (" " if summary else "")

        if request['colname'] and 'local' in request['src']:
            summary += " colname:" + request['colname'][0]

        if request['type']:
            summary += " type:" + request['type']

        return summary


def search_column(data: pd.DataFrame, key=None, regex=None):
    '''Function to search if a word is present or a regex pattern is matched in a dataframe column

    data -- pd.DataFrame in which to look
    key -- word to look for
    regex -- a string pattern

    returns the column name in which the key/regex pattern was found
    '''
    if (key and regex) or (not key and not regex):
        raise ValueError('You can search for a key or a regex pattern, but not for both')

    for colname in data:  # and for each column in our dataframe
        column = data[colname]  # we extract the column
        column = column.astype(str).str.lower()  # we make it lowercase in order to match our key

        if key:
            if not data[column.str.contains(key)].empty:  # and check if the key is somewhere in the col
                #  request['colname'] = [colname]  # if so, the column is this col.
                return colname

        if regex:
            for _, row in data.iterrows():
                words = re.findall(regex, str(row[colname]))
                if words:
                    return colname

    return None

