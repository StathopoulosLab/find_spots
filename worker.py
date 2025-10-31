# worker.py
"""
Mechanism to pull work out of Qt main thread so that the UI doesn't hang
"""

from PySide6.QtCore import QObject, QRunnable, Signal
from sys import exc_info
from traceback import format_exc, print_exc

class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)

class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        # Run the passed fn with the passed args
        try:
            result = self.fn(*self.args, **self.kwargs)
        except BaseException:
            print_exc()
            exctype, value = exc_info()[:2]
            self.signals.error.emit((exctype, value, format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

