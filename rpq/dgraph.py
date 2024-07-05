import random
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from attrs import define, field, Factory as new

@define
class DGraph:
    graph: nx.Graph = field(default=new(nx.Graph))

    def gen(self, n=10, p=0.5, seed=101):
        self.graph = nx.erdos_renyi_graph(n, p, seed=seed, directed=False)
        for (u, v) in self.graph.edges():
            self.graph.edges[u, v]["w"] = random.randint(1, 10)

    def n(self) -> int:
        return self.graph.number_of_nodes()

    def m(self) -> int:
        return self.graph.number_of_edges()

    def add_vert(self, v):
        if not self.graph.has_node(v): self.graph.add_node(v)

    def rem_vert(self, v):
        if self.graph.has_node(v): self.graph.remove_node(v)

    def add_edge(self, u, v, w=1):
        if not self.graph.has_edge(u, v): self.graph.add_edge(u, v, w=w)

    def rem_edge(self, u, v):
        if self.graph.has_edge(u, v): self.graph.remove_edge(u, v)

    def mod_edge(self, u, v, w):
        if self.graph.has_edge(u, v): self.graph.edges[u, v]["w"] = w

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
                    if self.graph.has_edge(u, v): continue
                    self.add_edge(u, v, w=random.randint(1, 10))
                case "rem":
                    if self.graph.number_of_edges == 0: continue
                    e = random.sample(m, 1)[0]
                    self.rem_edge(e[0], e[1])
                case "mod":
                    if self.graph.number_of_edges == 0: continue
                    e = random.sample(m, 1)[0]
                    self.graph.edges[e[0], e[1]]["w"] = random.randint(1, 10)
                case _:
                    continue
            i += 1

# Example usage:
if __name__ == "__main__":
    # Create a DGraph instance
    dgraph = DGraph()

    # Generate a random connected graph
    dgraph.gen(n=10, p=0.4, seed=42)

    # Print number of nodes and edges
    print(f"Number of nodes: {dgraph.n()}")
    print(f"Number of edges: {dgraph.m()}")

    # Plot the graph
    dgraph.plot(filename="graph.png")

    # Add/Remove vertex or edge
    dgraph.add_vert(10)
    dgraph.add_edge(10, 2, w=5)
    dgraph.mod_edge(10, 2, w=7)
    dgraph.rem_edge(10, 2)
    dgraph.rem_vert(10)

    # Perform random updates
    dgraph.rand_upd(5)

    # Plot the updated graph
    dgraph.plot(filename="updated_graph.png")
