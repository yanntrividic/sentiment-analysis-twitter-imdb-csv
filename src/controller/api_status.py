'''
Created on Apr 12, 2021

@author: yann

Module to control the API status panel in the dashboard by using QThreads and the network_utils module
'''
from PyQt5.QtGui import QPixmap
from background_work import Worker
from main_window import WARNING_API_STATUS_ICON_PATH, VALID_API_STATUS_ICON_PATH, INVALID_API_STATUS_ICON_PATH
from network_utils import (is_connected_internet, is_api_up, is_imdb_api_up, is_tweepy_up,
                           is_detectlanguage_api_up, is_googletrans_api_up)
from requests_handler import RequestsHandler


def update_api_status_icons(ui, rh: RequestsHandler):
    '''Function that verifies if the various API services are available or not and updates the icon in the
    API status panel of the Dashboard
    '''
    if is_connected_internet():  #  if we are connected to the internet, we can check the status

        # while being checked, a warning icon will be displayed
        ui.api_status_image_googletrans_label.setPixmap(QPixmap(WARNING_API_STATUS_ICON_PATH))
        ui.api_status_image_detectlanguage_label.setPixmap(QPixmap(WARNING_API_STATUS_ICON_PATH))
        ui.api_status_image_twitter_label.setPixmap(QPixmap(WARNING_API_STATUS_ICON_PATH))
        ui.api_status_image_imdb_label.setPixmap(QPixmap(WARNING_API_STATUS_ICON_PATH))

        # gooletrans
        if is_api_up(is_googletrans_api_up, "gooletrans"):
            ui.api_status_image_googletrans_label.setPixmap(QPixmap(VALID_API_STATUS_ICON_PATH))
        else:
            ui.api_status_image_googletrans_label.setPixmap(QPixmap(INVALID_API_STATUS_ICON_PATH))

        # detectlang
        if is_api_up(is_detectlanguage_api_up, "detectlang"):
            ui.api_status_image_detectlanguage_label.setPixmap(QPixmap(VALID_API_STATUS_ICON_PATH))
        else:
            ui.api_status_image_detectlanguage_label.setPixmap(QPixmap(INVALID_API_STATUS_ICON_PATH))

        # tweepy
        if is_api_up(is_tweepy_up, "tweepy"):
            ui.api_status_image_twitter_label.setPixmap(QPixmap(VALID_API_STATUS_ICON_PATH))
        else:
            ui.api_status_image_twitter_label.setPixmap(QPixmap(INVALID_API_STATUS_ICON_PATH))

        # imdb (works a bit differently as we verify if a webdriver could be loaded)
        if (is_imdb_api_up, rh):
            ui.api_status_image_imdb_label.setPixmap(QPixmap(VALID_API_STATUS_ICON_PATH))
        else:
            ui.api_status_image_imdb_label.setPixmap(QPixmap(INVALID_API_STATUS_ICON_PATH))

    else:  # if no internet, every API is set to invalid status
        ui.api_status_image_detectlanguage_label.setPixmap(QPixmap(INVALID_API_STATUS_ICON_PATH))
        ui.api_status_image_googletrans_label.setPixmap(QPixmap(INVALID_API_STATUS_ICON_PATH))
        ui.api_status_image_twitter_label.setPixmap(QPixmap(INVALID_API_STATUS_ICON_PATH))
        ui.api_status_image_imdb_label.setPixmap(QPixmap(INVALID_API_STATUS_ICON_PATH))


def thread_update_api_status(app, ui, rh):
    '''A Worker loads the various classifiers in the RequestsHandler. This procedure is transparent, the user
    can use the interface in parallel. This is basically a thread wrapper for the update_api_status_icons function
    '''
    api_status_thread = Worker(update_api_status_icons, app, ui, rh)  #  set up of the thread using the Worker
    api_status_thread.start()  #  starts the thread, no signals need to be connected
