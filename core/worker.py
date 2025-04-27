from PySide2.QtCore import QObject, Signal


class GenericWorker(QObject):
    result = Signal(object)
    finished = Signal()

    def __init__(self, task, *args, **kwargs):
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs

    def run(self):
        result = self.task(*self.args, **self.kwargs)
        self.result.emit(result)
        self.finished.emit()
