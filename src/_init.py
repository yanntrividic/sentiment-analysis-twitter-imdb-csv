'''
Created on Apr 16, 2021

@author: yann

Module that correctly sets up the environment's variables before really going into it.
'''

import os
import sys
import nltk

MODULES_PATHS = [r"/controller",
                 r"/model",
                 r"/model/analysis",
                 r"/model/local_io",
                 r"/model/data_extraction",
                 r"/view",
                 r"/setup"]

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    APPLICATION_PATH = sys._MEIPASS
else:
    APPLICATION_PATH = os.path.dirname(os.path.abspath(__file__))

if APPLICATION_PATH:
    print("cwd: " + APPLICATION_PATH)
    os.chdir(APPLICATION_PATH)

for rel_path in MODULES_PATHS:  # correctly adds our modules to be PYTHONPATH
    abs_path = APPLICATION_PATH + rel_path
    if abs_path not in sys.path:
        sys.path.append(abs_path)

nltk_files = [(r"tokenizers/punkt", 'punkt'),
              (r"corpora/stopwords", 'stopwords'),
              (r"corpora/movie_reviews", 'movie_reviews'),
              (r"corpora/twitter_samples", 'twitter_samples')]

for nltk_file in nltk_files:  #  if files are missing because the user has not dowloaded them yet
    location, name = nltk_file
    try:
        nltk.data.find(location)
    except LookupError:
        nltk.download(name)
