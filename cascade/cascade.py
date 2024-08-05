import functools
from typing import Callable, Dict, List
import os
import heapq
from dataclasses import dataclass
from dgraph import DGraph
from attrs import define, field, Factory as new
import pickle
import random
from perf import PerfEval
"""
Cascade shortest path implementation; supports importing or randomly generating graph
(see dgraph.py for options)

Dynamically updates graph representation and computes new shortest path tree as 
both cache and predecessor tree (self.cache, self.pred). 
"""
type SP_MAP[T] = Dict[str, T]
@dataclass
class Pred:
    prev: str
    height: int
    val: float

@define
class Cascade:
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

    def plot(self, file="sp.png"):
        self.graph.plot(file, pred=self.pred, updates=self.updates)

    def gen(self, n=10, p=0.5, seed=None):
        self.graph.gen(n,p,seed)
    
    def print(self):
        print(self.pred)
        print(self.cache)

    def clear(self):
        self.updates = []; self.pred = {}; self.cache = {}

    def load(self, graph):
        self.graph = graph

    def read(self, file):
        self.graph = pickle.load(open(file, "rb"))  # noqa: SIM115

    def write(self, file="data.pickle"):
        pickle.dump(self.graph, open(file, "wb"))  # noqa: SIM115

    def _predSet(self, u, v, w):
        self.cache[v] = self.cache[u] + w 
        self.pred[v].height = self.pred[u].height + 1
        self.pred[v].prev = u
        self.pred[v].val = w

    def _propSP(self, pq, v, _dist, vis, comp, chg, acc):  # noqa: PLR0913
        for key, val in self.graph.graph[v].items():
            if key not in vis:
                dist = _dist + val["w"]
                if dist < self.cache[key]:
                    self._predSet(v, key, val["w"])
                    heapq.heappush(pq, (dist, key))
                    chg += 1
                comp += 1
        acc += 1

    def _loopSP(self, pq, vis):
        comp = chg = acc = 0
        while pq:
            dist, vertex = heapq.heappop(pq)
            if vertex in vis: continue
            vis.add(vertex)
            self._propSP(pq, vertex, dist, vis, comp, chg, acc)
        return comp, chg, acc

    @_perfDec
    def dijkstra(self, v):
        self.clear()
        n, v = self.graph.n(), str(v)
        self.pred = {str(v): Pred(prev="", height=0, val=0) for v in range(n)}
        self.cache = {str(v): float("inf") for v in range(n)}
        self.cache[v] = 0.0
        pq = []; vis = set()
        heapq.heappush(pq, (0, v))   
        comp, chg, acc = self._loopSP(pq, vis)
        self.perf.inc("dijkstra", comp,chg,acc)

    def _propCasc(self, v, vis):
        for key, val in self.graph.graph[v].items():
            dist = self.cache[v] + val["w"]
            if self.pred[v].prev != key and dist < self.cache[key]:
                    self._predSet(v, key, val["w"])
            if self.pred[key].prev == v:
                if key in vis: vis.remove(key)
                self._predSet(v, key, val["w"])
                heapq.heappush(self.repairs, (dist, key))
    
    def _loopCasc(self):
        vis = set()
        comp = chg = acc = 0
        while self.updates:
            dist, vertex = heapq.heappop(self.updates)
            if vertex in vis: continue
            if dist != self.cache[vertex]:
                dist = self.cache[vertex]
                heapq.heappush(self.updates, (dist, vertex))
                continue
            vis.add(vertex)
            self._propSP(self.updates, vertex, dist, vis, comp, chg, acc)
        return comp, chg, acc
    
    def _fix(self, v):
        self.cache[v] = float("inf")
        prev = self.cache[v]
        for key, val in self.graph.graph[v].items():
            dist = self.cache[key] + val["w"]
            if self.pred[key].prev != v and dist < self.cache[v]:
                self._predSet(key, v, val["w"])
        return prev

    def _repair(self):
        vis = set()
        while self.repairs:
            _, vertex = heapq.heappop(self.repairs)
            if vertex not in vis: prev = self._fix(vertex)
            vis.add(vertex)
                    
            if (prev != self.cache[vertex]):
                self._propCasc(vertex,vis)

    def _unlink(self, v):
        self.pred[v] = Pred(prev="", height=0, val=0)
        self.cache[v] = float("inf")
        heapq.heappush(self.repairs, (self.cache[v], v))
        for key, _ in self.pred.items():
            if (self.pred[key].prev == v):
                self._unlink(key) 

    def _add(self, u, v, w):
        if self.cache[u] + w >= self.cache[v]: return
        self._predSet(u,v,w)
        heapq.heappush(self.updates, (self.cache[v], v)) 

    def _rem(self, u,v):
        if self.pred[v].prev != u: return
        heapq.heappush(self.updates, (self.cache[u], u))
        self._unlink(v)
    
    def _mod(self, u, v, w):
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

    def _match(self, e, op, w):
        u, v = e
        match op:
            case "add": self._add(u,v,w)
            case "rem": self._rem(u,v)
            case "mod": self._mod(u,v,w)
            case _: print("error")

    # updates in form [('id', (op, weight=None)),...]
    # op = "add", "rem", "mod"
    @_perfDec
    def update(self, updates):
        ret = self.graph.update(updates)
        updates = [update for update, ret in zip(updates, ret) if ret]
        for update in updates:
            u = min(update[0][0],update[0][1], key=lambda x: self.cache[x])
            v = update[0][0] if u == update[0][1] else update[0][1]
            self._match((u,v), update[1], update[2])
        return ret

    def randUpdate(self, N, opt=None):
        updates = self.graph.randUpdate(N, opt)
        return self.update(updates)

    @_perfDec
    def cascade(self):
        self._repair() # type: ignore
        comp, chg, acc = self._loopCasc() # type: ignore
        self.perf.inc("cascade",comp,chg,acc)
            

# Example usage
if __name__ == "__main__":
    # Create an instance of Cascade
    c = Cascade()
    val = 100
    for i in range(val):
        random.seed(i)
        os.system("clear")
        c.clear()
        c.gen(seed=i)
        c.dijkstra(0)
        c.perfClear()
        c.randUpdate(10, ["add", "mod","rem"])
        c.cascade() # type: ignore
        v1 = c.cache
        c.dijkstra(0)
        v2 = c.cache
        c.show()
        print("RUN: ", i+1, "/", val)
        if (v1 != v2): 
            print("------------")
            print(v1)
            print(v2)
            print("------------")
            break