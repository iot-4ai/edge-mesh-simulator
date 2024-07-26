import time
from typing import Dict
from attrs import define, field, Factory as new
"""
Measures performance of function calls and operation counts configurable by user

Interfaced through Decorators (see cascade.py for example implementation)
"""

@define
class PerfEval:
    perf: Dict[str, Dict[str, list]] = field(default=new(dict))
    s_time: Dict[str, float] = field(default=new(dict))
    e_time: Dict[str, float] = field(default=new(dict))
    comp: Dict[str, int] = field(default=new(dict))
    change: Dict[str, int] = field(default=new(dict))
    access: Dict[str, int] = field(default=new(dict))

    def start(self, func):
        self.s_time[func] = time.time()
        self.comp[func] = self.change[func] = self.access[func] = 0

    # func is function id, tag is [("key", val),...]
    def end(self, func):
        self.e_time[func] = time.time()
        tags = [("avg_time", self.e_time[func] - self.s_time[func]),
            ("comp", self.comp[func]), ("change", self.change[func]),
            ("access", self.access[func])]
        if func not in self.perf: self.perf[func] = {}
        vals = self.perf[func]
        for (key, val) in tags:
            if key not in vals: vals[key] = [val]
            else: vals[key].append(val)

    def inc(self, func, comp, chg, acc):
        self.comp[func] += comp
        self.change[func] += chg
        self.access[func] += acc

    def clear(self):
        self.perf = {}

    def _row(self, key, val, _len):
        print(f"{key}:")
        for k, v in val.items():
            avg = sum(v)/len(v)
            if k == "avg_time":
                avg = str(round(avg*1000000, 2)) + "ns"
                print(f" {k + ':':<{_len+1}} {avg}")
            elif avg > 0:
                print(f" {k + ':':<{_len+1}} {avg:.4e}")

    def print(self):
        print("------PERFORMANCE------")
        _len = max(len(k) for val in self.perf.values() for k in val)
        for key, val in self.perf.items():
            self._row(key, val, _len)
