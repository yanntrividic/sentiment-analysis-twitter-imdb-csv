'''
Created on Mar 5, 2021

@author: yann

Module that contains the DataExtractor abstract class.
'''

from abc import abstractmethod, ABCMeta
from pandas import DataFrame


class DataExtractor(metaclass=ABCMeta):  # DataExtractor is specified to be an abstract class
    '''Abstract class which will be used to extract data for various sources. Those sources can
    be IMDb, Twitter, a local CSV file.
    '''

    request: dict  # implies that the request attribute has to be a dict
    data: DataFrame  #  and that data has to be a pandas DataFrames

    @abstractmethod
    def extract_data(self, request):
        '''Method called to extract data from the specified source of the inherited object according to the request.
        '''
        pass
