'''
Created on Apr 18, 2021

@author: jack
'''

import os
import sys
import unittest
import pytest

from main_window import Ui_MainWindow


def __init__(self):
        '''
        Constructor
        '''
        self.ui = Ui_MainWindow(self.app)
        self.ui.setupUi(self.main_window)

def test_init_mainwindow(self):
        
        self.assertEqual(self.ui.get_french(),False)
        self.assertEqual(self.ui.get_english(),True)
        self.assertEqual(self.ui.get_user_entry(),"")
        self.assertEqual(self.ui.get_search_engine(),False)
        self.assertEqual(self.ui.get_csv_path(),"")
        self.assertEqual(self.ui.get_file_loaded(),False)
        self.assertEqual(self.ui.get_message_location(),"dashboard")
        self.assertEqual(self.ui.get_target_language(),"")
        self.assertEqual(self.ui.get_pos_click(),"")