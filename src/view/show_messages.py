'''
Created on Apr 12, 2021

@author: jack

Module to display various message
'''

import sys

from PyQt5 import QtCore

RED = "#dc0000"
BLACK = "#000000"
WHITE = "#ffffff"


def update_mainwindow_console(ui):
    '''
    Function for updating status on mainwindow_console
    '''
    target = ui.comboBoxTargetLanguage.currentText()

    text = ("Entry:" + ui.user_entry + " Search engine: " + ui.search_engine +
            " - French: " + str(ui.french) + " - English: " + str(ui.english) +
            (" - Target language: " + target if target else ""))

    if not getattr(sys, 'frozen', False):  # if it is not an executable
        ui.mainwindow_console.setText(text)
    print(text)


def show_on_mainwindow_console(ui, text):
    '''
    Function for showing some text status on mainwindow_console
    '''
    if not getattr(sys, 'frozen', False):
        ui.mainwindow_console.setText(text)
    print(text)


def show_message(ui, message, error=False):
    '''
    Function for displaying error in the right place
    '''
    if ui.get_message_location() == "dashboard":
        show_message_on_dashboard(ui, message, error)
    else:
        show_message_on_mainmenu(ui, message, error)


def show_message_on_mainmenu(ui, message, error=False):
    '''
    Function for displaying a simple message in the dashboard
    '''
    _translate = QtCore.QCoreApplication.translate
    ui.labelErrorMainmenu.show()
    ui.labelErrorMainmenu.setText(_translate("MainWindow",
                                             "<html><head/><body><p align=\"center\"><span style=\" color:" +
                                             (RED if error else BLACK) + ";\">" +
                                             message + "</span></p></body></html>"))


def show_message_on_dashboard(ui, message, error=False):
    '''
    Function for displaying a simple message in the dashboard
    '''
    _translate = QtCore.QCoreApplication.translate
    ui.labelErrorDashboard.show()
    ui.labelErrorDashboard.setText(_translate("MainWindow",
                                              "<html><head/><body><p align=\"center\"><span style=\" color:" +
                                              (RED if error else WHITE) + ";\">" +
                                              message + "</span></p></body></html>"))
