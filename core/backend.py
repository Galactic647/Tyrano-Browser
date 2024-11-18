from core.thread import KillableThread
from core.parser import SavParser, parser_integrity_check
from core.workers import IntegrityChecker

from pathlib import Path
import os


class NoParserLoadedError(Exception):
    pass


class Backend(object):
    def __init__(self, parent):
        self.parent = parent

        self.save_file = None
        self.parser = None

        self.last_modified = None

    def _create_parser(self):
        if self.save_file is None:
            return
        self.parser = SavParser(self.save_file)

    def set_save_file(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f'File {path} does not exists')
        self.save_file = Path(path)
        self._create_parser()

    def get_raw_data(self):
        if not self.parser:
            raise NoParserLoadedError
        return self.parser.unpack()
    
    def integrity_check(self, callback=None):
        if not self.save_file:
            return
        ic = IntegrityChecker(str(self.save_file))
        ic.start()

        if callback:
            self.parent.test_timer.connect(lambda: callback(ic))
            # self.parent.scan_progress_bar_check_interval.start()
    
    def is_source_modified(self) -> bool:
        if not self.save_file:
            return False
        mtime = self.save_file.stat().st_mtime

        if self.last_modified is None:
            self.last_modified = mtime
            return False
        return mtime != self.last_modified
        
