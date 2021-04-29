'''
Created on Apr 2, 2021

@author: yann

Module that allows the visualisation of the data as a dataframe in the Charts' tab
'''

from PyQt5 import QtGui, QtWidgets

from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant
from PyQt5.QtWidgets import QTableWidgetItem

# Colors in which will be displayed the rows of the TableModel
POS_ROW_COLOR = "#a1d99b"
NEG_ROW_COLOR = "#fdae6b"
NEU_ROW_COLOR = "#eff0f1"

DEFAULT_ROW_HEIGHT = 24


class TableModel(QAbstractTableModel):
    '''Class that manipulates the data contained in a pandas' DataFrame to make it fit a QTableView object in a table.
    This class inherits from the QAbstractTableModel, which allows to play with an interface to begin with.
    '''

    def __init__(self, data):
        '''Constructor of the class

        df -- has to be a pandas' DataFrame. Contains the data to display
        '''
        super(TableModel, self).__init__()
        self.df = data.raw_data
        self.header_labels = data.get_colnames()  # an Index of column names
        self._data = self.df.values.tolist()  # _data is a list of lists

        try:  # in the case there is no polarity col
            self.pol_index = self.header_labels.index(data.get_polarity_colname())
        except ValueError:
            self.pol_index = None
            print("The \"" + data.get_polarity_colname() + "\" column could not be found, the data will not be colored.")

        self.background_colors = {"pos": QtGui.QColor(POS_ROW_COLOR), "neg": QtGui.QColor(NEG_ROW_COLOR)}

    def data(self, index, role):
        if index.isValid():  # iterates through the data to perform different operations depending on the "role"

            if role == Qt.BackgroundRole and self.pol_index is not None:
                ix = self.index(index.row(), self.pol_index).data()  # extraction of the polarity of the sentence
                if ix in self.background_colors:  # if the polarity has been assigned a color
                    color = self.background_colors[ix]
                    return QVariant(color)  # the return value has to be a QVariant object in the data func

            if role == Qt.DisplayRole:
                # See below for the nested-list data structure.
                # .row() indexes into the outer list,
                # .column() indexes into the sub-list
                return self._data[index.row()][index.column()]

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):  # assigns the headers of the table
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def rowCount(self, index):  # eventhough we don't use it explicitly, this method has to be overriden
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):  #  same as rowCOunt
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])


def setColumnWidth(tableView, data):
    '''Function that sets the width of each column of the dataframe for it to match the width of the QTableView object
    '''
    df = data.raw_data
    nb_cols = len(df.columns)

    # index of the principal data (the text that was classified)
    main_text_index = df.columns.tolist().index(data.get_textual_data_colname())

    #  width that occupies the other columns
    width_occupied_by_the_other_cols = tableView.width() * 2 / 3

    if nb_cols < 10:  # if the event that we have less than 10 columns, the table will fit the QTableView width entirely
        for i in range(nb_cols):
            tableView.setColumnWidth(i, width_occupied_by_the_other_cols / nb_cols)
        tableView.horizontalHeader().setSectionResizeMode(main_text_index, QtWidgets.QHeaderView.Stretch)

    else:  # or it will be larger and all the cols except the main col will be 150px large
        for i in range(nb_cols):
            tableView.setColumnWidth(i, 150)
        tableView.setColumnWidth(main_text_index, tableView.width() * 1 / 3)


def setRowHeight(tableView, data):
    nb_rows = data.raw_data.shape[0]
    for i in range(nb_rows):
        tableView.verticalHeader().resizeSection(i, DEFAULT_ROW_HEIGHT)


def handleItemEnteredTableView(self, item):
    item.setBackground(QtGui.QColor('moccasin'))


def handleItemExitedTableView(self, item):
    item.setBackground(QTableWidgetItem().background())
