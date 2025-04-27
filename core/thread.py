from PySide2.QtCore import QObject, QThread

from typing import Optional, Callable


class ThreadManager(object):
    def __init__(self):
        self.threads = list()
        self.workers = list()

    def run(self, worker: QObject, *args, callback: Optional[Callable] = None, **kwargs):
        thread = QThread()
        worker = worker(*args, **kwargs)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        if callback:
            worker.result.connect(callback)

        def on_finished():
            self.threads.remove(thread)
            self.workers.remove(worker)
        
        thread.finished.connect(on_finished)

        self.threads.append(thread)
        self.workers.append(worker)
        thread.start()
