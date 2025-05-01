from core import worker, thread, process, cdphandler as cdph
from core.cdphandler import TyranoVars
from ui.ui import TyranoBrowserUI

from PySide2.QtWidgets import QApplication, QFileDialog, QTreeWidgetItem, QMessageBox
from PySide2.QtCore import Qt, QTimer, QThread, Signal
from PySide2.QtMultimedia import QSound

from pathlib import Path
import asyncio
import json
import time
import sys
import os

class TyranoBrowser(TyranoBrowserUI):
    update_gui_signal = Signal(dict)

    def __init__(self):
        super().__init__()

        self.thread_manager = thread.ThreadManager()
        self.persistent_async = thread.PersistentAsync()
        self.persistent_async.start()

        self.update_gui_signal.connect(self.gui_updater)
        self.actionLaunch_Game.triggered.connect(self.open_save_file)
        self.ScanButton.clicked.connect(self.scan_function)

    @thread.run_cdp_async_protocol
    async def close_websocket(self, event):
        await self.handler.close()
        self.persistent_async.stop()

        return super().closeEvent(event)

    def closeEvent(self, event):
        self.close_websocket(event)

    def update_gui(self, func, *args, **kwargs):
        self.update_gui_signal.emit({'func': func, 'args': args, 'kwargs': kwargs})

    def gui_updater(self, data: dict):
        func = data['func']
        args = data.get('args', tuple())
        kwargs = data.get('kwargs', dict())
        func(*args, **kwargs)

    def display_result(self, data):
        for d in data:
            for path, value in d.items():
                name = path.split('.')[-1]

                QTreeWidgetItem(self.ResultTab, [
                    name,
                    str(value),
                    str(value),
                    path
                ])
        self.ScanButton.setEnabled(True)
                
    @thread.run_cdp_async_protocol
    async def search_by_name(self, name):
        start = time.perf_counter()
        self._data = await self.handler.evaluate(TyranoVars.F, True)
        self._data = self.flatten(self._data, 'stat.f.')

        self._tf_data = await self.handler.evaluate(TyranoVars.TF, True)
        self._tf_data = self.flatten(self._tf_data, 'variable.tf.')
        self._data.update(self._tf_data)

        data = self._data
        found = []
        for k in data:
            if name in k.rpartition('.')[-1].split('[')[0]:
                found.append(k)

        self.FoundLabel.setText(f'Found: {len(found)} ({time.perf_counter() - start:.4f}s)')

        self.display_result(list({n: self._data[n]} for n in found))

    @thread.run_cdp_async_protocol
    async def search_by_value(self, value):
        if value.isdigit():
            value = int(value)
        else:
            try:
                value = float(value)
            except ValueError:
                pass

        start = time.perf_counter()
        self._data = await self.handler.evaluate(TyranoVars.F, True)
        self._data = self.flatten(self._data, 'stat.f.')

        self._tf_data = await self.handler.evaluate(TyranoVars.TF, True)
        self._tf_data = self.flatten(self._tf_data, 'variable.tf.')
        self._data.update(self._tf_data)

        data = self._data

        found = []
        for k, v in data.items():
            if v == value:
                found.append(k)

        self.FoundLabel.setText(f'Found: {len(found)} ({time.perf_counter() - start:.4f}s)')

        self.display_result(list({n: self._data[n]} for n in found))

    def scan_function(self):
        self.update_gui(self.ResultTab.clear)

        if self.ScanButton.text() == 'Scan':
            self.update_gui(self.ScanButton.setEnabled, False)

            if self.NameRadioButton.isChecked():
                self.search_by_name(self.ScanInput.text())
            else:
                self.search_by_value(self.ScanInput.text())

    def flatten(self, d, prefix=None):
        result = dict()
        for k, v in d.items():
            if prefix:
                name = f'{prefix}{k}'
            else:
                name = k
            values = self._flatten(name, v)
            result.update(values)
        return result

    def _flatten(self, name, value):
        if isinstance(value, list):
            flat = dict()
            for i, v in enumerate(value):
                flat.update(self._flatten(f'{name}[{i}]', v))
            return flat
        elif isinstance(value, dict):
            flat = dict()
            for k, v in value.items():
                flat.update(self._flatten(f'{name}.{k}', v))
            return flat
        return {name: value}
    
    @thread.run_cdp_async_protocol
    async def connect_to_game(self):
        ws_url = await cdph.get_cdp_ws_url_async(9222, self.game.game, wait=True)
        self.handler = cdph.CDPHandler(ws_url)
        await self.handler.connect()
        self.InfoLabel.setText(self.game.game_name)

    @thread.threaded
    def launch_game(self):
        self.game.launch_game()

    def open_save_file(self):
        game_loc = QFileDialog.getOpenFileName(self, 'Open Game', filter='Executable (*.exe)')[0]
        self.game = process.GameProcess(game_loc)
        self.launch_game()
        self.connect_to_game()


def main():
    app = QApplication(sys.argv)
    window = TyranoBrowser()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

