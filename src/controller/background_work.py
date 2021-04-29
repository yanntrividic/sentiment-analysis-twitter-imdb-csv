'''
Created on Mar 25, 2021

@author: yann

This module implements QThread for the app to be able to use differents threads for various tasks (API status tests,
models loading, requests processing, etc.)
'''
import sys
import time
import traceback

from PyQt5.QtCore import pyqtSlot, QObject, pyqtSignal, QThread


class Worker(QThread):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, parent, *args, **kwargs):
        super(Worker, self).__init__(parent)  #  specifying a parent allows us to terminate properly the thread if needed
        # Store constructor arguments (re-used for processing)
        self.signals = WorkerSignals()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        '''
        Initialize the runner function with passed args, kwargs.
        '''
        start = time.perf_counter()

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            # FIXME: the Worker is deleted before it's job is totally done.
            # RuntimeError: wrapped C/C++ object of type WorkerSignals has been deleted
            self.signals.finished.emit()  # Done
            finish = time.perf_counter()
            print(f'Work with {self.fn.__name__} finished in {round(finish-start, 2)} second(s)')


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
