import functools
import time
from typing import Callable, Dict, List
import os
import heapq
from dataclasses import dataclass
from dgraph import DGraph
from attrs import define, field, Factory as new
import pickle

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
                ("comp", self.comp[func]), 
                ("val_change", self.val_change[func]),
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
            avg = sum(v) / len(v)
            if k == "avg_time": 
                avg = str(round(avg*1000000,2)) + "ns"
                print(f" {k + ':':<{key_len+1}} {avg}")
            elif avg > 0: print(f" {k + ':':<{key_len+1}} {avg:.4e}")

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
    val: float

@define
class CascadeSP:
    graph: DGraph = field(default=new(DGraph))
    pred: SP_MAP[Pred] = field(default=new(dict))   
    cache: SP_MAP[float] = field(default=new(dict))
    perf: PerfEval = field(default=new(PerfEval))
    updates: List[tuple] = field(default=new(list))
    repairs: List[tuple] = field(default=new(list))

    @staticmethod
    def _perfDec(method: Callable):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            self.perf.start(method.__name__)
            result = method(self, *args, **kwargs)
            self.perf.end(method.__name__)
            return result
        return wrapper

    def show(self):
        self.perf.print()
    
    def perfClear(self):
        self.perf.clear()


    def plot(self, filename="sp.png"):
        self.graph.plot(filename, pred=self.pred, upd=self.updates)

    def gen(self, n=10, p=0.5, seed=None):
        self.graph.gen(n,p,seed)
    
    def print(self):
        print(self.pred)
        print(self.cache)

    def clear(self):
        self.updates = []; self.pred = {}; self.cache = {};

    def load(self, filename):
        self.graph = pickle.load(open(filename, "rb"))  # noqa: SIM115

    def write(self, filename="data.pickle"):
        pickle.dump(self.graph, open(filename, "wb"))  # noqa: SIM115

    def randUpd(self, N, opt=None):
        upd = self.graph.randUpd(N, opt)
        return self.upd(upd)

    # updates in form [('id', (op, weight=None)),...]
    # op = "add", "rem", "mod"
    def upd(self, updates):
        ret = self.graph.upd(updates)
        upds = [upd for upd, ret in zip(updates, ret) if ret]
        self._cascProp(upds)
        return ret
    
    @_perfDec
    def _cascProp(self, upds):
        for upd in upds:
            u = min(upd[0][0],upd[0][1], key=lambda x: self.cache[x])
            v = upd[0][0] if u == upd[0][1] else upd[0][1]
            self._cascMatch((u,v), upd[1], upd[2])

    def _predSet(self, u, v, w):
        self.cache[v] = self.cache[u] + w 
        self.pred[v].height = self.pred[u].height + 1
        self.pred[v].prev = u
        self.pred[v].val = w

    @_perfDec
    def dijkstra(self, v):
        self.clear()
        n, v = self.graph.n(), str(v)
        self.pred = {str(v): Pred(prev="", height=0, val=0) for v in range(n)}
        self.cache = {str(v): float("inf") for v in range(n)}
        self.cache[v] = 0.0
        pq = []; vis = set()
        heapq.heappush(pq, (0, v))   
        comp, valc, acc = self._spLoop(pq, vis)
        self.perf.inc("dijkstra", comp,valc,acc)
    
    def _spLoop(self, pq, vis):
        comp = valc = acc = 0
        while pq:
            curr_dist, curr = heapq.heappop(pq)
            if curr in vis: continue
            vis.add(curr)
            for key, val in self.graph.graph[curr].items():
                if key not in vis:
                    dist = curr_dist + val["w"]
                    if dist < self.cache[key]:
                        self._predSet(curr, key, val["w"])
                        heapq.heappush(pq, (dist, key))
                        valc += 1
                    comp += 1
            acc += 1
        return comp, valc, acc
    
    @_perfDec
    def _cascLoop(self):
        vis = set()
        comp = valc = acc = 0
        while self.updates:
            curr_dist, curr, *opt = heapq.heappop(self.updates)
            if len(opt) > 0 and opt[0] not in vis: vis.add(opt[0])
            if curr in vis: continue
            vis.add(curr)
            if curr_dist != self.cache[curr]:
                curr_dist = self.cache[curr]
            for key, val in self.graph.graph[curr].items():
                if key not in vis:
                    dist = curr_dist + val["w"]
                    if dist < self.cache[key]:
                        self._predSet(curr, key, val["w"])
                        heapq.heappush(self.updates, (dist, key))
                        valc += 1
                    comp += 1
            acc += 1
        return comp, valc, acc
    
    @_perfDec
    def _cascRepair(self):
        vis = set()
        while self.repairs:
            _, curr = heapq.heappop(self.repairs)
            if curr not in vis:
                self.cache[curr] = float("inf")
                prev = self.cache[curr]
                for key, val in self.graph.graph[curr].items():
                    dist = self.cache[key] + val["w"]
                    if self.pred[key].prev != curr and dist < self.cache[curr]:
                        self._predSet(key, curr, val["w"])
            vis.add(curr)
                    
            if (prev != self.cache[curr]):
                for key, val in self.graph.graph[curr].items():
                    dist = self.cache[curr] + val["w"]
                    if self.pred[curr].prev != key and dist < self.cache[key]:
                            self._predSet(curr, key, val["w"])
                    if self.pred[key].prev == curr:
                        if key in vis: vis.remove(key)
                        self._predSet(curr, key, val["w"])
                        heapq.heappush(self.repairs, (dist, key))

    def _unlink(self, v):
        self.pred[v] = Pred(prev="", height=0, val=0)
        self.cache[v] = float("inf")
        heapq.heappush(self.repairs, (self.cache[v], v))
        for key, _ in self.pred.items():
            if (self.pred[key].prev == v):
                self._unlink(key) 

    def _cascMatch(self, e, op, w):
        u, v = e
        match op:
            case "add":
                if self.cache[u] + w >= self.cache[v]: return
                self._predSet(u,v,w)
                heapq.heappush(self.updates, (self.cache[v], v, u)) 
            case "rem":
                if self.pred[v].prev != u: return
                heapq.heappush(self.updates, (self.cache[u], u))
                self._unlink(v)
            case "mod":
                if self.pred[v].prev != u:
                    if self.cache[u] + w >= self.cache[v]: return
                    self._predSet(u,v,w)
                    heapq.heappush(self.updates, (self.cache[v], v))
                else:
                    if self.cache[u] + w <= self.cache[v]: 
                        self._predSet(u,v,w)
                        heapq.heappush(self.updates, (self.cache[v], v))
                        return
                    heapq.heappush(self.repairs, (self.cache[v], v))
            case _:
                print("error")
        return

    @_perfDec
    def cascade(self):
        self._cascRepair() # type: ignore
        comp, valc, acc = self._cascLoop() # type: ignore
        self.perf.inc("cascade",comp,valc,acc)
            

# Example usage
if __name__ == "__main__":
    # Create an instance of CascadeSP
    csp = CascadeSP()
    val = 1
    for i in range(val):
        os.system("clear")
        csp.clear()
        csp.gen(50)
        print("dijkstra...")
        csp.dijkstra(0)
        csp.plot()
        csp.perfClear()
        csp.randUpd(10, ["add", "mod","rem"])
        csp.plot("upd.png")
        print("cascade...")
        csp.cascade() # type: ignore
        csp.plot("casc.png")
        v1 = csp.cache
        print("dijkstra2...")
        csp.dijkstra(0)
        csp.plot("bench.png")
        v2 = csp.cache
        csp.show()
        print("RUN: ", i+1, "/", val)
        if (v1 != v2): 
            print("------------")
            print(v1)
            print(v2)
            print("------------")
            break