import json
import glob
import os


def hex_to_rgb(hex):
    if hex[0] == '#':
        hex = hex[1:]
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#%02X%02X%02X' % rgb


class ExtraColor:
    RESULT_FOREGROUND_EQUAL = 'result.foreground.equal'
    RESULT_FOREGROUND_NOTEQUAL = 'result.foreground.notequal'
    RESULT_FOREGROUND_LOWERTHAN = 'result.foreground.lowerthan'
    RESULT_FOREGROUND_HIGHERTHAN = 'result.foreground.higherthan'


class ThemeLoader(object):
    def __init__(self, parent):
        self.parent = parent
        self.theme_path = None
        self.theme = None

    def load_theme(self, theme_path):
        self.theme_path = theme_path
        self.theme = os.path.basename(theme_path)

        if not os.path.exists(theme_path):
            raise FileNotFoundError(theme_path)
        
        qss = glob.glob(theme_path + '/*.qss')
        if not len(qss):
            raise FileNotFoundError('No QSS file found in ' + theme_path)
        elif len(qss) > 1:
            raise Exception('Multiple QSS files found in ' + theme_path)
        
        if not os.path.exists(theme_path + '/extra-color.json'):
            raise FileNotFoundError(theme_path + '/extra-color.json')
        
        with open(qss[0], 'r', encoding='utf-8') as f:
            qss = f.read()
            f.close()
        self.parent.setStyleSheet(qss)
        
        with open(theme_path + '/extra-color.json', 'r', encoding='utf-8') as f:
            extra_colors = json.load(f)
            f.close()
        
        ec = dict((k, v) for k, v in extra_colors.items() if not k.startswith('_'))
        for k, v in ec.items():
            setattr(ExtraColor, k, hex_to_rgb(extra_colors[v]))
