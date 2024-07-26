import time
from typing import Dict
from attrs import define, field, Factory as new
"""
Measures performance of function calls and operation counts configurable by user

interfaced through Decorators (see cascade.py for example implementation)
"""

@define
class PerfEval:
    perf: Dict[str, Dict[str, list]] = field(default=new(dict))
    stime: Dict[str, float] = field(default=new(dict))
    etime: Dict[str, float] = field(default=new(dict))
    comp: Dict[str, int] = field(default=new(dict))
    val_change: Dict[str, int] = field(default=new(dict))
    access: Dict[str, int] = field(default=new(dict))

    def start(self, func):
        self.stime[func] = time.time()
        self.comp[func] = 0
        self.val_change[func] = 0
        self.access[func] = 0

    # func is function id, tag is [("key", val),...]
    def end(self, func):
        self.etime[func] = time.time()
        tags = [("avg_time", self.etime[func] - self.stime[func]),
            ("comp", self.comp[func]), ("val_change", self.val_change[func]),
            ("access", self.access[func])]
        if func not in self.perf: self.perf[func] = {}
        vals = self.perf[func]
        for (key, val) in tags:
            if key not in vals: vals[key] = [val]
            else: vals[key].append(val)

    def inc(self, func, c, v, a):
        self.comp[func] += c
        self.val_change[func] += v
        self.access[func] += a

    def clear(self):
        self.perf = {}

    def _prtRow(self, key, val, key_len):
        print(f"{key}:")
        for k, v in val.items():
            avg = sum(v)/len(v)
            if k == "avg_time":
                avg = str(round(avg*1000000, 2)) + "ns"
                print(f" {k + ':':<{key_len+1}} {avg}")
            elif avg > 0:
                print(f" {k + ':':<{key_len+1}} {avg:.4e}")

    def print(self):
        print("------PERFORMANCE------")
        key_len = max(len(k) for val in self.perf.values() for k in val)
        for key, val in self.perf.items():
            self._prtRow(key, val, key_len)
