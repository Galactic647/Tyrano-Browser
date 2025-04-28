from core import config

from typing import Union

from pathlib import Path
import subprocess

DEBUG_ARGS = [
    f'--remote-debugging-port={config.load_config_value("websocket", "port")}',
    '--disable-web-security'
]


class GameProcess(object):
    def __init__(self, game: Union[Path, str]) -> None:
        if isinstance(game, str):
            game = Path(game)
        if not game.exists():
            raise FileNotFoundError(game)
        self.game = game
        self.game_name = game.name
    
    def launch_game(self):
        subprocess.Popen([str(self.game), *DEBUG_ARGS])
