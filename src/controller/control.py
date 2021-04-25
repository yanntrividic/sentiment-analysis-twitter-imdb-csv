'''
Created on Mar 9, 2021

Module that contains the Controller class, where most of the interactions between the user and the app are processed.
@author: yann, jack
'''

from PyQt5 import QtWidgets
import os
import sys
import traceback

from PyQt5.QtWidgets import QFileDialog
from api_status import thread_update_api_status
from background_work import Worker
from credits import Ui_Dialog
from file_writer import write_csv_to_df
from graph_handler import graph_convert, WORDCLOUD_PNG_PATH
from main_window import Ui_MainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from network_utils import is_connected_internet, load_driver
from requests_handler import RequestsHandler, RequestSyntaxError
from show_messages import show_message, show_on_mainwindow_console, update_mainwindow_console
from table_model import TableModel, setColumnWidth, setRowHeight
from translator import is_valid_target_lang


class Controller:
    '''Controls the various flows of data going from the interface to the model and vice versa
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_window = QtWidgets.QMainWindow()
        # Initialization of the window
        self.ui = Ui_MainWindow(self.app)
        self.ui.setupUi(self.main_window)
        self.ui_dialog = None
        self._connect_signals()
        self.main_window.show()  # we show the window

        self.req_thread = None
        self.rh = RequestsHandler()
        self.__thread_load_models()
        self.__thread_load_imdb_webdriver()

        self.canvas = None  # declaration of the canvas to prevent homebuttonclick from crashing
        self.delete_wordcloud_img()

        thread_update_api_status(self.app, self.ui, self.rh)

        # FIXME: when several models have to be loaded, it cannot be done in parallel otherwise the RAM explodes.
        # 1) verify if the folder and the files exist
        # 2) if more than N classifiers have to be trained, forget about parallelism (and train them once all the
        # others have been loaded?)

    def _connect_signals(self):
        '''Here we connect the stuff we want from the UI to trigger _send_request
        (and the other stuff we would want to control from here)
        '''

        # ==Interactive features==

        # =Line Edit=
        # Whenever "Enter" is pressed, it will click the corresponding button
        self.ui.lineEditDashboard.returnPressed.connect(self.ui.searchButtonDashboard.click)
        self.ui.lineEditMainWindowIMDB.returnPressed.connect(self.ui.searchButtonMainWindowIMDB.click)
        self.ui.lineEditMainWindowTwitter.returnPressed.connect(self.ui.searchButtonMainWindowTwitter.click)
        self.ui.lineEditMainWindowLocal.returnPressed.connect(self.ui.searchButtonMainWindowLocal.click)

        # =Search buttons=
        # Whenenever those button are clicked, it will register user's entry
        self.ui.searchButtonDashboard.clicked.connect(self.lineEditDashboard_click)
        self.ui.searchButtonMainWindowIMDB.clicked.connect(self.lineEditMainWindowIMDB_click)
        self.ui.searchButtonMainWindowTwitter.clicked.connect(self.lineEditMainWindowTwitter_click)
        self.ui.searchButtonMainWindowLocal.clicked.connect(self.lineEditMainWindowLocal_click)

        # =Home button=
        # Whenever clicked, will close the results tabs and clear the line entries
        self.ui.homeButton.clicked.connect(self.homeButton_click)

        # =Import button=
        # Whenever clicked, will open file explorer and show the search bar for local
        self.ui.importButton.clicked.connect(self.importButton_click)

        # =Import button=
        # Whenever clicked, will open file explorer and show the search bar for local
        self.ui.exportButton.clicked.connect(self.exportButton_click)

        # =About button=
        # Whenever clicked, a credits dialog will show up
        self.ui.about.clicked.connect(self.show_credits)

        # =Radio buttons=
        # It should switch between search engines
        self.ui.radioButtonIMDB.clicked.connect(self.radioButtonIMDB_click)
        self.ui.radioButtonTwitter.clicked.connect(self.radioButtonTwitter_click)

        # =Check Boxes=
        # It should switch between search engines
        self.ui.checkBoxEnglish.clicked.connect(self.checkBoxEnglish_click)
        self.ui.checkBoxFrench.clicked.connect(self.checkBoxFrench_click)

        # =ComboBox=
        self.ui.comboBoxTargetLanguage.currentTextChanged.connect(self.checkComboBox_change)

        #  =TableView=
        # self.ui.tableView.itemEntered.connect(handleItemEnteredTableView)
        # self.ui.tableView.itemExited.connect(handleItemExitedTableView)

    # == EVERYTHING ABOUT REQUESTS HANDLING ==

    def __thread_load_models(self):
        '''A Worker loads the various classifiers in the RequestsHandler. This procedure is transparent, the user
        can use the interface in parallel.
        '''
        self.loader_thread = Worker(self.rh.load_classifiers, self.app)  #  new worker instanciated
        self.loader_thread.signals.result.connect(self.show_finished_model_loading)  #  and send the results to the display_results method
        self.loader_thread.start()

    def show_finished_model_loading(self):
        '''One the models have been loaded, we display a message to the user
        '''
        self.ui.displayed_message_location = "dashboard"  #  will be displayed in the dashboard

        internet_connexion = is_connected_internet()
        no_co_message = " but you are not connected to Internet"  #  in the case there is no internet connection

        show_message(self.ui, "All the models were successfully loaded" +
                     (no_co_message if not internet_connexion else "") + "!", error=not internet_connexion)

        print(self.rh)  # debugging

    def __thread_load_imdb_webdriver(self):
        '''A Worker loads the various classifiers in the RequestsHandler. This procedure is transparent, the user
        can use the interface in parallel.
        '''
        self.webdriver_thread = Worker(load_driver, self.app)
        self.webdriver_thread.signals.result.connect(self.assign_webdriver)  #  and send the results to the display_results method
        self.webdriver_thread.signals.error.connect(self.error_webdriver_loading)
        self.webdriver_thread.signals.error.connect(self.finished_webdriver_loading)
        self.webdriver_thread.start()

    def assign_webdriver(self, result):
        '''Value assigned to the webdriver after loading
        '''
        self.rh.imdb_webdriver = result

    def finished_webdriver_loading(self):
        '''Debugging
        '''
        print("Webdriver loading finished")

    def error_webdriver_loading(self, tuple):
        ''' In the case an error is raised by the webdriver's loading a message is displayed
        '''
        _, value, _ = tuple
        if isinstance(value, ValueError):
            self.ui.lineEditMainWindowIMDB.setPlaceholderText(str(value))

    def request_builder(self):
        '''
        Function converting UI's variable to a long String
        '''
        request = ""
        request += "src:" + self.ui.get_search_engine() + " "  # We add to the request the search engine desired

        if self.ui.get_english():  # If English is checked
            request += "lang:en "
        if self.ui.get_french():  # If French is checked
            request += "lang:fr "

        if len(self.ui.comboBoxTargetLanguage.currentText()) > 0:
            lang = is_valid_target_lang(self.ui.comboBoxTargetLanguage.currentText())  #  gets the iso norm for the concerned language
            if lang:
                request += "target:" + lang + " "
            else:
                show_message(self.ui, "One of the specified target languages is not" +
                             " supported and won't be used for translation.", error=True)

        request += self.ui.get_user_entry()  # We add to the search the actual user entry
        return request

    def _send_request(self):
        '''This method is connected to the various search bars/buttons. When such a widget is used,
        a request is built from the various user entries and passed to the RequestsHandler in a loader_thread.

        The processed data is sent to the display_results method
        '''
        self.delete_wordcloud_img()
        self.ui.Analytics.removeWidget(self.canvas)  #  removes the current canvas to make room for the upcoming one
        self.ui.labelErrorDashboard.hide()
        self.ui.labelErrorMainmenu.hide()

        #  Here, we must get the data from the UI to the rh
        req = self.request_builder()  # we register in "req" the data from the interface
        show_on_mainwindow_console(self.ui, req)

        if self.rh:  # if the rh was correctly instanciated
            if self.req_thread is None:  # in the case no request is being processing in the background
                self.req_thread = Worker(self.rh.handle_request, self.app, req)  # we start a new loader_thread to handle the request
                self.loading_on()

                # we connect the signals
                self.req_thread.signals.result.connect(self.display_results)  #  and send the results to the display_results method
                self.req_thread.signals.error.connect(self.show_req_error)
                self.req_thread.signals.finished.connect(self.__reset_req_thread)  # and we reset the worker to make it available

                self.req_thread.start()
            else:
                show_message(self.ui, "Requests can only be submitted at once.", error=True)
        else:
            show_message(self.ui, "The RequestsHandler has not been loaded yet.", error=True)

    def show_req_error(self, tuple):
        '''Wrapper method to receive the signal sent by the Worker and preprocess it for the show_message method
        '''
        _, value, _ = tuple
        if isinstance(value, RequestSyntaxError):
            show_message(self.ui, str(value), error=True)  # displays the error

    def __reset_req_thread(self, check_api_status=True):
        '''Resets the request thread, for example when the user wants to cancel its request or when a error is raised
        '''
        self.req_thread = None
        self.loading_off()  #  removes the GIF to put back the lens
        if check_api_status:
            thread_update_api_status(self.app, self.ui, self.rh)

    def display_results(self, data):
        self.ro = data[0]  # instanciate a new attribute, the RequestOutput

        try:
            self.figure = graph_convert(self.ro)
            self.canvas = FigureCanvas(self.figure)
            self.ui.Analytics.addWidget(self.canvas)

            # sets the tabs to the analytics' tab
            self.ui.tabResults.setCurrentWidget(self.ui.tabResults.findChild(QtWidgets.QWidget, "tabAnalytics"))

        except IndexError:
            traceback.print_exc()
            self.ui.displayed_message_location = "dashboard"
            show_message(self.ui, "Not enough data could be extracted to produce any visualization.", error=True)

        except Exception:  #  if an error occurs while we generate the graph, we adopt a clean behavior
            traceback.print_exc()
            self.ui.displayed_message_location = "dashboard"
            show_message(self.ui, "An unexpected error occurred while we tried to plot your graphics.", error=True)
            self.ui.tabResults.setCurrentWidget(self.ui.tabResults.findChild(QtWidgets.QWidget, "tabCharts"))

        #  instantiation of a new TableModel with the extracted data, it will be the data of the table in Charts
        model = TableModel(self.ro)
        self.ui.tableView.setModel(model)  #  and the model is set to the QTableView object
        setColumnWidth(self.ui.tableView, self.ro)  #  the width of the columns is fit to the QTableView object width
        setRowHeight(self.ui.tableView, self.ro)  #  resets the row height
        # FIXME: reset the position of the scrollbar

        self.ui.frameTabResult.show()  #  we display the two tabs

    def delete_wordcloud_img(self):
        if os.path.exists(WORDCLOUD_PNG_PATH):
            os.remove(WORDCLOUD_PNG_PATH)
    # == EVERYTHING ABOUT BUTTONS AND USER ENTRIES

    def homeButton_click(self):
        '''
        Function for the home button in the dashboard
        '''
        self.loading_off()  # not sure why yet, but this line is needed otherwise the program crashes

        self.ui.lineEditDashboard.clear()
        self.ui.lineEditMainWindowTwitter.clear()
        self.ui.lineEditMainWindowIMDB.clear()
        self.ui.lineEditMainWindowLocal.clear()

        self.ui.labelErrorDashboard.hide()
        self.ui.labelErrorMainmenu.hide()

        self.ui.frameTabResult.hide()
        self.delete_wordcloud_img()
        self.ui.comboBoxTargetLanguage.setCurrentIndex(-1)
        self.ui.user_entry = ""

        thread_update_api_status(self.app, self.ui, self.rh)

        # we force the request thread to exit
        if self.req_thread is not None:
            if self.req_thread.isRunning():
                print("req_thread terminated by force.")
                self.req_thread.terminate()  # properly ends the thread
            self.__reset_req_thread(check_api_status=False)

        show_on_mainwindow_console(self.ui, "Environment cleared")

        # TODO: clean the Graphics window, otherwise graphs appear on each other

    def importButton_click(self):  # Bouton import en cours de dev
        '''
        Function for the import button in the main window
        '''
        title = "CSV file import"  # title of the window
        filter = "CSV files (*.csv)"  #  valid syntax to only display CSV files

        # Sometimes, on Ubuntu, the following warning is met at this point:
        # Gtk-Message: 17:32:27.820: GtkDialog mapped without a transient parent. This is discouraged.
        # Apparently, this warning can't be hidden but is harmless, so no worries...
        csv_path = QFileDialog.getOpenFileName(caption=title, filter=filter)  # displays dialog
        self.ui.displayed_message_location = "mainmenu"

        if csv_path[0]:  #  if the return path is not None
            try:
                self.rh.import_local_data(csv_path[0])
                print("Imported file: " + csv_path[0])
                self.ui.lineEditMainWindowLocal.show()
                # Display of the name of the loaded file in the placeholder
                self.ui.lineEditMainWindowLocal.setPlaceholderText("Search " + csv_path[0].split("/")[-1])
                self.ui.lineEditMainWindowLocal.clear()
                self.ui.searchButtonMainWindowLocal.show()
                self.ui.labelErrorMainmenu.hide()
            except FileNotFoundError as fnfe:
                show_message(self.ui, str(fnfe))
            except Exception:
                traceback.print_exc()
                show_message(self.ui, "Your file could not be read. Please consult our User Manual for more information.", error=True)

    def exportButton_click(self):
        '''
        Function for the export button in the charts tab
        '''
        title = "CSV file export"  # title of the window
        filter = "CSV files (*.csv)"  #  valid syntax to only display CSV files

        # Same warning as importButton_click

        csv_path = QFileDialog.getSaveFileName(caption=title, filter=filter)  # displays dialog
        self.ui.displayed_message_location = "mainmenu"

        csv_path = csv_path[0]

        if csv_path.split(".")[-1].lower() != "csv" and csv_path:  #  we had the extension if it isn't here
            csv_path += ".csv"

        if csv_path:  # in the case the user has entered something
            self.ui.displayed_message_location = "dashboard"
            try:
                write_csv_to_df(self.ro.raw_data, csv_path)
                show_message(self.ui, csv_path.split("/")[-1] + " was successfully saved.")
            except Exception:
                show_message(self.ui, "There has been an error while trying to save " +
                             csv_path.split("/")[-1] + ".", error=True)

    def lineEditDashboard_click(self):
        '''
        Function for the user entry in the dashboard
        '''
        self.ui.user_entry = self.ui.lineEditDashboard.text()
        self.ui.Analytics.removeWidget(self.canvas)
        self.ui.pos_click = "dashboard"  #  for the loading gif

        if self.ui.radioButtonTwitter.isChecked():
            self.ui.search_engine = "Twitter"
        else:
            self.ui.search_engine = "IMDb"

        self.ui.displayed_message_location = "dashboard"
        update_mainwindow_console(self.ui)
        self._send_request()

    def lineEditMainWindowTwitter_click(self):
        '''
        Function for the Twitter user entry in the homepage
        '''
        self.ui.user_entry = self.ui.lineEditMainWindowTwitter.text()
        self.ui.pos_click = "Twitter"
        self.ui.search_engine = "Twitter"
        self.ui.displayed_message_location = "mainmenu"
        update_mainwindow_console(self.ui)
        self._send_request()

    def lineEditMainWindowIMDB_click(self):
        '''
        Function for the IMDb user entry in the homepage
        '''
        self.ui.user_entry = self.ui.lineEditMainWindowIMDB.text()
        self.ui.pos_click = "IMDb"
        self.ui.search_engine = "IMDb"
        self.ui.displayed_message_location = "mainmenu"
        update_mainwindow_console(self.ui)
        self._send_request()

    def lineEditMainWindowLocal_click(self):
        '''
        Function for the local user entry in the homepage
        '''
        self.ui.user_entry = self.ui.lineEditMainWindowLocal.text()
        self.ui.pos_click = "Local"
        self.ui.search_engine = "Local"
        self.ui.displayed_message_location = "mainmenu"
        update_mainwindow_console(self.ui)
        self._send_request()

    def radioButtonIMDB_click(self):
        '''
        Function for the IMDb radio button in the dashboard
        '''
        self.ui.search_engine = "IMDb"
        update_mainwindow_console(self.ui)

    def radioButtonTwitter_click(self):
        '''
        Function for the Twitter radio button in the dashboard
        '''
        self.ui.search_engine = "Twitter"
        update_mainwindow_console(self.ui)

    def checkBoxEnglish_click(self):
        '''
        Function for the English checkbox in the dashboard
        '''
        self.ui.english = self.ui.checkBoxEnglish.isChecked()
        self.check_checkbox()
        update_mainwindow_console(self.ui)

    def checkBoxFrench_click(self):
        '''
        Function for the French checkbox in the dashboard
        '''
        self.ui.french = self.ui.checkBoxFrench.isChecked()
        self.check_checkbox()
        update_mainwindow_console(self.ui)

    def check_checkbox(self):
        '''
        Function for display an error if no languages are checked
        '''
        if not self.ui.get_english() and not self.ui.get_french():
            self.ui.displayed_message_location = "dashboard"
            show_message(self.ui, "If no language is selected, the default language will be english.", error=True)
        elif self.ui.get_english() or self.ui.get_french():
            self.ui.labelErrorDashboard.hide()

    def checkComboBox_change(self):
        update_mainwindow_console(self.ui)

    def show_credits(self):
        '''
        Function for opening the credits dialog, this dialog can be opened only if it is not already opened
        '''
        if self.ui_dialog is None:  # None means no window is opened atm
            self.dialog = QtWidgets.QDialog()
            self.ui_dialog = Ui_Dialog()
            self.ui_dialog.setupUi(self.dialog)

            # the two events are connected to the clean exit of the window
            self.ui_dialog.pushButton.clicked.connect(self.__exit_credits)
            self.dialog.finished.connect(self.__exit_credits)

            self.dialog.show()
            self.dialog.exec_()

    def __exit_credits(self):
        self.dialog.close()
        self.ui_dialog = None

    def loading_on(self):
        '''
        Function for replacing lens icon with animated gif
        '''
        self.loading_off()
        if self.ui.get_pos_click() == "dashboard":
            self.ui.searchButtonDashboard.hide()
            self.ui.loading_icon_dashboard.raise_()
            self.ui.loading_icon_dashboard.show()
            self.ui.loading_icon_dashboard.setMovie(self.ui.loading)
        elif self.ui.get_pos_click() == "Twitter":
            self.ui.searchButtonMainWindowTwitter.hide()
            self.ui.loading_icon_twitter.raise_()
            self.ui.loading_icon_twitter.show()
            self.ui.loading_icon_twitter.setMovie(self.ui.loading)
        elif self.ui.get_pos_click() == "IMDb":
            self.ui.searchButtonMainWindowIMDB.hide()
            self.ui.loading_icon_IMDB.raise_()
            self.ui.loading_icon_IMDB.show()
            self.ui.loading_icon_IMDB.setMovie(self.ui.loading)
        elif self.ui.get_pos_click() == "Local":
            self.ui.searchButtonMainWindowLocal.hide()
            self.ui.loading_icon_local.raise_()
            self.ui.loading_icon_local.show()
            self.ui.loading_icon_local.setMovie(self.ui.loading)
        self.ui.loading.start()

    def loading_off(self):
        '''
        Function for stoping loading animation
        '''
        self.ui.loading.stop()
        self.ui.loading_icon_dashboard.hide()
        self.ui.loading_icon_twitter.hide()
        self.ui.loading_icon_IMDB.hide()
        self.ui.loading_icon_local.hide()
        self.ui.searchButtonDashboard.show()
        self.ui.searchButtonMainWindowTwitter.show()
        self.ui.searchButtonMainWindowIMDB.show()
        if self.rh.local_data:
            self.ui.searchButtonMainWindowLocal.show()
