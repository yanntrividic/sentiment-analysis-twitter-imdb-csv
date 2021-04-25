'''
Created on Mar 9, 2021

@author: Yann
'''

import pickle
from pandas import read_csv


def load_pickle(path, message="", verbose=False):
    '''Loads a pickle file if the used path exists, the error handling has to be done on a higher level

    path -- a valid path for a PICKLE file
    message -- the leading message to display
    verbose -- if we want to display a message

    returns the object contained in the pickle file
    '''
    with open(path, "rb") as pickle_rfile:
        loaded = pickle.load(pickle_rfile)
    pickle_rfile.close()
    if verbose:
        print(message + " loaded from " + path)
    return loaded


def read_csv_to_df(path):
    '''Reads a CSV file to make it fit into a dataframe, the delimiter is set to ',', the file has to have a header row
    and everything is set to default according to the Dataframe.to_csv documentation
    '''
    try:
        df = read_csv(path, delimiter=',', header=0)  # i.e. the file HAS TO have a header as first row and "," seps.
        df = df.dropna()  # removes rows that have empty cells
        return(df)
    except FileNotFoundError:
        print(path, " could not be read.")
        return None
