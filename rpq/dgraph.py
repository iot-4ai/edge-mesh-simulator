import random
import networkx as nx
import matplotlib.pyplot as plt
from attrs import define, field, Factory as new

@define
class DGraph:
    graph: nx.Graph = field(default=new(nx.Graph))

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

    def plot(self, filename="graph.png", pos=None):
        if pos is None: pos = nx.spring_layout(self.graph, seed=11)
        labels = nx.get_edge_attributes(self.graph, "w")
        plt.figure(figsize=(10, 8))
        nx.draw(self.graph, pos, with_labels=True, node_color="lightblue", \
            node_size=500, font_size=10, font_weight="bold")
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=labels)
        plt.savefig("output/" + filename)
        plt.close()

    def _randChoose(self, op, n, m):
        match op:
            case "add":
                u, v = random.sample(n, 2)
                return self.addEdge(u, v, w=random.randint(1, 10))
            case "rem":
                e = random.sample(m, 1)[0]
                return self.remEdge(e[0], e[1])
            case "mod":
                e = random.sample(m, 1)[0]
                return self.modEdge(e[0], e[1], w=random.randint(1, 10))
            case _:
                return False

    def randUpd(self, N):
        n, m, i = list(self.graph.nodes()), list(self.graph.edges()), 0
        while i < N:
            op = random.choice(["add", "rem", "mod"])
            if not self._randChoose(op, n, m): continue
            i += 1

    def _choose(self, inp):
        key, val, opt = inp
        match val:
            case "add":
                if type(key) is tuple: ret = self.addEdge(key[0], key[1], opt)
                else: ret = self.addVert(key)
            case "remv":
                if type(key) is tuple: ret = self.remEdge(key[0], key[1])
                else: ret = self.remVert(key)
            case "mod":
                ret = self.modEdge(key[0], key[1], opt) if type(key) is tuple else False
            case _:
                ret = False
        return ret

    # updates in form [('id', (op, weight=None)),...]
    # op = "add", "rem", "mod"
    def upd(self, updates):
        ret = []
        for (key, val, *opt) in updates:
            resp = self._choose((key, val, opt))
            ret.append(resp)
        return ret

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
    dgraph.randUpd(5)

    # manual updates
    upd = [(11, "add"), ((1, 2), "mod", 5), ((2, 3), "rem"), ((3, 4), "mod"),
        ((3, 4), "mod", "bait")]
    ret = dgraph.upd(upd)
    print(ret)

    # Plot the updated graph
    dgraph.plot(filename="dgraph_mod.png")
