from core import worker

from PySide2.QtCore import QObject, QThread

from typing import Optional, Callable

import functools
import asyncio


def threaded(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        callback = kwargs.pop('callback', None)

        def task():
            result = func(self, *args, **kwargs)

            if callback is not None:
                callback(result)
        
        self.thread_manager.run(
            worker.GenericWorker,
            task,
        )
    return wrapper

def run_async(coro):
    @functools.wraps(coro)
    def wrapper(self, *args, **kwargs):
        callback = kwargs.pop('callback', None)

        async def task():
            result = await coro(self, *args, **kwargs)

            if callback is not None:
                callback(result)
        
        self.thread_manager.run(
            worker.AsyncRunnerWorker,
            task,
        )
    return wrapper

def run_cdp_async_protocol(coro):
    @functools.wraps(coro)
    def wrapper(self, *args, **kwargs):
        callback = kwargs.pop('callback', None)

        future = asyncio.run_coroutine_threadsafe(
            coro(self, *args, **kwargs),
            self.persistent_async.loop
        )

        if callback is not None:
            callback(future.result())
    return wrapper


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


class PersistentAsync(QObject):
    def __init__(self):
        super().__init__()
        self.thread_ = QThread()
        self.moveToThread(self.thread_)
        self.thread_.started.connect(self._run)

        self.loop = None
        self._shutdown_event = asyncio.Event()

    def _run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        async def shutdown_watcher():
            await self._shutdown_event.wait()
            self.loop.stop()
        
        self.loop.create_task(shutdown_watcher())
        self.loop.run_forever()

        self._cleanup_loop()
        self.thread.quit()

    def _cleanup_loop(self):
        if self.loop:
            tasks = asyncio.all_tasks(self.loop)
            for task in tasks:
                task.cancel()
            
            self.loop.run_until_complete(
                asyncio.gather(*tasks, return_exceptions=True)
            )
            
            self.loop.close()
            self.loop = None
    
    def start(self):
        self.thread_.start()

    def stop(self):
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(
                self._shutdown_event.set
            )
            
            # Wait for thread to finish (optional timeout)
            self.thread.wait(2000)  # 2 second timeout
            
            # Force quit if not stopped cleanly
            if self.thread.isRunning():
                self.thread.terminate()
