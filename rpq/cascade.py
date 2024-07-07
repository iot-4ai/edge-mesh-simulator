import functools
import time
from typing import Callable, Dict
import networkx as nx
import matplotlib.pyplot as plt
import os
import re
import heapq
from dataclasses import dataclass
from sortedcontainers import SortedDict
from dgraph import DGraph
from attrs import define, field, Factory as new

@define
class PerfEval:
    perf: Dict[str, Dict[str, list]] = field(default=new(dict))
    stime: float = 0.0
    etime: float = 0.0
    comp: int = 0
    val_change: int = 0
    access: int = 0

    def start(self):
        self.stime = time.time()
        self.comp = 0
        self.val_change = 0
    
    # func is function id, tag is [("key", val),...]
    def end(self, func):
        self.etime = time.time()
        tags = [("avg_time", self.etime - self.stime), 
                ("comp", self.comp), 
                ("val_change", self.val_change),
                ("access", self.access)]
        if func not in self.perf: self.perf[func] = {}
        vals = self.perf[func]
        for (key, val) in tags:
            if key not in vals: vals[key] = [val]
            else: vals[key].append(val)

    def inc(self, c, v, a):
        self.comp += c
        self.val_change += v
        self.access += a
    
    def _prtRow(self, key, val, key_len):
        print(f"{key}:")
        for k, v in val.items():
            avg = sum(v) / len(v)
            print(f" {k + ':':<{key_len+1}} {avg:.4e}")

    def print(self):
        print("------PERFORMANCE------")
        key_len = max(len(k) for val in self.perf.values() for k in val)
        for key, val in self.perf.items():
            self._prtRow(key,val,key_len)



type SP_MAP[T] = Dict[str, T]
@dataclass
class Pred:
    prev: str
    height: int
    update: bool

@define
class CascadeSP:
    graph: DGraph = field(default=new(DGraph))
    pred: SP_MAP[Pred] = field(default=new(dict))   
    cache: SP_MAP[float] = field(default=new(dict))
    perf: PerfEval = field(default=new(PerfEval))

    @staticmethod
    def _perfDec(method: Callable):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            self.perf.start()
            result = method(self, *args, **kwargs)
            self.perf.end(method.__name__)
            return result
        return wrapper

    def perfShow(self):
        self.perf.print()
    
    # alias 
    show = perfShow

    def gen(self, n=10, p=0.5, seed=None):
        self.graph.gen(n,p,seed)
    
    def print(self):
        print(self.pred)
        print(self.cache)
        self.graph.plot("g.png")

    @_perfDec
    def upd(self, updates):
        return self.graph.upd(updates)

    @_perfDec
    def dijkstra(self, v):
        comp = valc = acc = 0
        v = str(v)

        n = self.graph.n()
        self.pred = {str(v): Pred(prev="", height=0, update=False) for v in range(n)}
        self.cache = {str(v): float("inf") for v in range(n)}
        self.cache[v] = 0.0

        pq = []
        heapq.heappush(pq, (0, v))
        vis = set()
        
        while pq:
            curr_dist, curr = heapq.heappop(pq)

            if curr in vis: continue
            vis.add(curr)

            for key, val in self.graph.graph[curr].items():
                if key not in vis:
                    dist = curr_dist + val["w"]

                    if dist < self.cache[key]:
                        self.cache[key] = dist
                        self.pred[key].height = self.pred[curr].height + 1
                        self.pred[key].prev = curr
                        heapq.heappush(pq, (dist, key))
                        valc += 1
                    comp += 1
            acc += 1
        
        self.perf.inc(comp,valc,acc)
    
    def cascade(self):
        return

# Example usage
if __name__ == "__main__":
    # Create an instance of CascadeSP
    csp = CascadeSP()
    
    # Assuming upd method requires updates
    updates = []  # Replace with actual updates
    csp.upd(updates)

    csp.gen()

    csp.dijkstra(0)

    csp.show() 