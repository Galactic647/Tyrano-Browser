from PySide2.QtCore import QObject, Signal

import traceback


class GenericWorker(QObject):
    result = Signal(object)
    finished = Signal()

    def __init__(self, task, *args, **kwargs):
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.task(*self.args, **self.kwargs)
            self.result.emit(result)
        except Exception:
            self.result.emit(traceback.format_exc())
        self.finished.emit()
