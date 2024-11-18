from core.parser import parser_integrity_check

from multiprocessing import Process, Value, Array
import ctypes


class IntegrityChecker(object):
    def __init__(self, save_file: str) -> None:
        self.status = Array(ctypes.c_char, 128)
        self.progress = Value(ctypes.c_int, 0)
        self.max_progress = Value(ctypes.c_int, 0)

        self.valid = Value(ctypes.c_bool, False)
        self.original_sig = Array(ctypes.c_char, 64)
        self.repacked_sig = Array(ctypes.c_char, 64)

        self.args = (self.status, self.progress, self.max_progress,
                     self.valid, self.original_sig, self.repacked_sig)

        self.save_file_path = save_file
    
    def start(self) -> None:
        if not self.save_file_path:
            raise ValueError('Please set a save file path first')
        Process(target=parser_integrity_check, args=(self.save_file_path, self.args,), daemon=True).start()

    def get_progress(self) -> tuple:
        return self.status.value, self.progress.value, self.max_progress.value
    
    def get_result(self) -> tuple:
        return self.valid.value, self.original_sig.value, self.repacked_sig.value