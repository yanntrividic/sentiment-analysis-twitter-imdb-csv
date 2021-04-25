'''
Created on Mar 2, 2021

Module that contains the Ui_Dialog class.
@author: jack
'''
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\credits.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from main_window import IMG_PATH, ICON_PATH

LOGO_PATH = IMG_PATH + "L3AA1.png"
UNIV_PATH = IMG_PATH + "univ.png"
CREDITS_PATH = IMG_PATH + "credits.png"


class Ui_Dialog(object):

    def setupUi(self, dialog):
        # ==Automatic code from QT Designer==

        # =dialog=
        dialog.setObjectName("dialog")
        dialog.resize(500, 500)
        dialog.setFixedSize(500, 500)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(ICON_PATH), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dialog.setWindowIcon(icon)
        dialog.setStyleSheet("background-color: rgb(255, 255, 255);")

        # =About Window=

        # >Dialog Frame
        self.frame = QtWidgets.QFrame(dialog)
        self.frame.setGeometry(QtCore.QRect(0, 0, 500, 500))
        self.frame.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")

        # >Label "Wallpaper"
        self.wallpapercredits = QtWidgets.QLabel(self.frame)
        self.wallpapercredits.setGeometry(QtCore.QRect(0, 0, 500, 500))
        self.wallpapercredits.setText("")
        self.wallpapercredits.setPixmap(QtGui.QPixmap(CREDITS_PATH))
        self.wallpapercredits.setScaledContents(True)
        self.wallpapercredits.setObjectName("Wallpapercredits")

        # >OK Button
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setGeometry(QtCore.QRect(200, 420, 100, 30))
        self.pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton.setStyleSheet("background-color: rgb(204, 204, 204);")
        self.pushButton.setObjectName("pushButton")

        # >Label "L3AA1"
        self.L3AA1 = QtWidgets.QLabel(self.frame)
        self.L3AA1.setGeometry(QtCore.QRect(200, 50, 100, 100))
        self.L3AA1.setText("")
        self.L3AA1.setPixmap(QtGui.QPixmap(LOGO_PATH))
        self.L3AA1.setScaledContents(True)
        self.L3AA1.setObjectName("L3AA1")
        self.L3AA1.setStyleSheet("background-color: rgba(0,0,0,0%)")

        # >Label "Team Member"
        self.team = QtWidgets.QLabel(self.frame)
        self.team.setGeometry(QtCore.QRect(150, 160, 200, 150))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.team.setFont(font)
        self.team.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.team.setObjectName("Team")
        self.team.setStyleSheet("background-color: rgba(0,0,0,0%)")

        # >Label "Université de Paris"
        self.u_paris = QtWidgets.QLabel(self.frame)
        self.u_paris.setGeometry(QtCore.QRect(150, 320, 200, 80))
        self.u_paris.setText("")
        self.u_paris.setPixmap(QtGui.QPixmap(UNIV_PATH))
        self.u_paris.setScaledContents(True)
        self.u_paris.setObjectName("U_Paris")
        self.u_paris.setStyleSheet("background-color: rgba(0,0,0,0%)")

        # =DISPLAY ORDER=
        self.wallpapercredits.raise_()
        self.L3AA1.raise_()
        self.team.raise_()
        self.u_paris.raise_()
        self.pushButton.raise_()

        self.retranslateUi(dialog)
        QtCore.QMetaObject.connectSlotsByName(dialog)

    def retranslateUi(self, dialog):
        _translate = QtCore.QCoreApplication.translate
        dialog.setWindowTitle(_translate("dialog", "About"))
        self.pushButton.setText(_translate("dialog", "OK"))
        self.team.setText(_translate("dialog", "Team members:\n" +
                                     "\t- Laforge Johan \n" +
                                     "\t- Tanriverdi Messie\n" +
                                     "\t- Thay Jacky\n" +
                                     "\t- Trividic Yann\n\n" +
                                     "Supervisor:\n" +
                                     "\t- Rogovschi Nicoleta"))
