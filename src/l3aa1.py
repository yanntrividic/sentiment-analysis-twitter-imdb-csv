'''
Created on Mar 9, 2021

@author: yann

Launcher of our app, sets the environment and instanciates the Controller
'''

import multiprocessing
import platform
import sys

import _init
from control import Controller

if __name__ == '__main__':
    if platform.system() == 'Windows':  #  allows multithreading / multiprocessing on Windows
        multiprocessing.freeze_support()

    controller = Controller()

    sys.exit(controller.app.exec_())
