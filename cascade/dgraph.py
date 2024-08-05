import random
import networkx as nx
import matplotlib.pyplot as plt
from attrs import define, field, Factory as new
from typing import Dict, Any, Tuple
"""
Wrapper class for networkx graph

Import or generate graph using erdos_renyi; supports random or provided updates 
(see update() for formatting and expected output)
"""

@define
class DGraph:
    graph: nx.Graph = field(default=new(nx.Graph))
    pos: Dict[Any, Tuple[float, float]] = field(default=new(dict))

    def gen(self, n=10, p=0.5, seed=None):
        self.graph = nx.erdos_renyi_graph(n, p, seed=seed, directed=False)
        map = {i: str(i) for i in self.graph.nodes()}  # noqa: A001
        self.graph = nx.relabel_nodes(self.graph, map)
        for (u, v) in self.graph.edges():
            self.graph.edges[u, v]["w"] = random.randint(1, 10)

    def n(self) -> int:
        return self.graph.number_of_nodes()

    def m(self) -> int:
        return self.graph.number_of_edges()

    def getW(self, u, v):
        if not self.graph.has_edge(u, v): return float("inf")
        return self.graph.edges[u, v]["w"]

    def addVert(self, v):
        if self.graph.has_node(v): return False
        self.graph.add_node(v)
        return True

    def remVert(self, v):
        if not self.graph.has_node(v): return False
        self.graph.remove_node(v)
        return True

    def addEdge(self, u, v, w):
        if self.graph.has_edge(u, v) \
        or (not isinstance(w, int) and not isinstance(w,float)):
            return False
        self.graph.add_edge(u, v, w=w)
        return True

    def remEdge(self, u, v):
        if not self.graph.has_edge(u, v): return False
        self.graph.remove_edge(u, v)
        return True

    def modEdge(self, u, v, w):
        if not self.graph.has_edge(u, v) \
        or (not isinstance(w, int) and not isinstance(w, float)):
            return False
        self.graph.edges[u, v]["w"] = w
        return True

    def _gridLayout(self):
        pos = {}
        n = self.graph.number_of_nodes()
        _len = int(n**0.5) + 1
        for i, node in enumerate(sorted(self.graph.nodes())):
            pos[node] = (i % _len, -i // _len)
        return pos

    def _plotGraph(self, colors):
        self.pos = nx.kamada_kawai_layout(self.graph, self.pos)  # type: ignore
        labels = nx.get_edge_attributes(self.graph, "w")
        plt.figure(figsize=(10, 8))
        nx.draw(self.graph, self.pos, with_labels=True, node_color=colors, \
            node_size=500, font_size=10, font_weight="bold")
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels=labels)

    def _drawSP(self, source, pos, pred):
        if source:
            edges = [(pred[node].prev, node) for node in pred]
            edges = [e for e in edges if self.graph.has_edge(e[0], e[1])]
            nx.draw_networkx_edges(
                self.graph, pos, edgelist=edges, edge_color="r", width=2
            )

    def _colorUpdate(self, updates):
        nodes = set()
        for _, *val in updates:
            nodes.add(val[0])
        return ["red" if node in nodes else "lightblue" for node in self.graph.nodes]

    def plot(self, filename="graph.png", pred=None, updates=None):
        colors = ["lightblue"]*len(self.graph.nodes)
        if updates: colors = self._colorUpdate(updates)
        self._plotGraph(colors)
        if pred:
            source = None
            for node, data in pred.items():
                if data.prev == "":
                    source = node
                    break
            self._drawSP(source, self.pos, pred)
        plt.savefig("output/" + filename)
        plt.close()
        if pred: self.plot("graph.png")

    def _choose(self, inp, vis):
        key, val, opt = inp
        if len(opt) > 0: opt = opt[0]
        if key in vis: return False
        match val:
            case "add":
                if type(key) is tuple: ret = self.addEdge(key[0], key[1], opt)
                else: ret = self.addVert(key)
            case "rem":
                if type(key) is tuple: ret = self.remEdge(key[0], key[1])
                else: ret = self.remVert(key)
            case "mod":
                ret = self.modEdge(key[0], key[1], opt) if type(key) is tuple else False
            case _:
                ret = False
        vis.add(key)
        return ret

    # updates in form [('id', (op, weight=None)),...]
    # op = "add", "rem", "mod"
    def update(self, updates):
        vis = set()
        ret = []
        for (key, val, *opt) in updates:
            resp = self._choose((key, val, opt), vis)
            ret.append(resp)
        return ret

    def _randChoose(self, op, n, m):
        u, v = random.sample(n, 2)
        e = random.sample(m, 1)[0]
        w = random.randint(1, 10)
        match op:
            case "add":
                while self.graph.has_edge(u, v):
                    u, v = random.sample(n, 2)
            case "rem" | "mod":
                u, v = e
        return ((u, v), op, w)

    def randUpdate(self, N, opt=None):
        update = []
        n, m, i = list(self.graph.nodes()), list(self.graph.edges()), 0
        while i < N:
            op = random.choice(["add", "rem", "mod"])
            if opt: op = random.choice(opt)
            update.append(self._randChoose(op, n, m))
            i += 1
        return update

# Example usage:
if __name__ == "__main__":
    # Create a DGraph instance
    dgraph = DGraph()

    # Generate a random connected graph
    dgraph.gen(n=10, p=0.4)

    # Plot the graph
    dgraph.plot(filename="dgraph.png")

    # Add/Remove vertex or edge
    dgraph.addVert(10)
    dgraph.addEdge(10, 2, w=5)
    dgraph.modEdge(10, 2, w=7)
    dgraph.remEdge(10, 2)
    dgraph.remVert(10)

    # Perform random updates
    dgraph.randUpdate(5)

    # manual updates
    updates = [(11, "add"), ((1, 2), "mod", 5), ((2, 3), "rem"), ((3, 4), "mod"),
        ((3, 4), "mod", "bait")]
    ret = dgraph.update(updates)
    print(ret)

    # Plot the updated graph
    dgraph.plot(filename="dgraph_mod.png")
