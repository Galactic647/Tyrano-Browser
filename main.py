from core import thread, process, config, cdphandler as cdph, tablemanager as tm
from core.cdphandler import TyranoVars
from ui.ui import LucidEngineUI

from PySide2.QtWidgets import QApplication, QFileDialog, QTreeWidgetItem, QMessageBox
from PySide2.QtGui import QBrush, QColor
from PySide2.QtMultimedia import QSound
from PySide2.QtCore import Signal, QTimer

import asyncio
import json
import time
import sys
import os

class LucidEngine(LucidEngineUI):
    update_gui_signal = Signal(dict)

    def __init__(self):
        super().__init__()

        self._spb_value = 0
        self._lpb_value = 0

        self.thread_manager = thread.ThreadManager()
        self.persistent_async = thread.PersistentAsync()
        self.persistent_async.start()

        self.update_gui_signal.connect(self.gui_updater)

        self.actionLaunch_Game.triggered.connect(self.launch_game)
        self.actionSave_Table.triggered.connect(self.save_table)
        self.actionLoad_Table.triggered.connect(self.load_table)

        self.ScanButton.clicked.connect(self.scan_function)
        self.ClearButton.clicked.connect(self.clear_result)

        # self._update_prog_bar = QTimer()
        # self._update_prog_bar.timeout.connect(self.update_progress_bars)
        # self._update_prog_bar.start(100)

    @thread.run_cdp_async_protocol
    async def close_websocket(self, event):
        await self.handler.close()
        self.persistent_async.stop()

        return super().closeEvent(event)

    def closeEvent(self, event):
        self.close_websocket(event)

    def update_progress_bars(self):
        self.ScanProgressBar.setValue(self._spb_value)
        self.LoadProgressBar.setValue(self._lpb_value)

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

                if not isinstance(value, str):
                    value = json.dumps(value)

                item = QTreeWidgetItem(self.ResultTab, [
                    name,
                    value,
                    value,
                    value,
                    path
                ])
                self._rt_list_items.append(item)
        self.ScanButton.setEnabled(True)
        self.ClearButton.setEnabled(True)

        self.continue_polling()
                
    @thread.run_cdp_async_protocol
    async def search_by_name(self, name):
        await self.wait_for_polling()

        try:
            start = time.perf_counter()
            self._data = await self.handler.evaluate(TyranoVars.F, True)
            self._data = self.flatten(self._data, 'stat.f.')

            self._tf_data = await self.handler.evaluate(TyranoVars.TF, True)
            self._tf_data = self.flatten(self._tf_data, 'variable.tf.')
            self._data.update(self._tf_data)

            data = self._data
            found = []
            ndata = len(data)
            for idx, k in enumerate(data, start=1):
                if name in k.rpartition('.')[-1].split('[')[0]:
                    found.append(k)
                self._spb_value = int(idx / ndata * 100)

            self.FoundLabel.setText(f'Found: {len(found)} ({time.perf_counter() - start:.4f}s)')

            self.display_result(list({n: self._data[n]} for n in found))
            self._spb_value = 0
        except Exception as e:
            print(repr(e))

    @thread.run_cdp_async_protocol
    async def search_by_value(self, value):
        await self.wait_for_polling()

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
        ndata = len(data)
        for idx, d in enumerate(data.items(), start=1):
            k, v = d
            if v == value:
                found.append(k)
            self._spb_value = int(idx / ndata * 100)

        self.FoundLabel.setText(f'Found: {len(found)} ({time.perf_counter() - start:.4f}s)')

        self.display_result(list({n: self._data[n]} for n in found))
        self._spb_value = 0

    @thread.run_cdp_async_protocol
    async def set_value(self, target, value):
        self.pause_polling()
        await self.wait_for_polling()

        if value.isdigit():
            value = int(value)
        else:
            try:
                value = float(value)
            except ValueError:
                pass

        await self.handler.set_value(f'TYRANO.kag.{target}', value)
        self.continue_polling()

    async def wait_for_polling(self):
        while True:
            if self._polling_paused:
                break
            await asyncio.sleep(0.1)

    def clear_result(self):
        self.ResultTab.clear()
        self._rt_list_items = list()

        self.ClearButton.setEnabled(False)

    def scan_function(self):
        self.pause_polling()
        self.clear_result()

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
    
    def _get_vl_data(self, root):
        data = dict()
        data = {
            'name': root.text(0),
            'path': root.text(1),
            'value': root.text(2),
            'color': root.foreground(0).color().getRgb()[:-1],
        }

        children = list()
        for i in range(root.childCount()):
            children.append(self._get_vl_data(root.child(i)))

        data['children'] = children
        return data

    def get_vl_data(self):
        data = list()
        root = self.ValueListWidget.invisibleRootItem()

        for i in range(root.childCount()):
            data.append(self._get_vl_data(root.child(i)))
        return data
    
    def save_table(self):
        location = QFileDialog.getSaveFileName(self, 'Save Table', '', 'Tyrano Browser Table Files (*.tbt)')[0]
        if location:
            tm.save_table(location, self.get_vl_data())

    def _load_table(self, data: list, parent=None):
        for item in data:
            value = item['value']
            if not isinstance(value, str):
                value = json.dumps(value)
            it = QTreeWidgetItem(parent, [item['name'], item['path'], value])
            it.setForeground(0, QBrush(QColor(*item['color'])))
            it.setForeground(1, QBrush(QColor(*item['color'])))
            it.setForeground(2, QBrush(QColor(*item['color'])))
            if value and item['path']:
                self._tree_list_items.append(it)

            if item['children']:
                self._load_table(item['children'], it)

    def load_table(self):
        location = QFileDialog.getOpenFileName(self, 'Load Table', '', 'Tyrano Browser Table Files (*.tbt)')[0]
        if not location:
            return
        if self.ValueListWidget.invisibleRootItem().childCount():
            confirmation = QMessageBox.question(
                self,
                'Confirm',
                'Are you sure you want to load a new table? This will clear the current table.'
            )
            if confirmation == QMessageBox.No:
                return
        self.ValueListWidget.clear()
        data = tm.load_table(location)
        self._load_table(data, self.ValueListWidget)
    
    def continue_polling(self):
        self._pause_polling = False
    
    def pause_polling(self):
        self._pause_polling = True
    
    @thread.run_cdp_async_protocol
    async def polling(self):
        # NOTE
        # Needs to check if the item is freezed or not
        # Freezed items shouldn't get their value updated

        # TODO CRITICAL
        # - value can be undefined, we should never set an undefined value for whatever reason
        # - check what happen if a list is empty (e.g. stat.f.some_var = []) how would we query this
        general_items = result_items = paths = None

        while True:
            start = time.perf_counter()
            if self._pause_polling:
                print('paused polling')
                self._polling_paused = True
                await asyncio.sleep(0.1)
                continue
            elif not self._connected:
                print('not connected')
                await asyncio.sleep(0.1)
                continue
            self._polling_paused = False
            
            try:
                if self._tree_list_items:
                    general_items = list(map(lambda x: x.text(1), self._tree_list_items))
                if self._rt_list_items:
                    result_items = list(map(lambda x: x.text(4), self._rt_list_items))
            except Exception as e:
                print(repr(e))

            if result_items:
                general_items = general_items + result_items
            if general_items:
                paths = set(general_items)

            if not paths:
                await asyncio.sleep(0.1)
                continue

            expression = ','.join(f'"{p}":TYRANO.kag.{p}' for p in paths)
            expression = f'({{{expression}}})'

            object_id = await self.handler.evaluate(expression, False)
            response = await self.handler.get_properties(object_id)
            data = dict()
            try:
                for r in response:
                    if r['name'] in cdph.SKIP_PROPERTIES:
                        continue
                    value = r['value']

                    if value['type'] == 'undefined':
                        data[r['name']] = '??'
                    else:
                        data[r['name']] = value['value']
                
                for ti in self._tree_list_items:
                    if ti.text(1) in data:
                        val = data[ti.text(1)]

                        if not isinstance(val, str):
                            val = json.dumps(val)
                        ti.setText(2, val)
                
                for ri in self._rt_list_items:
                    if ri.text(4) in data:
                        prev = ri.text(2)
                        try:
                            prev = json.loads(prev)
                        except json.JSONDecodeError:
                            pass

                        cur = data[ri.text(4)]
                        try:
                            if isinstance(cur, str):
                                ri.setText(1, cur)
                                cur = json.loads(cur)
                            else:
                                ri.setText(1, json.dumps(cur))
                        except json.JSONDecodeError:
                            pass

                        if (isinstance(prev, str) or isinstance(cur, str)) and prev != cur:
                            ri.setForeground(1, QBrush(QColor(255, 0, 0)))
                        elif cur == prev:
                            ri.setForeground(1, QBrush(QColor(255, 255, 255)))
                        elif cur < prev:
                            ri.setForeground(1, QBrush(QColor(255, 0, 0)))
                        elif cur > prev:
                            ri.setForeground(1, QBrush(QColor(96, 128, 255)))
            except Exception as e:
                print(repr(e))
            print(time.perf_counter() - start)
            await asyncio.sleep(0.1)
    
    @thread.run_cdp_async_protocol
    async def connect_to_game(self):
        ws_url = await cdph.get_cdp_ws_url_async(9222, self.game.game, wait=True)
        self.handler = cdph.CDPHandler(ws_url)
        await self.handler.connect()
        self.InfoLabel.setText(self.game.game_name)
        self._connected = True

    @thread.threaded
    def _launch_game(self):
        self.game.launch_game()

    def launch_game(self):
        game_loc = QFileDialog.getOpenFileName(self, 'Open Game', filter='Executable (*.exe)')[0]
        if game_loc:
            self.game = process.GameProcess(game_loc)
            self._launch_game()
            self.connect_to_game()
            self.polling()


def main():
    app = QApplication(sys.argv)
    check_config()

    window = LucidEngine()
    window.show()
    sys.exit(app.exec_())


def check_config():
    config.create_config()
    
    if not os.path.exists('theme'):
        os.mkdir('theme')
        QMessageBox.critical(None, 'Error', 'No themes found, the app will not use any theme, this might cause UI issues.')
    elif (theme := config.load_config_value('app', 'theme')) not in os.listdir('theme'):
        QMessageBox.warning(None, 'Warning', f'Theme {theme} not found, using default-dark theme.')


if __name__ == '__main__':
    main()

