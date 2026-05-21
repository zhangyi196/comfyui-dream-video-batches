import hashlib
import json
import os
import re


def natsort_key(path):
    basename = os.path.basename(path)
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', basename)]


def hashed_as_strings(*items, **kwargs):
    tokens = "|".join(list(map(str, items)))
    m = hashlib.sha256()
    m.update(tokens.encode(encoding="utf-8"))
    for pair in kwargs.items():
        m.update(str(pair).encode(encoding="utf-8"))
    return m.digest().hex()



class ForEachState:
    def __init__(self, filepath):
        self._filepath = os.path.abspath(filepath)
        self._dir = os.path.normpath(os.path.dirname(self._filepath))
        try:
            with open(self._filepath, "r", encoding="utf8") as f:
                self._data = json.load(f)
        except:
            self._data = dict()

    def _write(self):
        sorted_data = {k: self._data[k] for k in sorted(self._data.keys(), key=natsort_key)}
        with open(self._filepath, "w", encoding="utf8") as f:
            txt = json.dumps(sorted_data, indent=2)
            f.write(txt)

    def add_files_to_process(self, files):
        all_files = set(self._data.keys())
        all_files.update(files)
        for filename in sorted(all_files, key=natsort_key):
            if filename not in self._data:
                self._data[filename] = False
        self._write()

    def mark_done(self, filename):
        self._data[filename] = True
        self._write()

    def pop(self):
        for filename in sorted(self._data.keys(), key=natsort_key):
            if not self._data.get(filename, False):
                print("pop {}".format(filename))
                return os.path.join(self._dir, filename)
        return None
