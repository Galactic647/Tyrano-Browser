from PySide2.QtCore import QObject, Signal

import traceback
import asyncio


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


class AsyncRunnerWorker(QObject):
    result = Signal(object)
    finished = Signal()

    def __init__(self, coro, *args, **kwargs):
        super().__init__()
        self.coro = coro
        self.args = args
        self.kwargs = kwargs
        
        self.loop = None

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        result = self.loop.run_until_complete(self.coro(*self.args, **self.kwargs))
        self.result.emit(result)
        self.finished.emit()

        self.loop.close()
