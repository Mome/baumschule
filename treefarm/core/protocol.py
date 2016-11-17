from collections import namedtuple
import os
import json
from datetime import datetime

Record = namedtuple('Record', ['name' 'time', 'perf'])

class Protocol:
    def __init__(self, name):
        self.name = name
        self.records = {}

    def save(self, name=None):
        if not name:
            name = self.name
        fullpath = os.path.join(path, name)
        with open(fullpath) as f:
            json.dump(self.records)

    def write(self, name, perf):
        tmp = Record(naem, str(datetime.now()), perf)
        if name not in self.records:
            self.records = []
        self.records[name].append(tmp)

    def get_best(self):
        return max(
            self.records.items(),
            key = lambda item : item.perf)
