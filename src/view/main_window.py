'''
Created on Mar 2, 2021

Module that contains the Ui_MainWindow class.
@author: jack, yann
'''
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\main_window.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from os.path import sep

from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QDesktopWidget, QWidget
from translator import SUPPORTED_TARGET_LANGUAGES

IMG_PATH = "view" + sep + "img" + sep
ICON_PATH = IMG_PATH + "L3AA1icon.png"
LENS_PATH = IMG_PATH + "lens.png"
LOADING_PATH = IMG_PATH + "loading_gear.gif"
HOME_PATH = IMG_PATH + "home.png"
WALLPAPER_PATH = IMG_PATH + "wallpaper.png"
DASHBOARD_PATH = IMG_PATH + "dashboard.png"

VALID_API_STATUS_ICON_PATH = IMG_PATH + "status_valid18.png"
INVALID_API_STATUS_ICON_PATH = IMG_PATH + "status_invalid18.png"
WARNING_API_STATUS_ICON_PATH = IMG_PATH + "status_warning18.png"


class Ui_MainWindow(QWidget):

    # >>> Declaring elements for the GUI <<<
    def setupUi(self, MainWindow):
        # Loads images
        logo_icon = QtGui.QIcon()
        logo_icon.addPixmap(QtGui.QPixmap(ICON_PATH), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        lens_icon = QtGui.QIcon()
        lens_icon.addPixmap(QtGui.QPixmap(LENS_PATH), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        home_icon = QtGui.QIcon()
        home_icon.addPixmap(QtGui.QPixmap(HOME_PATH), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        wallpaper_icon = QtGui.QIcon()
        wallpaper_icon.addPixmap(QtGui.QPixmap(WALLPAPER_PATH), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dashboard_icon = QtGui.QIcon()
        dashboard_icon.addPixmap(QtGui.QPixmap(DASHBOARD_PATH), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        # Load animation
        self.loading = QMovie(LOADING_PATH)

        # =Main Window=
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 720)  # I suppose everyone has at least an HD Ready screen.
        MainWindow.setFixedSize(1280, 720)
        MainWindow.setWindowIcon(logo_icon)
        MainWindow.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Set font
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setBold(True)
        font.setUnderline(False)
        font.setWeight(75)
        font.setKerning(True)

        # Set palette and brushes
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)

        brush = QtGui.QBrush(QtGui.QColor(31, 191, 184))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)

        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)

        # =DASHBOARD=
        # >Dashboard Frame
        self.frameDashboard = QtWidgets.QFrame(self.centralwidget)
        self.frameDashboard.setGeometry(QtCore.QRect(0, 0, 300, 720))
        self.frameDashboard.setStyleSheet("background-color: rgb(31, 191, 184);")
        self.frameDashboard.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameDashboard.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameDashboard.setObjectName("frameDashboard")

        # >Label "Wallpaper"
        self.wallpaperdashboard = QtWidgets.QLabel(self.frameDashboard)
        self.wallpaperdashboard.setGeometry(QtCore.QRect(0, 0, 300, 720))
        self.wallpaperdashboard.setText("")
        self.wallpaperdashboard.setPixmap(QtGui.QPixmap(DASHBOARD_PATH))
        self.wallpaperdashboard.setScaledContents(True)
        self.wallpaperdashboard.setObjectName("Wallpaperdashboard")

        # >Home Button
        self.homeButton = QtWidgets.QPushButton(self.frameDashboard)
        self.homeButton.setGeometry(QtCore.QRect(100, 30, 100, 100))
        self.homeButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.homeButton.setText("")
        self.homeButton.setIcon(home_icon)
        self.homeButton.setIconSize(QtCore.QSize(100, 100))
        self.homeButton.setFlat(True)
        self.homeButton.setObjectName("homeButton")

        # >Label "Error Dashboard"
        self.labelErrorDashboard = QtWidgets.QLabel(self.frameDashboard)
        self.labelErrorDashboard.setGeometry(QtCore.QRect(20, 130, 260, 80))
        self.labelErrorDashboard.setWordWrap(True)
        self.labelErrorDashboard.setFont(font)
        self.labelErrorDashboard.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.labelErrorDashboard.setObjectName("labelErrorDashboard")
        self.labelErrorDashboard.setStyleSheet("background-color: rgba(0,0,0,0%)")

        # >Line Edit Dashboard
        self.lineEditDashboard = QtWidgets.QLineEdit(self.frameDashboard)
        self.lineEditDashboard.setGeometry(QtCore.QRect(20, 210, 240, 25))
        self.lineEditDashboard.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.lineEditDashboard.setClearButtonEnabled(True)
        self.lineEditDashboard.setObjectName("lineEditDashboard")

        # >Search Button Dashboard
        self.searchButtonDashboard = QtWidgets.QPushButton(self.frameDashboard)
        self.searchButtonDashboard.setGeometry(QtCore.QRect(260, 210, 25, 25))
        self.searchButtonDashboard.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.searchButtonDashboard.setFont(font)
        self.searchButtonDashboard.setText("")
        self.searchButtonDashboard.setIcon(lens_icon)
        self.searchButtonDashboard.setFlat(True)
        self.searchButtonDashboard.setObjectName("searchButtonDashboard")

        # > Label loading icon dashboard
        self.loading_icon_dashboard = QtWidgets.QLabel(self.frameDashboard)
        self.loading_icon_dashboard.setGeometry(QtCore.QRect(260, 210, 25, 25))
        self.loading_icon_dashboard.setObjectName("loading_icon_dashboard")
        self.loading_icon_dashboard.setScaledContents(True)
        self.loading_icon_dashboard.setStyleSheet("background-color: rgba(0,0,0,0%)")
        self.loading_icon_dashboard.hide()

        # >Label "Platform"
        self.labelPlatform = QtWidgets.QLabel(self.frameDashboard)
        self.labelPlatform.setGeometry(QtCore.QRect(20, 250, 260, 25))
        self.labelPlatform.setObjectName("labelPlatform")
        self.labelPlatform.setStyleSheet("background-color: rgba(0,0,0,0%)")

        # >Radio Button "Twitter"
        self.radioButtonTwitter = QtWidgets.QRadioButton(self.frameDashboard)
        self.radioButtonTwitter.setGeometry(QtCore.QRect(40, 280, 100, 20))
        self.radioButtonTwitter.setPalette(palette)
        self.radioButtonTwitter.setFont(font)
        self.radioButtonTwitter.setChecked(True)
        self.radioButtonTwitter.setObjectName("radioButtonTwitter")

        # >Radio Button "Imdb"
        self.radioButtonIMDB = QtWidgets.QRadioButton(self.frameDashboard)
        self.radioButtonIMDB.setGeometry(QtCore.QRect(40, 310, 100, 20))
        self.radioButtonIMDB.setPalette(palette)
        self.radioButtonIMDB.setFont(font)
        self.radioButtonIMDB.setObjectName("radioButtonIMDB")

        # >Label "Search Language"
        self.labelLanguage = QtWidgets.QLabel(self.frameDashboard)
        self.labelLanguage.setGeometry(QtCore.QRect(20, 350, 260, 25))
        self.labelLanguage.setObjectName("labelLanguage")
        self.labelLanguage.setStyleSheet("background-color: rgba(0,0,0,0%)")

        # >Checkbox "English"
        self.checkBoxEnglish = QtWidgets.QCheckBox(self.frameDashboard)
        self.checkBoxEnglish.setGeometry(QtCore.QRect(40, 380, 100, 20))
        self.checkBoxEnglish.setPalette(palette)
        self.checkBoxEnglish.setFont(font)
        self.checkBoxEnglish.setChecked(True)
        self.checkBoxEnglish.setObjectName("checkBoxEnglish")

        # >Checkbox "French"
        self.checkBoxFrench = QtWidgets.QCheckBox(self.frameDashboard)
        self.checkBoxFrench.setGeometry(QtCore.QRect(40, 410, 100, 20))
        self.checkBoxFrench.setPalette(palette)
        self.checkBoxFrench.setFont(font)
        self.checkBoxFrench.setObjectName("checkBoxFrench")

        # >Label "Target Language"
        self.labelTargetLanguage = QtWidgets.QLabel(self.frameDashboard)
        self.labelTargetLanguage.setGeometry(QtCore.QRect(20, 450, 260, 25))
        self.labelTargetLanguage.setObjectName("labelTargetLanguage")
        self.labelTargetLanguage.setStyleSheet("background-color: rgba(0,0,0,0%)")
        self.labelTargetLanguage.setText("")

        # >Combobox Target Language
        self.comboBoxTargetLanguage = QtWidgets.QComboBox(self.frameDashboard)
        self.comboBoxTargetLanguage.setGeometry(QtCore.QRect(40, 490, 150, 20))
        self.comboBoxTargetLanguage.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.comboBoxTargetLanguage.setObjectName("comboBoxTargetLanguage")
        for _, item in enumerate(SUPPORTED_TARGET_LANGUAGES):
            self.comboBoxTargetLanguage.addItem(SUPPORTED_TARGET_LANGUAGES[item])  # adds entries to the cbox
        self.comboBoxTargetLanguage.setEditable(True)  #  necessary to remove transparency and be able to search the cbox
        self.comboBoxTargetLanguage.setCurrentIndex(-1)
        self.comboBoxTargetLanguage.lineEdit().setPlaceholderText("For translation")
        self.comboBoxTargetLanguage.setStyleSheet("QComboBox{" +
                                                  "combobox-popup:0;" +  # makes the cbox height acceptable
                                                  "background-color: rgb(255, 255, 255);}")

        # >Label "API Status"
        self.labelAPIStatus = QtWidgets.QLabel(self.frameDashboard)
        self.labelAPIStatus.setGeometry(QtCore.QRect(20, 530, 260, 25))
        self.labelAPIStatus.setObjectName("labelAPIStatus")
        self.labelAPIStatus.setStyleSheet("background-color: rgba(0,0,0,0%)")
        self.labelAPIStatus.setText("")

        # =API status labels=

        font_api_status = font
        # font_api_status.setBold(False)

        # Position constants
        Y_GOOGLETRANSLATE_STATUS = 560
        Y_DETECTLANGUAGE_STATUS = Y_GOOGLETRANSLATE_STATUS + 30
        Y_TWITTER_STATUS = Y_DETECTLANGUAGE_STATUS + 30
        Y_IMDB_STATUS = Y_TWITTER_STATUS + 30
        X_STATUS_LABELS = 40

        self.googletrans_api_status_label = QtWidgets.QLabel(self.frameDashboard)
        self.googletrans_api_status_label.setFont(font_api_status)
        self.googletrans_api_status_label.setPalette(palette)
        self.googletrans_api_status_label.setGeometry(QtCore.QRect(X_STATUS_LABELS + 25, Y_GOOGLETRANSLATE_STATUS + 1, 121, 16))
        self.googletrans_api_status_label.setObjectName("googletrans_api_status_label")
        self.googletrans_api_status_label.setAutoFillBackground(True)  # This is important!!
        self.googletrans_api_status_label.setStyleSheet("background-color: rgba(255, 255, 255, 0);")

        self.detectlanguage_api_status_label = QtWidgets.QLabel(self.frameDashboard)
        self.detectlanguage_api_status_label.setFont(font_api_status)
        self.detectlanguage_api_status_label.setPalette(palette)
        self.detectlanguage_api_status_label.setGeometry(QtCore.QRect(X_STATUS_LABELS + 25, Y_DETECTLANGUAGE_STATUS + 1, 111, 16))
        self.detectlanguage_api_status_label.setObjectName("detectlanguage_api_status_label")
        self.detectlanguage_api_status_label.setStyleSheet("background-color: rgba(255, 255, 255, 0);")

        self.twitter_api_status_label = QtWidgets.QLabel(self.frameDashboard)
        self.twitter_api_status_label.setFont(font_api_status)
        self.twitter_api_status_label.setPalette(palette)
        self.twitter_api_status_label.setGeometry(QtCore.QRect(X_STATUS_LABELS + 25, Y_TWITTER_STATUS + 1, 61, 16))
        self.twitter_api_status_label.setObjectName("twitter_api_status_label")
        self.twitter_api_status_label.setStyleSheet("background-color: rgba(255, 255, 255, 0);")

        self.imdb_api_status_label = QtWidgets.QLabel(self.frameDashboard)
        self.imdb_api_status_label.setFont(font_api_status)
        self.imdb_api_status_label.setPalette(palette)
        self.imdb_api_status_label.setGeometry(QtCore.QRect(X_STATUS_LABELS + 25, Y_IMDB_STATUS + 1, 50, 16))
        self.imdb_api_status_label.setObjectName("imdb_api_status_label")
        self.imdb_api_status_label.setStyleSheet("background-color: rgba(255, 255, 255, 0);")

        self.api_status_image_googletrans_label = QtWidgets.QLabel(self.frameDashboard)
        self.api_status_image_googletrans_label.setGeometry(QtCore.QRect(X_STATUS_LABELS, Y_GOOGLETRANSLATE_STATUS, 18, 18))
        self.api_status_image_googletrans_label.setText("")
        self.api_status_image_googletrans_label.setPixmap(QtGui.QPixmap(WARNING_API_STATUS_ICON_PATH))
        self.api_status_image_googletrans_label.setObjectName("valid_api_status_googletrans_label")
        self.api_status_image_googletrans_label.setStyleSheet("background-color: rgba(0,0,0,0%)")

        self.api_status_image_detectlanguage_label = QtWidgets.QLabel(self.frameDashboard)
        self.api_status_image_detectlanguage_label.setGeometry(QtCore.QRect(X_STATUS_LABELS, Y_DETECTLANGUAGE_STATUS, 18, 18))
        self.api_status_image_detectlanguage_label.setText("")
        self.api_status_image_detectlanguage_label.setPixmap(QtGui.QPixmap(WARNING_API_STATUS_ICON_PATH))
        self.api_status_image_detectlanguage_label.setObjectName("api_status_image_detectlanguage_label")
        self.api_status_image_detectlanguage_label.setStyleSheet("background-color: rgba(0,0,0,0%)")

        self.api_status_image_twitter_label = QtWidgets.QLabel(self.frameDashboard)
        self.api_status_image_twitter_label.setGeometry(QtCore.QRect(X_STATUS_LABELS, Y_TWITTER_STATUS, 18, 18))
        self.api_status_image_twitter_label.setText("")
        self.api_status_image_twitter_label.setPixmap(QtGui.QPixmap(WARNING_API_STATUS_ICON_PATH))
        self.api_status_image_twitter_label.setObjectName("api_status_image_twitter_label")
        self.api_status_image_twitter_label.setStyleSheet("background-color: rgba(0,0,0,0%)")

        self.api_status_image_imdb_label = QtWidgets.QLabel(self.frameDashboard)
        self.api_status_image_imdb_label.setGeometry(QtCore.QRect(X_STATUS_LABELS, Y_IMDB_STATUS, 18, 18))
        self.api_status_image_imdb_label.setText("")
        self.api_status_image_imdb_label.setPixmap(QtGui.QPixmap(WARNING_API_STATUS_ICON_PATH))
        self.api_status_image_imdb_label.setObjectName("api_status_image_imdb_label")
        self.api_status_image_imdb_label.setStyleSheet("background-color: rgba(0,0,0,0%)")

        # >About Button
        self.about = QtWidgets.QPushButton(self.frameDashboard)
        self.about.setGeometry(QtCore.QRect(20, 690, 51, 20))
        self.about.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.about.setFont(font)
        self.about.setStyleSheet("color: rgb(255, 255, 255);")
        self.about.setFlat(True)
        self.about.setObjectName("about")

        # =MAIN MENU=
        # >Main Menu Frame
        self.frameMainMenu = QtWidgets.QFrame(self.centralwidget)
        self.frameMainMenu.setGeometry(QtCore.QRect(300, 0, 980, 720))
        self.frameMainMenu.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.frameMainMenu.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameMainMenu.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameMainMenu.setObjectName("frameMainMenu")

        # >Dev_console
        self.mainwindow_console = QtWidgets.QLabel(self.frameMainMenu)
        self.mainwindow_console.setGeometry(QtCore.QRect(0, 0, 980, 20))
        self.mainwindow_console.setObjectName("mainwindow_console")
        self.mainwindow_console.setStyleSheet("background-color: rgba(0,0,0,0%)")

        # >Label "Wallpaper"
        self.wallpaper = QtWidgets.QLabel(self.frameMainMenu)
        self.wallpaper.setGeometry(QtCore.QRect(0, 0, 980, 720))
        self.wallpaper.setText("")
        self.wallpaper.setPixmap(QtGui.QPixmap(WALLPAPER_PATH))
        self.wallpaper.setScaledContents(True)
        self.wallpaper.setObjectName("Wallpaper")

        # >Line Edit "Twitter"
        self.lineEditMainWindowTwitter = QtWidgets.QLineEdit(self.frameMainMenu)
        self.lineEditMainWindowTwitter.setGeometry(QtCore.QRect(205, 470, 260, 25))
        self.lineEditMainWindowTwitter.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.lineEditMainWindowTwitter.setInputMask("")
        self.lineEditMainWindowTwitter.setClearButtonEnabled(True)
        self.lineEditMainWindowTwitter.setObjectName("lineEditMainWindowTwitter")

        # >Search Button Main Menu "Twitter"
        self.searchButtonMainWindowTwitter = QtWidgets.QPushButton(self.frameMainMenu)
        self.searchButtonMainWindowTwitter.setGeometry(QtCore.QRect(465, 470, 25, 25))
        self.searchButtonMainWindowTwitter.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.searchButtonMainWindowTwitter.setFont(font)
        self.searchButtonMainWindowTwitter.setText("")
        self.searchButtonMainWindowTwitter.setIcon(lens_icon)
        self.searchButtonMainWindowTwitter.setFlat(True)
        self.searchButtonMainWindowTwitter.setObjectName("searchButtonMainWindowTwitter")

        # > Label loading icon "Twitter"
        self.loading_icon_twitter = QtWidgets.QLabel(self.frameMainMenu)
        self.loading_icon_twitter.setGeometry(QtCore.QRect(465, 470, 25, 25))
        self.loading_icon_twitter.setObjectName("loading_icon_twitter")
        self.loading_icon_twitter.setScaledContents(True)
        self.loading_icon_twitter.setStyleSheet("background-color: rgba(0,0,0,0%)")
        self.loading_icon_twitter.hide()

        # >Line Edit "IMDB"
        self.lineEditMainWindowIMDB = QtWidgets.QLineEdit(self.frameMainMenu)
        self.lineEditMainWindowIMDB.setGeometry(QtCore.QRect(490, 470, 260, 25))
        self.lineEditMainWindowIMDB.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.lineEditMainWindowIMDB.setInputMask("")
        self.lineEditMainWindowIMDB.setClearButtonEnabled(True)
        self.lineEditMainWindowIMDB.setObjectName("lineEditMainWindowIMDB")

        # >Search Button Main Menu "IMDB"
        self.searchButtonMainWindowIMDB = QtWidgets.QPushButton(self.frameMainMenu)
        self.searchButtonMainWindowIMDB.setGeometry(QtCore.QRect(750, 470, 25, 25))
        self.searchButtonMainWindowIMDB.setFont(font)
        self.searchButtonMainWindowIMDB.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.searchButtonMainWindowIMDB.setText("")
        self.searchButtonMainWindowIMDB.setIcon(lens_icon)
        self.searchButtonMainWindowIMDB.setFlat(True)
        self.searchButtonMainWindowIMDB.setObjectName("searchButtonMainWindowIMDB")

        # > Label loading icon "IMDB"
        self.loading_icon_IMDB = QtWidgets.QLabel(self.frameMainMenu)
        self.loading_icon_IMDB.setGeometry(QtCore.QRect(750, 470, 25, 25))
        self.loading_icon_IMDB.setObjectName("loading_icon_IMDB")
        self.loading_icon_IMDB.setScaledContents(True)
        self.loading_icon_IMDB.setStyleSheet("background-color: rgba(0,0,0,0%)")
        self.loading_icon_IMDB.hide()

        # >Button "Import"
        self.importButton = QtWidgets.QPushButton(self.frameMainMenu)
        self.importButton.setGeometry(QtCore.QRect(440, 520, 100, 40))
        self.importButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.importButton.setFont(font)
        self.importButton.setStyleSheet("background-color: rgb(212, 212, 212);")
        self.importButton.setObjectName("importButton")

        # >Line Edit "Local"
        self.lineEditMainWindowLocal = QtWidgets.QLineEdit(self.frameMainMenu)
        self.lineEditMainWindowLocal.setGeometry(QtCore.QRect(347.5, 580, 260, 25))
        self.lineEditMainWindowLocal.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.lineEditMainWindowLocal.setInputMask("")
        self.lineEditMainWindowLocal.setClearButtonEnabled(True)
        self.lineEditMainWindowLocal.setObjectName("lineEditMainWindowLocal")

        # >Search Button Main Menu "Local"
        self.searchButtonMainWindowLocal = QtWidgets.QPushButton(self.frameMainMenu)
        self.searchButtonMainWindowLocal.setGeometry(QtCore.QRect(607.5, 580, 25, 25))
        self.searchButtonMainWindowLocal.setFont(font)
        self.searchButtonMainWindowLocal.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.searchButtonMainWindowLocal.setText("")
        self.searchButtonMainWindowLocal.setIcon(lens_icon)
        self.searchButtonMainWindowLocal.setFlat(True)
        self.searchButtonMainWindowLocal.setObjectName("searchButtonMainWindowLocal")

        # > Label loading icon "IMDB"
        self.loading_icon_local = QtWidgets.QLabel(self.frameMainMenu)
        self.loading_icon_local.setGeometry(QtCore.QRect(607.5, 580, 25, 25))
        self.loading_icon_local.setObjectName("loading_icon_local")
        self.loading_icon_local.setScaledContents(True)
        self.loading_icon_local.setStyleSheet("background-color: rgba(0,0,0,0%)")
        self.loading_icon_local.hide()

        # >Label "Error MainMenu"
        self.labelErrorMainmenu = QtWidgets.QLabel(self.frameMainMenu)
        self.labelErrorMainmenu.setGeometry(QtCore.QRect(297.5, 610, 385, 80))
        self.labelErrorMainmenu.setWordWrap(True)
        self.labelErrorMainmenu.setFont(font)
        self.labelErrorMainmenu.setObjectName("labelErrorMainmenu")
        self.labelErrorMainmenu.setStyleSheet("background-color: rgba(0,0,0,0%)")

        # =Tab Results=

        # >Tab Result Frame
        self.frameTabResult = QtWidgets.QFrame(self.centralwidget)
        self.frameTabResult.setGeometry(QtCore.QRect(300, 0, 980, 720))
        self.frameTabResult.setStyleSheet("background-color: rgb(240, 240, 240);")
        self.frameTabResult.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameTabResult.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameTabResult.setObjectName("frameTabResult")

        # >Tab area Results
        self.tabResults = QtWidgets.QTabWidget(self.frameTabResult)
        self.tabResults.setGeometry(QtCore.QRect(0, 0, 980, 720))
        self.tabResults.setObjectName("tabResults")

        # >>Begining of tab for analytics
        self.tabAnalytics = QtWidgets.QWidget()
        self.tabAnalytics.setObjectName("tabAnalytics")

        # >>>Scroll area
        self.scrollArea = QtWidgets.QScrollArea(self.tabAnalytics)
        self.scrollArea.setGeometry(QtCore.QRect(0, 0, 974, 691))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 972, 689))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        # >>>>Analytics
        self.Analytics = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.Analytics.setGeometry(QtCore.QRect(0, 0, 972, 689))
        self.Analytics.setObjectName("Analytics")

        # >>>End of scroll area
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        # >>End of tab for analytics
        self.tabResults.addTab(self.tabAnalytics, "")

        # >>Begining of tab for charts
        self.tabCharts = QtWidgets.QWidget()
        self.tabCharts.setObjectName("tabCharts")

        # >>>Table view for displaying dataframe
        self.tableView = QtWidgets.QTableView(self.tabCharts)
        self.tableView.setGeometry(QtCore.QRect(5, 11, 961, 621))
        self.tableView.setObjectName("tableView")
        self.tableView.setMouseTracking(True)

        # >>>Export button
        self.exportButton = QtWidgets.QPushButton(self.tabCharts)
        self.exportButton.setGeometry(QtCore.QRect(850, 640, 93, 28))
        self.exportButton.setObjectName("exportButton")

        # >>End of tab for charts
        self.tabResults.addTab(self.tabCharts, "")

        # =DISPLAY ORDER=
        # >Main Menu
        self.wallpaper.raise_()
        self.mainwindow_console.raise_()
        self.lineEditMainWindowTwitter.raise_()
        self.searchButtonMainWindowTwitter.raise_()
        self.lineEditMainWindowIMDB.raise_()
        self.searchButtonMainWindowIMDB.raise_()
        self.importButton.raise_()
        self.lineEditMainWindowLocal.raise_()
        self.searchButtonMainWindowLocal.raise_()
        self.labelErrorMainmenu.raise_()

        # >Dashboard
        self.wallpaperdashboard.raise_()
        self.homeButton.raise_()
        self.labelErrorDashboard.raise_()

        self.lineEditDashboard.raise_()
        self.searchButtonDashboard.raise_()

        self.labelPlatform.raise_()
        self.radioButtonTwitter.raise_()
        self.radioButtonIMDB.raise_()

        self.labelLanguage.raise_()
        self.checkBoxEnglish.raise_()
        self.checkBoxFrench.raise_()

        self.labelTargetLanguage.raise_()
        self.comboBoxTargetLanguage.raise_()

        self.labelAPIStatus.raise_()

        self.api_status_image_googletrans_label.raise_()
        self.googletrans_api_status_label.raise_()

        self.api_status_image_detectlanguage_label.raise_()
        self.detectlanguage_api_status_label.raise_()

        self.api_status_image_twitter_label.raise_()
        self.twitter_api_status_label.raise_()

        self.api_status_image_imdb_label.raise_()
        self.imdb_api_status_label.raise_()

        self.about.raise_()

        # =Hiding Stuff=
        self.lineEditMainWindowLocal.hide()  # Hiding local search line edit
        self.searchButtonMainWindowLocal.hide()  # And its button
        self.labelErrorDashboard.hide()  # Hiding error labels
        self.labelErrorMainmenu.hide()
        self.frameTabResult.hide()  # Hiding the tabs for results

        # =Tab button Order=
        MainWindow.setTabOrder(self.homeButton, self.lineEditDashboard)
        MainWindow.setTabOrder(self.lineEditDashboard, self.searchButtonDashboard)
        MainWindow.setTabOrder(self.searchButtonDashboard, self.radioButtonTwitter)
        MainWindow.setTabOrder(self.radioButtonTwitter, self.radioButtonIMDB)
        MainWindow.setTabOrder(self.radioButtonIMDB, self.checkBoxEnglish)
        MainWindow.setTabOrder(self.checkBoxEnglish, self.checkBoxFrench)
        MainWindow.setTabOrder(self.checkBoxFrench, self.comboBoxTargetLanguage)
        MainWindow.setTabOrder(self.comboBoxTargetLanguage, self.lineEditMainWindowTwitter)
        MainWindow.setTabOrder(self.lineEditMainWindowTwitter, self.searchButtonMainWindowTwitter)
        MainWindow.setTabOrder(self.searchButtonMainWindowTwitter, self.lineEditMainWindowIMDB)
        MainWindow.setTabOrder(self.lineEditMainWindowIMDB, self.searchButtonMainWindowIMDB)
        MainWindow.setTabOrder(self.searchButtonMainWindowIMDB, self.importButton)
        MainWindow.setTabOrder(self.importButton, self.about)
        MainWindow.setTabOrder(self.about, self.homeButton)

        # =Miscs=
        MainWindow.setCentralWidget(self.centralwidget)

        # self.center()  # FIXME: I don't work correctly

        # Automatic translation
        self.retranslateUi(MainWindow)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "L3AA1: Multilingual text data categorization for opinion detection"))
        self.lineEditDashboard.setPlaceholderText(_translate("MainWindow", "Search"))
        self.labelPlatform.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:11pt; font-weight:600; color:#ffffff;\">Platform</span></p></body></html>"))
        self.radioButtonTwitter.setText(_translate("MainWindow", "Twitter"))
        self.radioButtonIMDB.setText(_translate("MainWindow", "IMDb"))
        self.labelLanguage.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:11pt; font-weight:600; color:#ffffff;\">Source language</span></p></body></html>"))
        self.checkBoxEnglish.setText(_translate("MainWindow", "English"))
        self.checkBoxFrench.setText(_translate("MainWindow", "French"))
        self.labelAPIStatus.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:11pt; font-weight:600; color:#ffffff;\">API status</span></p></body></html>"))
        self.about.setText(_translate("MainWindow", "About"))
        self.lineEditMainWindowTwitter.setPlaceholderText(_translate("MainWindow", "Twitter"))
        self.lineEditMainWindowIMDB.setPlaceholderText(_translate("MainWindow", "IMDb"))
        self.lineEditMainWindowLocal.setPlaceholderText(_translate("MainWindow", "Local"))
        self.importButton.setText(_translate("MainWindow", "Import CSV"))
        self.mainwindow_console.setText(_translate("MainWindow", ""))
        self.labelTargetLanguage.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:11pt; font-weight:600; color:#ffffff;\">Target language</span></p></body></html>"))
        self.googletrans_api_status_label.setText("Google Translate")
        self.detectlanguage_api_status_label.setText("detectlanguage")
        self.twitter_api_status_label.setText("Twitter")
        self.imdb_api_status_label.setText("IMDb")

        for idx, item in enumerate(SUPPORTED_TARGET_LANGUAGES):
            self.comboBoxTargetLanguage.setItemText(idx, _translate("MainWindow", SUPPORTED_TARGET_LANGUAGES[item]))

        # self.labelErrorDashboard.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" color:#dc0000;\">Error Dashboard</span></p></body></html>"))
        # self.labelErrorMainmenu.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" color:#dc0000;\">Error Main Menu</span></p></body></html>"))

        self.tabResults.setTabText(self.tabResults.indexOf(self.tabAnalytics), _translate("MainWindow", "Analytics"))
        self.exportButton.setText(_translate("MainWindow", "Save"))
        self.tabResults.setTabText(self.tabResults.indexOf(self.tabCharts), _translate("MainWindow", "Charts"))

    def __init__(self, app):
        super().__init__()
        self.app = app

        # >>> Declaring variables <<<
        self.user_entry = ""  # Entry from user for his search
        self.search_engine = "Twitter"  # Search engine selected by user
        self.english = True  # If the use want his search to be on English tweets
        self.french = False  # If the use want his search to be on French tweets
        self.csv_path = ""  # Location in the HDD of .csv file to load
        self.file_loaded = False  # If a .csv file is loaded
        self.displayed_message_location = "dashboard"  # Location of where to display messages/errors
        self.target_language = ""  # Language targeted for translation
        self.pos_click = ""  # Location of the user's click

    def get_french(self):
        '''
        Return variable value for french
        '''
        return self.french

    def get_english(self):
        '''
        Return variable value for english
        '''
        return self.english

    def get_user_entry(self):
        '''
        Return variable value for user_entry
        '''
        return self.user_entry

    def get_search_engine(self):
        '''
        Return variable value for search_engine
        '''
        return self.search_engine

    def get_csv_path(self):
        '''
        Return variable value for csv_path
        '''
        return self.csv_path

    def get_file_loaded(self):
        '''
        Return variable value for file_loaded
        '''
        return self.file_loaded

    def get_message_location(self):
        '''
        Return variable value for displayed_message_location
        '''
        return self.displayed_message_location

    def get_target_language(self):
        '''
        Return variable value for target_language
        '''
        return self.target_language

    def get_pos_click(self):
        '''
        Return last known position of user's click
        '''
        return self.pos_click

    def center(self):
        # geometry of the main window
        qr = self.frameGeometry()
        # print(qr)
        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()
        # print(cp)
        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)
        # top left of rectangle becomes top left of window centering it
        self.move(800, 800)
