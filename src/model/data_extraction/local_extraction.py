'''
Created on Mar 5, 2021

@author: yann

Module that contains the LocalImporter class (implements the DataExtractor class).
'''

import re

from extractor import DataExtractor
from file_reader import read_csv_to_df
from translator import remove_unwanted_langs

import pandas as pd


class LocalImporter(DataExtractor):
    '''This class is the bridge between the Classifier and the RequestsHandler relative to imported data contained
    in CSV files. In order to analyze imported data, the user has to load a CSV file and initialize this class
    with its content.
    '''

    def __init__(self, path):
        '''
        Constructor
        '''

        if not(isinstance(path, str)):  # is a str
            raise ValueError("The path is expected to be a str.")
        else:
            self.path = path
            self.data = read_csv_to_df(self.path)

        self.request = {}

    def extract_data(self, request):
        '''From the request passed as argument is returned a dataframe that contains the data wanted by the user

        request -- a valid dict according to the syntax and semantics described in requests_handler.py
        returns a dataframe that contains the extracted rows to classify
        raises a ValueError if no row was found
        '''

        temp = pd.DataFrame

        if request['search']:
            detected_col = False

            if not request['colname']:  # otherwise, we iterate through the df to look for the specified keyword
                detected_col = self.__search_colname(request)
                if not detected_col:
                    raise ValueError("The submitted request didn't result in the extraction of any data.")

            colname = request['colname'][0]
            extracted_rows_index = []

            for idx, row in self.data.iterrows():
                words = re.findall(r'\w+', row[colname].lower())
                if set(request['search']).issubset(words):
                    extracted_rows_index.append(idx)

            if not extracted_rows_index and detected_col:
                raise ValueError("We detected an occurrence of your search in the '" + colname + "' column though no " +
                                 "data could be extracted. Try to specify the column to search with the 'colname' keyword.")

            if extracted_rows_index:
                temp = self.data.loc[extracted_rows_index]

        else:  # it means a colname was specified and the classifier will know where to look
            temp = self.data  # change this

        if not temp.empty:
            temp = self.__subset_data_maxentries(request, temp)
            result = self.__add_src_lang_col(request, temp)

            if not result.empty:
                maxentries = result.shape[0] if request['maxentries'][0] > result.shape[0] else request['maxentries'][0]
                # print(maxentries, result.shape[0])
                return result.sample(maxentries).sort_index()

        raise ValueError("The submitted request didn't result in the extraction of any data.")

    def __subset_data_maxentries(self, request: dict, temp: pd.DataFrame):
        """Method to limit the amount of data sent to detect_lang and save API credits.
        """
        req_maxentries = int(request['maxentries'][0])
        request['foundentries'] = [temp.shape[0]]
        real_maxentries = request['foundentries'][0] if req_maxentries > request['foundentries'][0] else req_maxentries

        if request['foundentries'][0] > real_maxentries * 2:
            nb_entries_before_lang_detect = real_maxentries * 2
        elif request['foundentries'][0] > req_maxentries:
            nb_entries_before_lang_detect = request['foundentries'][0]
        else:
            nb_entries_before_lang_detect = real_maxentries

        return temp.sample(nb_entries_before_lang_detect)
        # the factor 2 is here to make sure we will have more

    def __add_src_lang_col(self, request: dict, temp: pd.DataFrame):
        """If we have enough credits, the language will be added. Otherwise an AttributeError will be raised.
        """
        try:
            # on regarde la langue avant de filtrer avec maxentries, il faudrait faire dans l'autre sens
            return remove_unwanted_langs(temp, request['colname'][0], request['lang'])
        except AttributeError:  # when we reach the daily limit of detection with detectlanguage
            return temp

    def __search_colname(self, request: dict):
        '''Method that detects the column in which we want to search for the data
        The user should be warned that the wrong column could be found, and that if he wants to be sure that
        the right column is found, he has to use the 'colname' keyword in its request.

        request -- a dict that respects the request syntax defined by the requests_handler module.

        Returns True if a column was found. In that case, a new value is given to the 'colname' key of request.
        Otherwise, returns False.
        '''
        for key in request['search']:  # for each word in search
            for colname in self.data:  # and for each column in our dataframe
                column = self.data[colname]  # we extract the column
                column = column.astype(str).str.lower()  # we make it lowercase in order to match our key
                if not self.data[column.str.contains(key)].empty:  # and check if the key is somewhere in the col
                    request['colname'] = [colname]  # if so, the column is this col.
                    return True
        return False
