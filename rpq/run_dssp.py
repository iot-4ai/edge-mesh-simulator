import random
import heapq
import time
import networkx as nx
import matplotlib.pyplot as plt
import os
import re
from sortedcontainers import SortedDict

class RPQ:

    def __init__(self):
        self.ins = SortedDict()  # (distance, vertex, time) -> True/False
        self.delmin = SortedDict()  # time -> (distance, vertex)
        self.current_time = 0

    def _genkey(self, distance, vertex, t):
        return (distance, vertex, t)

    def insert(self, item, t):
        distance, vertex = item
        if t >= self.current_time:
            key = self._genkey(distance, vertex, t)
            self.ins[key] = True
            self.current_time = max(self.current_time, t)
        else:
            key = self._genkey(distance, vertex, t)
            self.ins[key] = True
            for del_time in self.delmin:
                if del_time > t:
                    k = self.delmin[del_time]
                    return (k, del_time)
        return None

    def del_min(self, t):
        t_prime = max([time for time in self.delmin if time > t], default=None)
        if t_prime is not None:
            k = max([time for time in self.delmin if time < t], default=0)
            min_key = min([item for item in self.ins if item[2] > k and self.ins[item]],
                default=None)
        else:
            min_key = min([item for item in self.ins if self.ins[item]], default=None)
        if min_key is None:
            return None
        del_item = (min_key[0], min_key[1])
        self.delmin[t] = del_item
        self.ins[min_key] = False
        self.current_time = max(self.current_time, t)
        return del_item

    def print(self):
        print("Insert tree:")
        for k, v in self.ins.items():
            print(f"  {k}: {'valid' if v else 'invalid'}")
        print("Delmin tree:")
        for k, v in self.delmin.items():
            print(f"  {k}: {v}")

def plot_rpq(rpq, filename):
    fig, ax = plt.subplots()

    # Extract insertion and deletion times from the RPQ
    insertions = {key[1]: key[2] for key in rpq.ins}
    deletions = {v[1]: k for k, v in rpq.delmin.items()}
    tmp = {}
    item_mapping = {}
    for idx, item in enumerate(sorted(rpq.delmin.items())):
        tmp[item[1][1]] = idx
    sorted_entries = sorted(tmp.items(), key=lambda x: x[1])
    for idx, item in enumerate(sorted_entries):
        item_mapping[item[0]] = idx
    max_key = max(item_mapping.values()) + 1
    for key, _ in insertions.items():
        if key not in item_mapping:
            item_mapping[key] = max_key
            max_key += 1

    # Plot insertions and deletions as horizontal lines
    for item, insert_time in insertions.items():
        delete_time = deletions.get(item, rpq.current_time + 1)
        ax.hlines(item_mapping.get(item, 0), insert_time, delete_time, colors="blue")

    # Plot del_min calls as vertical lines
    for item, delete_time in deletions.items():
        ax.vlines(
            delete_time,
            ymin=item_mapping[item] - 1,
            ymax=item_mapping[item] + 1,
            colors="red"
        )

    ax.set_xlabel("Time")
    ax.set_ylabel("Item")
    ax.set_title("RPQ Operations")
    plt.savefig(filename)
    plt.close()

class Graph:

    def __init__(self, num_vertices):
        self.num_vertices = num_vertices
        self.adjacency_list = {i: [] for i in range(num_vertices)}

    def add_edge(self, u, v, weight):
        self.adjacency_list[u].append((v, weight))
        self.adjacency_list[v].append((u, weight))  # Undirected graph

    def remove_edge(self, u, v):
        self.adjacency_list[u] = [pair for pair in self.adjacency_list[u] if pair[0] != v]
        self.adjacency_list[v] = [pair for pair in self.adjacency_list[v] if pair[0] != u]

    def change_edge_weight(self, u, v, new_weight):
        for i, pair in enumerate(self.adjacency_list[u]):
            if pair[0] == v:
                self.adjacency_list[u][i] = (v, new_weight)
        for i, pair in enumerate(self.adjacency_list[v]):
            if pair[0] == u:
                self.adjacency_list[v][i] = (u, new_weight)

    def generate_random_graph(self, num_edges):
        edges_added = 0
        while edges_added < num_edges:
            u = random.randint(0, self.num_vertices - 1)
            v = random.randint(0, self.num_vertices - 1)
            if u != v:
                weight = random.randint(1, 10)
                if (v, weight) not in self.adjacency_list[u] and (u,
                    weight) not in self.adjacency_list[v]:
                    self.add_edge(u, v, weight)
                    edges_added += 1

    def ensure_connected(self):
        visited = [False]*self.num_vertices

        def dfs(v):
            visited[v] = True
            for neighbor, _ in self.adjacency_list[v]:
                if not visited[neighbor]:
                    dfs(neighbor)

        dfs(0)

        for i in range(self.num_vertices):
            if not visited[i]:
                self.add_edge(0, i, random.randint(1, 10))
                dfs(i)

    def create_random_connected_graph(self, num_edges):
        self.generate_random_graph(num_edges)
        self.ensure_connected()

    def print_graph(self):
        for key, value in self.adjacency_list.items():
            print(f"{key}: {value}")

    def to_networkx_graph(self):
        G = nx.Graph()
        for key, value in self.adjacency_list.items():
            for neighbor, weight in value:
                G.add_edge(key, neighbor, weight=weight)
        return G

    def plot_graph(self, file_name="graph.png", pos=None):
        G = self.to_networkx_graph()
        if pos is None:
            pos = nx.spring_layout(G, seed=42)  # Fixed layout
        edge_labels = nx.get_edge_attributes(G, "weight")
        plt.figure(figsize=(10, 8))
        nx.draw(
            G,
            pos,
            with_labels=True,
            node_color="lightblue",
            node_size=500,
            font_size=10,
            font_weight="bold"
        )
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        plt.savefig(file_name)
        plt.close()

    def modify_graph(self, N=5):
        modified_edges = set()
        i = 0
        while i < N:
            operation = random.choice(["add", "remove", "change"])
            u = random.randint(0, self.num_vertices - 1)
            v = random.randint(0, self.num_vertices - 1)
            while u == v:
                v = random.randint(0, self.num_vertices - 1)

            edge = (min(u, v), max(u, v))  # Use sorted tuple to ensure uniqueness

            if edge in modified_edges:
                continue

            if operation == "add":
                if not any(pair[0] == v for pair in self.adjacency_list[u]):
                    weight = random.randint(1, 10)
                    self.add_edge(u, v, weight)
                    modified_edges.add(edge)
                else:
                    i -= 1

            elif operation == "remove":
                if any(pair[0] == v for pair in self.adjacency_list[u]):
                    self.remove_edge(u, v)
                    modified_edges.add(edge)
                else:
                    i -= 1

            elif operation == "change":
                if any(pair[0] == v for pair in self.adjacency_list[u]):
                    new_weight = random.randint(1, 10)
                    self.change_edge_weight(u, v, new_weight)
                    modified_edges.add(edge)
                else:
                    i -= 1
            i += 1

class DijkstraPerformance:

    def __init__(self):
        self.comparisons = 0
        self.value_changes = 0
        self.execution_time = 0

    def dijkstra(self, graph, start_vertex, opt):
        self.comparisons = 0
        self.value_changes = 0
        self.execution_time = 0

        num_vertices = graph.num_vertices
        distances = {vertex: float("inf") for vertex in range(num_vertices)}
        distances[start_vertex] = 0

        priority_queue = RPQ()
        priority_queue.insert((0, start_vertex), 0)
        previous = {vertex: None for vertex in range(num_vertices)}
        visited = set()

        start_time = time.time()
        r_time = 0.0
        tmp = 0.0
        plot_counter = 1
        while True:
            min_entry = priority_queue.del_min(priority_queue.current_time + 1)
            if min_entry is None:
                break
            current_distance, current_vertex = min_entry
            visited.add(current_vertex)

            tmp = time.time()
            if opt: plot_rpq(priority_queue, f"{plot_counter}.png")
            plot_counter += 1
            r_time += time.time() - tmp

            for neighbor, weight in graph.adjacency_list[current_vertex]:
                if neighbor not in visited:
                    distance = current_distance + weight
                    self.comparisons += 1
                    if distance < distances[neighbor]:
                        self.value_changes += 1
                        distances[neighbor] = distance
                        previous[neighbor] = current_vertex
                        priority_queue.insert((distance, neighbor),
                            priority_queue.current_time)

        self.execution_time = time.time() - start_time - r_time

        return distances, previous, priority_queue

    def plot_shortest_paths(  # noqa: PLR0913
        self,
        graph,
        start_vertex,
        distances,
        previous,
        file_name="shortest_paths.png",
        pos=None
    ):
        G = graph.to_networkx_graph()
        if pos is None:
            pos = nx.spring_layout(G, seed=42)
        edge_labels = nx.get_edge_attributes(G, "weight")

        plt.figure(figsize=(10, 8))
        nx.draw(
            G,
            pos,
            with_labels=True,
            node_color="lightblue",
            node_size=500,
            font_size=10,
            font_weight="bold"
        )
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        for target_vertex in distances:
            if target_vertex != start_vertex and previous[target_vertex] is not None:
                path = []
                current_vertex = target_vertex
                while current_vertex is not None:
                    path.append(current_vertex)
                    current_vertex = previous[current_vertex]
                path.reverse()
                path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
                nx.draw_networkx_edges(
                    G, pos, edgelist=path_edges, edge_color="red", width=2
                )

        plt.savefig(file_name)
        plt.close()

    def modify_and_rerun(self, graph, start_vertex, pos, N=10):
        graph.modify_graph(N)
        distances, previous, pq = self.dijkstra(graph, start_vertex, True)
        pq.insert((2, 20), 0)
        pq.insert((2, 5), 0)
        pq.print()
        plot_rpq(pq, "pq.png")
        self.plot_shortest_paths(
            graph, start_vertex, distances, previous, "dsp_updated", pos=pos
        )

def test_dijkstra_performance():
    num_vertices = 10
    num_edges = 15
    graph = Graph(num_vertices)
    graph.create_random_connected_graph(num_edges)
    graph.plot_graph("graph.png")

    start_vertex = 0
    pos = None  # Use default positioning for networkx layout

    performance_tracker = DijkstraPerformance()
    distances, previous, pq = performance_tracker.dijkstra(graph, start_vertex, False)

    print("Comparisons:", performance_tracker.comparisons)
    print("Value Changes:", performance_tracker.value_changes)
    print("Execution Time:", performance_tracker.execution_time, "seconds")

    # Using the same layout for consistent positioning
    pos = nx.spring_layout(graph.to_networkx_graph(), seed=42)
    performance_tracker.plot_shortest_paths(
        graph, start_vertex, distances, previous, "dsp.png", pos
    )

    # Modify the graph and re-run Dijkstra's algorithm
    performance_tracker.modify_and_rerun(graph, start_vertex, pos)

    print("Comparisons:", performance_tracker.comparisons)
    print("Value Changes:", performance_tracker.value_changes)
    print("Execution Time:", performance_tracker.execution_time, "seconds")

def remove_numbered_png_files():
    # Get the current working directory
    cwd = os.getcwd()

    # Iterate over all files in the current directory
    for filename in os.listdir(cwd):
        # Check if the filename starts with a number and ends with .png
        if re.match(r"^\d+.*\.png$", filename):
            # Construct the full file path
            file_path = os.path.join(cwd, filename)
            # Remove the file
            os.remove(file_path)
            print(f"rm: {filename}")

remove_numbered_png_files()
test_dijkstra_performance()
