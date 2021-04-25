'''
Created on Apr 1, 2021

@author: yann
'''

import requests
from urllib3.exceptions import NewConnectionError, MaxRetryError, TimeoutError, ConnectionError

from googletrans.client import Translator

from config import DETECT_LANGUAGE_KEY
import googletrans as gt
import numpy as np
import pandas as pd

try:  #  when not connected to internet
    import deep_translator as dt
except requests.exceptions.ConnectionError:
    pass

SUPPORTED_TARGET_LANGUAGES = gt.LANGUAGES


def is_lang_valid(data, valid_langs: list):
    """Detects the language of the sentences passed as arguments using the detect_language API
    and returns data based on the type of input given.
    For now, with the current key, we can get up to 1000 requests/day or 1 MB/day

    valid_langs -- list of str that contains the admitted languages
    data can be a str, and a single boolean will be returned
    data can be a list, and a list of tuples will be returned, the first entry is the original index
    of the data, and the second one is the valid language detected for this data
    """
    try:
        dt
    except NameError:  #  if not connected to the internet
        try:
            import deep_translator as dt
        except requests.exceptions.ConnectionError:
            raise AttributeError("You are not connected to the Internet.")

    try:
        if isinstance(data, str):
            lang = dt.single_detection(data, api_key=DETECT_LANGUAGE_KEY)
            return lang in valid_langs
        if isinstance(data, list):
            langs = dt.batch_detection(data, api_key=DETECT_LANGUAGE_KEY)
            return [(i, langs[i]) for i in range(len(data)) if langs[i] in valid_langs]

    except (AttributeError, MaxRetryError, NewConnectionError, TimeoutError, ConnectionError):
        raise AttributeError("No more API credits available for language detection today.")

    #  when the dt import worked but there is still a connection issue
    except requests.exceptions.ConnectionError:
        raise AttributeError("You were disconnected from the Internet.")


def translate_google(data, target, src="auto", googletrans=True):
    """ Wrapper for the GoogleTranslate API. Make sure a recent version is installed, as the previous
    ones are buggy (pip install googletrans==3.1.0a0 is fine).
    For now, without a key, we can get up to 1000 requests/hour, 5000 chars per request

    If it's not enough, we could use a proxy to augment this ceiling. Or pay for a private key.
    Concurrent requests gets you blocked if no timeout is implemented.

    data -- either a string or a list of strings
    target -- the target language to translate the string in
    src (optional) -- the src language of the data
    googletrans -- boolean to specify if we wanna use directly the GoogleTrans API or the deep-translation
    wrapper
    """
    if googletrans:
        # if not is_googletrans_api_up():  # might speed up results if the api is not up
        #    return None

        translator = Translator()
        if isinstance(data, str):
            output = translator.translate(data, dest=target)
            text_output = output.text
            error_code = output._response.status_code

        if isinstance(data, list):
            translations = translator.translate(data, dest=target)
            text_output = [t.text for t in translations]
            error_code = translations[-1]._response.status_code  # the last request's code

        if error_code != 429:
            return text_output
        else:  # it means we have already sent too many requests
            return None
    else:
        if isinstance(data, str):
            translated = dt.GoogleTranslator(source=src, target=target).translate(text=data)
        if isinstance(data, list):
            translated = dt.GoogleTranslator(source=src, target=target).translate_batch(data)
    return translated


def translate_df(df: pd.DataFrame, request: dict, target: str):
    """Method to automatically translate the column of a dataframe to a target language using the
    Google Translate API

    df -- a dataframe that contains the data we'll work with
    text_col -- name of the column that contains the sentences to translate
    src_lang_col -- name of the column that contains the detected language associated with the text
        this parameter optimizes the amount of data sent to the API (see limitations in translate_google)
    target -- target language to translate the sentence in.
    """
    sents = df[request['colname'][0]].values.tolist()

    if 'src_lang' in df:
        src_lang = df['src_lang'].values.tolist()
    else:
        # FIXME If possible
        src_lang = [request['lang'][0] for _ in range(df.shape[0])]  # list of langs based on the languages provided

    indices = []  # keep track on the indices
    sents_to_translate = []  # will contain the sentences that we wanna translate

    for i in range(len(sents)):
        if src_lang[i] != target:  # if the sentence is not already in the target language
            indices.append(i)
            sents_to_translate.append(sents[i])

    translated = translate_google(sents_to_translate, target, googletrans=True)  # translation happens here

    if translated:  # means the api request was successful
        list_to_df = []
        j = 0
        for i in range(len(sents)):
            if i in indices:
                list_to_df.append(translated[j])
                j += 1
            else:
                list_to_df.append("")

        df[target + "_trans"] = np.asarray(list_to_df)  # and we add a column to the dataframe
    return df


def remove_unwanted_langs(df, column, valid_langs):
    """Checks if the data extracted is in the wanted language or not.

    df -- the dataframe to process
    column -- the column where the text is contained
    valid_langs -- a list of admitted languages
    """
    df = df.reset_index(drop=True)
    data = df[column].values.tolist()  # gets the values of the specified column as list
    valids = list(zip(*is_lang_valid(data, valid_langs)))  #  checks if the detected langs is in the valid_langs

    if valids:
        try:
            for idx in range(len(data)):
                if idx not in valids[0]:
                    df = df.drop([idx])
            df['src_lang'] = valids[1]
            return df

        except IndexError:  # in the case no valid data is found, an empty dataset is returned
            return df.iloc[0:0]

    else:
        return df.iloc[0:0]


def translate_linguee(word, src, target):
    if isinstance(word, str):
        translated = dt.LingueeTranslator(source=src, target=target).translate(word)
    if isinstance(word, list):
        translated = dt.LingueeTranslator(source=src, target=target).translate(word)
    return translated


def is_valid_target_lang(lang: str):
    '''Detects in the str passed as argument is a language supported by the googletrans API. If so, it returns
    the ISO639-1 id associated with this language, otherwise, it returns False.

    lang -- the string to detect
    '''
    for key, value in SUPPORTED_TARGET_LANGUAGES.items():
        if lang == key or lang == value:
            return key
    return False

# if __name__ == '__main__':
#     from file_reader import read_csv_to_df
#
#     df = read_csv_to_df("../resources/data_titanic.csv")
#     txt = " ".join(df['texte'].values.tolist())[:1000]
#     result = Value('i', 0)
#
#     print(is_lang_valid(txt, ['fr']))
#
#     while(True):
#         print(str(is_api_up(is_googletrans_api_up, 5, "test")))
