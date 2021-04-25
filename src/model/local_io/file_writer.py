'''
Created on Mar 9, 2021

@author: Yann
'''

import ntpath
import os
import pickle

import pandas as pd

ntpath.basename("a/b/c")


# -*-coding: utf-8 -*
def save_pickle(to_serialize, path, message="", verbose=False):
    '''
    '''
    try:
        save_pickle = open(path, "wb")
    except(FileNotFoundError):
        head, _ = ntpath.split(path)  #  generates a new folder if it doesn't already exist
        os.makedirs(head, exist_ok=True)
        save_pickle = open(path, "wb")  # and saves the pickle in it
    pickle.dump(to_serialize, save_pickle)
    save_pickle.close()
    if verbose:
        print(message + " saved at " + path + "\n")


def write_csv_to_df(data: pd.DataFrame, path: str):
    '''Saves a dataframe into a CSV file. Every parameter has its default value according to the pandas.Dataframe.to_csv's
    documentation

    data -- a pandas dataframe
    path -- has to be a valid path, the error handling must be done higher in the program
    '''
    data.to_csv(path)
