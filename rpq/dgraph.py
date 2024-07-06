import random
import networkx as nx
import matplotlib.pyplot as plt
from attrs import define, field, Factory as new

@define
class DGraph:
    graph: nx.Graph = field(default=new(nx.Graph))

    def gen(self, n=10, p=0.5, seed=None):
        self.graph = nx.erdos_renyi_graph(n, p, seed=seed, directed=False)
        for (u, v) in self.graph.edges():
            self.graph.edges[u, v]["w"] = random.randint(1, 10)

    def n(self) -> int:
        return self.graph.number_of_nodes()

    def m(self) -> int:
        return self.graph.number_of_edges()

    def add_vert(self, v):
        if self.graph.has_node(v): return False
        self.graph.add_node(v)
        return True

    def rem_vert(self, v):
        if not self.graph.has_node(v): return False
        self.graph.remove_node(v)
        return True

    def add_edge(self, u, v, w=1):
        if self.graph.has_edge(u, v) or not isinstance(w, int): return False
        self.graph.add_edge(u, v, w=w)
        return True

    def rem_edge(self, u, v):
        if not self.graph.has_edge(u, v): return False
        self.graph.remove_edge(u, v)
        return True

    def mod_edge(self, u, v, w):
        if not self.graph.has_edge(u, v) or not isinstance(w, int): return False
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

    def rand_upd(self, N):
        n, m, i = list(self.graph.nodes()), list(self.graph.edges()), 0
        while i < N:
            op = random.choice(["add", "rem", "mod"])
            match op:
                case "add":
                    u, v = random.sample(n, 2)
                    if not self.add_edge(u, v, w=random.randint(1, 10)): continue
                case "rem":
                    e = random.sample(m, 1)[0]
                    if not self.rem_edge(e[0], e[1]): continue
                case "mod":
                    e = random.sample(m, 1)[0]
                    if not self.mod_edge(e[0], e[1], w=random.randint(1, 10)): continue
                case _:
                    continue
            i += 1

    # updates in form [('id', (op, weight=None)),...]
    # op = "addv", "adde", "remv", "reme", "mod"
    def upd(self, updates):
        ret = []
        for (key, val, *opt) in updates:
            match val:
                case "add":
                    if type(key) is tuple: resp = self.add_edge(key[0], key[1])
                    resp = self.add_vert(key)
                case "remv":
                    if type(key) is tuple: resp = self.rem_edge(key[0], key[1])
                    resp = self.rem_vert(key)
                case "mod":
                    if type(key) is tuple: resp = self.mod_edge(key[0], key[1], opt)
                    resp = False
                case _:
                    resp = False
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
    dgraph.add_vert(10)
    dgraph.add_edge(10, 2, w=5)
    dgraph.mod_edge(10, 2, w=7)
    dgraph.rem_edge(10, 2)
    dgraph.rem_vert(10)

    # Perform random updates
    dgraph.rand_upd(5)

    # manual updates
    upd = [(11, "add"), ((1, 2), "mod", 5), ((2, 3), "rem"), ((3, 4), "mod"),
        ((3, 4), "mod", "bait")]
    ret = dgraph.upd(upd)
    print(ret)

    # Plot the updated graph
    dgraph.plot(filename="dgraph_mod.png")
