'''
Created on Mar 5, 2021

@author: yann

Module that contains the RequestsHandler class.
'''

from collections import defaultdict
import re
from threading import Thread
import time
import traceback

from imdb_extraction import requetes_imdb
from local_extraction import LocalImporter
from network_utils import (is_connected_internet, TIMEOUT_DURATION,
                           is_googletrans_api_up, is_api_up, is_detectlanguage_api_up, is_tweepy_up, is_tweepy_api_key_valid)
from nlp_utils import convert_lang_format
from request_output import RequestOutput
from selenium.webdriver import firefox, chrome
from translator import translate_df, is_valid_target_lang
from twitter_extraction import requetes_twitter
from voting_system import (get_imdb_short_reviews_vc, get_imdb_allocine_vc,
                           get_twitter_en_vc, get_twitter_fr_vc, VoteClassifier)

import numpy as np
import pandas as pd

# Allowed keys in the request (followed by a KEY_SEPARATOR) :
SEARCH_KEYS = ['search', 'film', 'user', 'hashtag', 'lang', 'target', 'src', 'enddate', 'begindate', 'type',
               'year', 'id', 'maxentries', 'colname']

METADATA_KEYS = ['foundentries']

# Allowed characters in the request' attributes (A to Z lower case and capitals, 0 to 9, accentuated characters)
ALLOWED_CHARS = 'a-zA-Z0-9À-ÿ\-_'
FILM_TITLE_ALLOWED_CHARS = ':,\'\.!\?() '
FILM_YEAR_PATTERN = r'^(19|20)\d{2}$'
IMDB_ID_TT_PATTERN = r'^(tt\d{7}|tt\d{5})$'
IMDB_ID_NB_PATTERN = r'^(\d{5}|\d{7})$'

DEFAULT_LANG = 'en'

DEFAULT_MAX_ENTRIES = 50
MAX_ENTRIES_PATTERN = r'^([1-9][0-9]{0,2}|1000)$'

# Operators allowed
HASHTAG_KEY = '#'  # leading char for hashtag keywords
FILM_KEY = '\"'  # film title have to be entered between two apostrophes
USER_KEY = '@'  # leading char for user keywords
KEY_SEPARATOR = ':'  # separator between a search key and a search value
INTERSECTION_SEPARATOR = ','  # separator between two sub-requests
UNION_SEPARATOR = ' '  # separator between keywords and tuples of searchkeys/values
TMP_FILM_OPERATOR = '*'  # character to locate film_titles

POL_COLUMN_NAME = "polarity"  # name of the column that will contains the polarity data


class RequestsHandler:
    '''
    Main class of the package. This is where the requests from the control will be interpreted. Every flow of data
    will go through this class to go in or out of the model package.
    '''

    def __init__(self):
        '''
        Constructor
        '''

        self.str_request = ""  # the unprocessed request
        self.processed_data = None  # the data to return to the controller
        # self.api_keys = None #might not be useful as an attribute
        self.interpreted_request = {}  # will contain the list of dict extracted from the original str

        # Data extractors
        # self.imdb = new instance of extractor, with the argument read_api_key('imdb')
        # self.twitter = new instance of extractor, with the argument read_api_key('twitter')
        self.local_data = None  # new instance of local extractor
        self.imdb_webdriver = None

        # Classifiers
        # self.vc_en_imdb = get_imdb_long_reviews_vc()  # instantiates the VoteClassifier for IMDb
        self.vc_en_twitter = VoteClassifier("Twitter (en)")
        self.vc_fr_twitter = VoteClassifier("Twitter (fr)")
        self.vc_en_imdb = VoteClassifier("IMDb (en)")
        self.vc_fr_imdb = VoteClassifier("IMDb (fr)")

    def load_classifiers(self, multithreading=True):
        time.sleep(0.1)  # this line allows the time for the GUI to load correctly
        if multithreading:  # with multithreading
            vcs = [(self.vc_en_twitter, get_twitter_en_vc),
                   (self.vc_fr_twitter, get_twitter_fr_vc),
                   (self.vc_en_imdb, get_imdb_short_reviews_vc),
                   (self.vc_fr_imdb, get_imdb_allocine_vc)]

            threads = []

            for vc, get in vcs:
                t = Thread(target=get, args=[vc])
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

        else:  # without multithreading
            get_twitter_en_vc(self.vc_en_twitter)
            get_imdb_short_reviews_vc(self.vc_en_imdb)
            get_twitter_fr_vc(self.vc_fr_twitter)

    def __repr__(self):
        s = "\nRequestsHandler state:\n"
        s += "\t* Raw request: \"" + self.str_request + "\"\n"
        s += "\t* Interpreted request: " + str(self.interpreted_request) + "\n"
        s += "\t* Imported data? " + ("No" if self.local_data is None else "Yes") + ".\n"
        s += "\t* Has the data been processed? " + ("No" if self.processed_data is None else "Yes:\n" +
                                                    str(self.processed_data)) + ".\n"
        s += ("\t* Webdriver: " + ("Firefox" if isinstance(self.imdb_webdriver, firefox.webdriver.WebDriver) else "") +
              ("Chrome" if isinstance(self.imdb_webdriver, chrome.webdriver.WebDriver) else "") +
              ("None" if not self.imdb_webdriver else "")) + ".\n\n"
        return s

    def __interpret_request(self, request):
        if self.__check_basic_requirements(request):  # raises exceptions for basic invalidity
            self.str_request = request  # if there is no obvious errors, then it is passed as a value of the attribute
        self.__parse_request()
        self.__post_process_request()

        # checks semantic validity
        self.__validate_semantic()
        return True

    def __check_basic_requirements(self, req):
        '''Checks if the parameter of the method meets the basic requirements to be a valid request.
        The request is a str, it is not empty and contains only valid characters.
        '''

        if not(isinstance(req, str)):  # is a str
            raise RequestSyntaxError(req, "The request is expected to be a str.")

        if len(req) < 1:  # is not empty
            raise RequestSyntaxError(req, "The request is empty.")

        if not(self.__match_regex(req)):  # contains the expected characters
            raise RequestSyntaxError(req, "The request doesn't meet the expected syntax (invalid characters)." +
                                     "Please consult our User Manual.")

        return True

    def __match_regex(self, req):
        '''Method using a regular expression to check if the syntax of the request matches the requirements expected.
        '''

        basic_expression = ALLOWED_CHARS + HASHTAG_KEY + USER_KEY + KEY_SEPARATOR + INTERSECTION_SEPARATOR + UNION_SEPARATOR
        film_title_expression = ALLOWED_CHARS + FILM_TITLE_ALLOWED_CHARS  # film titles are treated separately

        pattern = r'([{0}]+|"[{1}]+"+)'.format(basic_expression, film_title_expression)

        regex = re.compile(pattern)
        results = regex.findall(req)  # finds every matching substring, treats separately film titles and the rest
        # print("result=" + str(result))

        if len(results) < 1:
            raise RequestSyntaxError(req, "The request is empty.")

        length_sum = 0
        for result in results:
            for r in result:
                length_sum += len(r)

        # if the sum of the lengths is equal to what findall has found, then it matched
        # otherwise, there is an error
        return length_sum == len(req)

    def __find_films_and_replace(self):
        '''Films titles are tricky to deal with in this project since they can use a lot of different characters.
        We have to treat them apart from the rest of the str.
        '''
        film_titles = []
        if FILM_KEY not in self.str_request:  # if no film title is detected in the original request
            return film_titles, self.str_request  # then nothing is done

        # we detect the film titles with their by looking at quotations marks.
        pattern = r'"[{}]+"'.format(ALLOWED_CHARS + FILM_TITLE_ALLOWED_CHARS)
        regex = re.compile(pattern)
        film_titles = regex.findall(self.str_request)

        tmp_request = self.str_request

        for i in range((len(film_titles))):
            # since titles can hold a broader range of characters, we have to replace them with a special key
            tmp_request = tmp_request.replace(film_titles[i], TMP_FILM_OPERATOR)
            film_titles[i] = film_titles[i].replace(FILM_KEY, '')  # removes the quotation mark from the stored value

        return (film_titles, tmp_request)

    def __parse_request(self):
        '''Method that naively goes through the raw string to parse it into a dict.
        Does some basic filtering in order to raise errors if needed.
        '''

        film_titles, tmp_request = self.__find_films_and_replace()  # removes film titles to deal with tricky characters
        tmp_request = tmp_request.lower()  # only the tmp_request is turned to lowercase
        films_index = 0  # index to keep count of where we are in the film's list
        intersect_requests = tmp_request.split(INTERSECTION_SEPARATOR)  # splits into several sub-requests

        if len(intersect_requests) > 1:
            raise RequestSyntaxError(self.str_request, "Multiple requests are not supported at the time." +
                                     " It will be supported in a future update.")

        tmp = []
        # by using a temporary variable, we ensure that the interpreted_request will only be updated if
        # the request is fully valid

        for req in intersect_requests:
            d = defaultdict(list)  # new empty dict of lists for this request

            if req == len(req) * UNION_SEPARATOR:  # when the request only contains spaces
                raise RequestSyntaxError(req, "One of the subrequest is only made of '" + UNION_SEPARATOR + "'.")

            if len(req) == 0:  # or if the sequence ',,' is met
                raise RequestSyntaxError(req, "One of the subrequest is empty.")

            union_requests = req.split(UNION_SEPARATOR)  # splits into keywords to interpret

            for u_req in union_requests:

                cut = u_req.split(KEY_SEPARATOR)

                if len(cut) == 2:
                    key = None
                    for search_key in SEARCH_KEYS:  # we verify if the key specified is a known key
                        if cut[0] == search_key:
                            key = search_key

                    if key is None or not cut[1]:  # if the word preceding the KEY_SEPARATOR isn't in SEARCH_KEYS then :
                        raise RequestSyntaxError(req, "The request contains invalid filters.")
                    else:
                        if key == 'lang':
                            try:
                                cut = convert_lang_format(cut[1])
                            except ValueError as e:
                                raise RequestSyntaxError(req, e)
                            d[key].append(cut)

                        elif key == 'year':
                            year_pattern = re.compile(FILM_YEAR_PATTERN)
                            if re.match(year_pattern, cut[1]):
                                d[key].append(cut[1])
                            else:
                                raise RequestSyntaxError(req, "The specified year is not a valid year.")

                        elif key == 'maxentries':
                            maxentries_pattern = re.compile(MAX_ENTRIES_PATTERN)
                            if re.match(maxentries_pattern, cut[1]):
                                d[key].append(cut[1])
                            else:
                                raise RequestSyntaxError(req, "The number of maximum entries you specified is not valid.")

                        elif key == 'id':
                            id_nb_pattern = re.compile(IMDB_ID_NB_PATTERN)
                            id_tt_pattern = re.compile(IMDB_ID_TT_PATTERN)

                            if re.match(id_nb_pattern, cut[1]):
                                d[key].append(cut[1])
                            elif re.match(id_tt_pattern, cut[1]):
                                d[key].append(cut[1][2:])  #  removes the tt
                            else:
                                raise RequestSyntaxError(req, "The entered IMDb ID is not valid.")

                        else:
                            d[key].append(cut[1])

                if len(cut) > 2:  # if there is more that one ':'
                    raise RequestSyntaxError(req, "You have put too many '" + KEY_SEPARATOR + "'.")

                if len(cut) == 1:  # that means no ':' was found
                    if len(u_req) != 0:  # useful when there is double spaces or ", "
                        if u_req[0] == HASHTAG_KEY:  # twitter hashtags
                            if len(u_req) == 1:
                                raise RequestSyntaxError(req, "Single '" + HASHTAG_KEY + "' detected.")
                            d['hashtag'].append(u_req[1:])
                            if not d['src']:  # if there is no source specified, then it becomes twitter
                                d['src'].append('twitter')

                        elif u_req[0] == USER_KEY:  # twitter users
                            if len(u_req) == 1:
                                raise RequestSyntaxError(req, "Single '" + USER_KEY + "' detected.")
                            d['user'].append(u_req[1:])
                            if not d['src']:
                                d['src'].append('twitter')

                        elif u_req[0] == TMP_FILM_OPERATOR:  # imdb film title
                            d['film'].append(film_titles[films_index])
                            films_index += 1
                            if not d['src']:
                                d['src'].append('imdb')

                        else:  # if no special char was found, then it's a "regular" keyword
                            d['search'].append(u_req)

            tmp.append(d)  # we put the constructed dict in the interpreted_request attr
        self.interpreted_request = tmp

    def __post_process_request(self):
        for idx, d in enumerate(self.interpreted_request):
            self.interpreted_request[idx] = {k: list(set(j)) for k, j in d.items()}  # removes duplicates
            for k in SEARCH_KEYS:
                if k not in d.keys():
                    self.interpreted_request[idx][k] = []  # gives an empty list if the key is not found

            for mk in METADATA_KEYS:
                self.interpreted_request[idx][mk] = []

    def __validate_semantic(self):
        '''Method to validate the coherence of a request.
        For example, a request that has a correct syntax but that contains both 'hashtag' and 'film' is not coherent,
        as we will only search for film titles in IMDb (and IMDb have any paradigm that resembles hashtags).
        As the prerequisites for the various source are very different, specific methods are called to ensure their
        validity : __validate_semantic_imdb, __validate_semantic_twitter and __validate_semantic_local
        '''
        # print(self.__repr__())
        for request in self.interpreted_request:

            # == Multiple sources
            if len(request['src']) > 1:
                raise RequestSyntaxError(self.str_request, "You cannot specify more than one source for your data extraction " +
                                         " in a single request.")
            elif not request['src']:
                raise RequestSyntaxError(self.str_request, "You haven't specified a source for your data.")

            # == IMDb
            if 'imdb' in request['src']:
                self.__validate_semantics_imdb(request)
            else:
                if request['film']:
                    raise RequestSyntaxError(self.str_request, "Films are specific to IMDb searches.")
                if request['year']:
                    raise RequestSyntaxError(self.str_request, "You can specify a year only when the source is IMDb " +
                                             "and you are already searching for a particular movie.")
                if request['id']:
                    raise RequestSyntaxError(self.str_request, "IDs are specific to IMDb searches.")

            # == Twitter
            if 'twitter' in request['src']:
                self.__validate_semantics_twitter(request)
            else:
                if request['hashtag']:
                    raise RequestSyntaxError(self.str_request, "Hashtags are specific to Twitter searches.")
                if request['user']:
                    raise RequestSyntaxError(self.str_request, "Users are specific to Twitter searches.")

            # == Local data
            if 'local' in request['src']:
                self.__validate_semantics_local(request)
            else:
                if request['colname']:
                    raise RequestSyntaxError(self.str_request, "You can specify the column to search in only for local searches.")
                if request['type']:
                    raise RequestSyntaxError(self.str_request, "You can only specify the type of data for requests on imported data.")

            # == Languages
            if len(request['lang']) < 1:
                request['lang'] = [DEFAULT_LANG]

            if request['target']:
                for idx, lang in enumerate(request['target']):
                    output = is_valid_target_lang(lang)
                    if output:
                        request['target'][idx] = output  # conversion to the ISO norm
                    else:
                        raise RequestSyntaxError(self.str_request, "\"" + lang + "\" is not a supported target language")

            if request['target'] and not is_api_up(is_googletrans_api_up, TIMEOUT_DURATION, "gooletrans"):
                if not is_connected_internet():
                    raise RequestSyntaxError(self.str_request, "You are not connected to the Internet at the moment. " +
                                             "No translation can be provided.")
                raise RequestSyntaxError(self.str_request, "You don't have any Google Translate API credits left for " +
                                         "today or the API is not available. No translation can be provided at the moment.")

            # == Max entries
            if not request['maxentries']:
                request['maxentries'] = [DEFAULT_MAX_ENTRIES]

    def __validate_semantics_local(self, request):
        '''Method that raises a RequestSyntaxError if the semantic prerequisites are not met for a local search.

        request -- a dict that contains a request are described in this module
        '''
        if not self.__check_presence_necessary_keys(request, ['colname', 'search']):
            raise RequestSyntaxError(self.str_request, "You must at least specify a column with the 'colname' keyword, or a search key.")

        if self.local_data is None:
            raise RequestSyntaxError(self.str_request, "In order to request an analysis on your imported data," +
                                     " you have to import your data first.")

        if len(request['colname']) > 1:
            raise RequestSyntaxError(self.str_request, "You can only search for data in atmost one column.")
        elif len(request['colname']) == 1:
            try:
                self.local_data.data[request['colname'][0]]
            except KeyError:
                raise RequestSyntaxError(self.str_request, "The specified column name doesn't exist")

        if len(request['type']) > 1:
            raise RequestSyntaxError(self.str_request, "You can only specify one type of data.")
        elif len(request['type']) == 1 and (request['type'][0] != 'tweets' and request['type'][0] != 'reviews'):
            raise RequestSyntaxError(self.str_request, "The specified data type can only be either 'tweets' or 'reviews'")
        elif not request['type']:
            request['type'] = 'tweets'  # if no type is specified, then we give it one

        if len(request['lang']) > 1 and not is_api_up(is_detectlanguage_api_up, TIMEOUT_DURATION, "detectlanguage"):
            message = ("No language detection can be provided at the moment, " +
                       "you have to specify the language in which the data is.")
            if not is_connected_internet():
                raise RequestSyntaxError(self.str_request, "You are not connected to the Internet. " +
                                         message)
            raise RequestSyntaxError(self.str_request, "You don't have any detect-language API credits left for " +
                                     "today or the API is not available. " + message)

    def __validate_semantics_imdb(self, request):
        '''Method that raises a RequestSyntaxError if the semantic prerequisites are not met for a IMDb search.

        request -- a dict that contains a request are described in this module
        '''
        if not is_connected_internet():
            if self.imdb_webdriver:
                raise RequestSyntaxError(self.str_request, "You are not connected to the Internet, please come back " +
                                         " when you have a stable Internet connection.")
            else:
                raise RequestSyntaxError(self.str_request, "No webdriver could be loaded and you are not connected " +
                                         "to the Internet. Please get a stable connection and restart the program.")

        if not self.imdb_webdriver:
            raise RequestSyntaxError(self.str_request, "No webdriver could be detected on your machine. " +
                                     "If neither a recent Google Chrome version nor a Firefox version are installed on your machine, " +
                                     "please do so. Otherwise, wait a few seconds or restart the program.")

        if not self.__check_presence_necessary_keys(request, ['film', 'id']):
            raise RequestSyntaxError(self.str_request, "In order to search for a film, you must specify an ID " +
                                     "or a film name between quotation marks.")

        if len(request['lang']) > 0 and 'en' not in request['lang']:
            raise RequestSyntaxError(self.str_request, "IMDb can only be searched in english as there is only " +
                                     "english data on this website.")

        if len(request['film']) > 1 or len(request['id']) > 1 or len(request['year']) > 1:
            raise RequestSyntaxError(self.str_request, "You can't search for more that one film at the moment.")

    def __validate_semantics_twitter(self, request):
        '''Method that raises a RequestSyntaxError if the semantic prerequisites are not met for a Twitter search.

        request -- a dict that contains a request are described in this module
        '''
        if not is_connected_internet():
            raise RequestSyntaxError(self.str_request, "You are not connected to the Internet, please come back " +
                                     " when you have a stable Internet connection.")

        if not is_api_up(is_tweepy_up, "twitter"):
            if not is_tweepy_api_key_valid():
                raise RequestSyntaxError(self.str_request, "Your Twitter API key is not valid.")
            raise RequestSyntaxError(self.str_request, "The Twitter API is not available at the moment, please " +
                                     "come back later.")

        if not self.__check_presence_necessary_keys(request, ['hashtag', 'user']):
            raise RequestSyntaxError(self.str_request, "In order to search for Twitter data, you must at least " +
                                     "specify a hashtag with a leading '" + HASHTAG_KEY + "' key or a user with a " +
                                     "leading '" +
                                     USER_KEY + "' key.")

        if len(request['user']) > 1:
            raise RequestSyntaxError(self.str_request, "You can't search for more that one user at the moment.")

    def __check_presence_necessary_keys(self, request: dict, keys: list):
        for key in keys:  # one if these keys has to be in the request
            if request[key]:
                return True
        return False

    def handle_request(self, req):
        '''This method is used by the Controller to send requests to the model.
        If the request is valid, it is processed by the various DataExtractors and the output data is then analyzed
        and classified. Otherwise, different errors are thrown to the Controller.

        req -- str that has to comply to the specified syntax and semantics of the program
        '''
        # checks syntax validity
        self.__interpret_request(req)
        extracted_data = pd.DataFrame()  # list where the data returned to the Controller will be stored

        self.processed_data = []  # will be the list of structured data analyzed and classified for each sub-request

        for d in self.interpreted_request:  # depending on the request src, we send the data to the various extractors
            print(self.__repr__())

            if 'twitter' in d['src']:
                try:
                    extracted_data = requetes_twitter(d)
                except ValueError as e:
                    raise RequestSyntaxError(self.str_request, str(e))
                except Exception:
                    traceback.print_exc()
                    raise RequestSyntaxError(self.str_request, "An unexpected error occurred with your Twitter search.")

            elif 'imdb' in d['src']:
                try:
                    extracted_data = requetes_imdb(d, self.imdb_webdriver)
                except ValueError as ve:  # in the case the ID doesn't exist
                    raise RequestSyntaxError(self.str_request, str(ve))
                except Exception as e:
                    # catches the exceptions thrown by the imdb extractor. At least two are needed
                    #    - when the user needs to specify a year
                    #    - when the user needs to specify an imdb id because specifying a year wasn't enough
                    traceback.print_exc()
                    raise RequestSyntaxError(self.str_request, "An unexpected error occurred with your IMDb search.")

            elif 'local' in d['src']:
                try:
                    extracted_data = self.local_data.extract_data(d)  # extract rows from the loaded dataset
                except ValueError as e:  #  in the case no row was found
                    raise RequestSyntaxError(self.str_request, e)

            print("Result from " + d['src'][0] + " extraction:\n" + str(extracted_data.head()))

            if 'src_lang' in extracted_data:  # if we were able to retrieve detect languages
                per_lang_extracted_data = []
                for lang in d['lang']:
                    per_lang_data = extracted_data.loc[extracted_data['src_lang'] == lang]  # divides the dataset by lang
                    if not per_lang_data.empty:
                        if 'type' in d:
                            if 'tweets' in d['type']:  # in the case those are tweets
                                polarity = self.__get_pol_twitter(per_lang_data, lang, colname=d['colname'][0])
                            else:  # or reviews
                                polarity = self.__get_pol_imdb(per_lang_data, lang, colname=d['colname'][0])
                        elif 'twitter' in d['src']:
                            polarity = self.__get_pol_twitter(per_lang_data, lang, colname=d['colname'][0])
                        elif 'imdb' in d['src']:
                            polarity = self.__get_pol_imdb(per_lang_data, lang, colname=d['colname'][0])
                        per_lang_data[POL_COLUMN_NAME] = np.asarray(polarity)  # add the polarity to the df
                        per_lang_extracted_data.append(per_lang_data)

                extracted_data = pd.concat(per_lang_extracted_data)  # .sort_index() (maybe it will be sorted w/o it?)

            else:  # otherwise, we use the first language, hoping it will cover most of the data
                if 'type' in d:
                    if 'tweets' in d['type']:  # in the case those are tweets
                        polarity = self.__get_pol_twitter(extracted_data, d['lang'][0], colname=d['colname'][0])
                    else:  # or reviews
                        polarity = self.__get_pol_imdb(extracted_data, d['lang'][0], d['colname'][0])
                    extracted_data[POL_COLUMN_NAME] = np.asarray(polarity)  # add the polarity to the df
                elif 'twitter' in d['src']:
                    polarity = self.__get_pol_twitter(per_lang_data, d['lang'][0], colname=d['colname'][0])
                elif 'imdb' in d['src']:
                    polarity = self.__get_pol_imdb(per_lang_data, d['lang'][0], colname=d['colname'][0])

            for lang in d['target']:
                extracted_data = translate_df(extracted_data, d, lang)

            # we extract the frequency of the most common words and had it to the output
            request_output = RequestOutput(self.str_request, d, extracted_data, POL_COLUMN_NAME)
            self.processed_data.append(request_output)

        print(self.__repr__())
        return self.processed_data

    def import_local_data(self, path):
        self.local_data = LocalImporter(path)
        try:
            print(self.local_data.data.head())
        except AttributeError:
            print("The file could not be read hence the imported data is None.")

    def __get_pol_twitter(self, extracted_data, language, colname):
        # wrapper method to lighten the code for language choice
        try:  # in the event no model was loaded
            if language == 'fr':
                return self.vc_fr_twitter.classify(extracted_data, colname, pos_max_thresh=0.7, neg_max_thresh=0.2)
            if language == 'en':
                return self.vc_en_twitter.classify(extracted_data, colname, pos_max_thresh=0.7, neg_max_thresh=0.2)
        except AttributeError as ae:
            raise RequestSyntaxError(self.str_request, str(ae))

    def __get_pol_imdb(self, extracted_data, language, colname):
        # wrapper method to lighten the code for language choice
        try:  # in the event no model was loaded
            if language == 'fr':
                return self.vc_fr_imdb.classify(extracted_data, colname, pos_max_thresh=0.7, neg_max_thresh=0.2)
            if language == 'en':
                return self.vc_en_imdb.classify(extracted_data, colname, pos_max_thresh=0.7, neg_max_thresh=0.2)
        except AttributeError as ae:
            raise RequestSyntaxError(self.str_request, str(ae))


class RequestSyntaxError(Exception):
    '''Base class for request syntax exceptions

    Attributes:
        req -- input request which caused the error
        message -- explanation of the error
    '''

    def __init__(self, req, message):
        self.req = req
        self.message = message
        super().__init__(self.message)
