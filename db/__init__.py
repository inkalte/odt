from pathlib import Path
from share import load_json, save_json
from logs import get_logger

logger = get_logger('db')
db_root = f"{Path(__file__).parent}\\"


class JsonDb:
    def __init__(self, name):
        self.name = name
        self.path = f"{db_root}{name}.json"
        if Path(self.path).exists():
            self.children = load_json(self.path)
        else:
            self.children = {}

    def save(self):
        save_json(self.children, self.path)

    def list(self):
        return list(self.children.values())

    def clear(self):
        self.children = {}
        self.save()
