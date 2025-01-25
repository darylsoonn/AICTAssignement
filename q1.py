import osmnx as ox
import networkx as nx
from heapq import heappush, heappop
import time
from math import sqrt


# Download the street network for a city
city_name = "Manhattan, New York, USA"
G = ox.graph_from_place(city_name, network_type="drive")  # Load a drivable street network

# Project the graph to UTM (for more accurate distance calculations)
G = ox.project_graph(G)

# BFS implementation
def bfs_shortest_path(graph, start, goal):
    visited = set()
    queue = [(start, [start])]

    while queue:
        current, path = queue.pop(0)
        if current == goal:
            return path
        visited.add(current)
        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))


# DFS implementation
def dfs_shortest_path(graph, start, goal, path=None, visited=None):
    if path is None:
        path = [start]
    if visited is None:
        visited = set()
    
    visited.add(start)
    if start == goal:
        return path

    for neighbor in graph.neighbors(start):
        if neighbor not in visited:
            result = dfs_shortest_path(graph, neighbor, goal, path + [neighbor], visited)
            if result:
                return result


# Greedy Best-First Search (GBFS)
def gbfs_shortest_path(graph, start, goal, heuristic):
    visited = set()
    queue = [(0, start, [start])]

    while queue:
        _, current, path = heappop(queue)
        if current == goal:
            return path
        visited.add(current)
        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                heappush(queue, (heuristic(graph, neighbor, goal), neighbor, path + [neighbor]))


# A* Search
def astar_shortest_path(graph, start, goal, heuristic):
    visited = set()
    queue = [(0, 0, start, [start])]  # (priority, cost, node, path)

    while queue:
        _, cost, current, path = heappop(queue)
        if current == goal:
            return path
        visited.add(current)
        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                edge_data = graph.get_edge_data(current, neighbor)[0]
                edge_cost = edge_data["length"]
                total_cost = cost + edge_cost
                priority = total_cost + heuristic(graph, neighbor, goal)
                heappush(queue, (priority, total_cost, neighbor, path + [neighbor]))

def euclidean_heuristic(graph, node, goal):
    x1, y1 = graph.nodes[node]["x"], graph.nodes[node]["y"]
    x2, y2 = graph.nodes[goal]["x"], graph.nodes[goal]["y"]
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

# Specify start and goal coordinates (latitude, longitude)
start_latlon = (40.748817, -73.985428)  # Example: Empire State Building
goal_latlon = (40.730610, -73.935242)  # Example: Brooklyn

# Get the nearest graph nodes
start_node = ox.distance.nearest_nodes(G, X=start_latlon[1], Y=start_latlon[0])
goal_node = ox.distance.nearest_nodes(G, X=goal_latlon[1], Y=goal_latlon[0])


# Evaluate algorithms
algorithms = {
    "BFS": bfs_shortest_path,
    "DFS": dfs_shortest_path,
    "GBFS": lambda g, s, g_: gbfs_shortest_path(g, s, g_, euclidean_heuristic),
    "A*": lambda g, s, g_: astar_shortest_path(g, s, g_, euclidean_heuristic),
}

for name, algorithm in algorithms.items():
    start_time = time.time()
    path = algorithm(G, start_node, goal_node)
    end_time = time.time()
    path_length = sum(ox.utils_graph.get_route_edge_attributes(G, path, "length"))
    
    print(f"{name}:")
    print(f"  Runtime: {end_time - start_time:.4f} seconds")
    print(f"  Path Length: {path_length:.2f} meters")
    print(f"  Path: {path}\n")


# Visualize the path
route = astar_shortest_path(G, start_node, goal_node, euclidean_heuristic)
ox.plot_route_folium(G, route, route_color="red", route_linewidth=5)
