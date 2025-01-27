import osmnx as ox
import networkx as nx
from heapq import heappush, heappop
import time
from math import sqrt
import folium
from pyproj import Proj, transform  # For converting UTM back to lat/lon

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

# Check if both start and goal nodes are the same and adjust if necessary
if start_node == goal_node:
    print("Start and Goal nodes are the same. Adjusting the goal node.")
    goal_node = list(G.neighbors(start_node))[0]  # Just select the first neighbor as a fallback

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

    if path:
        # Calculate path length manually
        path_length = sum(G[current][neighbor][0]["length"] for current, neighbor in zip(path[:-1], path[1:]))
        print(f"{name}:")
        print(f"  Runtime: {end_time - start_time:.4f} seconds")
        print(f"  Path Length: {path_length:.2f} meters")
        print(f"  Path: {path}\n")
    else:
        print(f"{name}: No path found.\n")


# Convert UTM coordinates back to lat/lon for visualization
def utm_to_latlon(utm_x, utm_y, crs):
    utm_proj = Proj(init=crs)  # Use the correct UTM zone for your graph
    lon, lat = utm_proj(utm_x, utm_y, inverse=True)
    return lat, lon


# Visualize the path using Folium
# Here, we will use the A* route as an example, but you can use any path returned by the algorithm
route = astar_shortest_path(G, start_node, goal_node, euclidean_heuristic)

# Get the coordinates for the nodes in the route
route_coords = []
for node in route:
    # Convert UTM to latitude/longitude before plotting
    node_coords = (G.nodes[node]["y"], G.nodes[node]["x"])  # UTM coordinates
    lat, lon = utm_to_latlon(node_coords[0], node_coords[1], "epsg:32618")  # Make sure the correct UTM CRS is used
    route_coords.append((lat, lon))

# Create a folium map centered at the start node
route_map = folium.Map(location=route_coords[0], zoom_start=14)

# Add the route as a polyline
folium.PolyLine(route_coords, color="red", weight=5, opacity=0.8).add_to(route_map)

# Save the map to an HTML file
route_map.save("route_map.html")

print("Route map saved as 'route_map.html'. Open this file in a browser to view the route.")

# Debugging: Check neighbors and coordinates of the nodes
print(f"Start Node: {start_node}")
print(f"Goal Node: {goal_node}")
print(f"Start coordinates: {start_latlon}, Start Node: {start_node}")
print(f"Goal coordinates: {goal_latlon}, Goal Node: {goal_node}")
print(f"Path: {path}")
ox.plot_graph(G)

# Debugging: Check neighbors and coordinates of the nodes
print("Start Node Neighbors:", list(G.neighbors(start_node)))
print("Goal Node Neighbors:", list(G.neighbors(goal_node)))

start_node_coords = (G.nodes[start_node]["y"], G.nodes[start_node]["x"])
goal_node_coords = (G.nodes[goal_node]["y"], G.nodes[goal_node]["x"])

print(f"Start Node Coordinates: {start_node_coords}")
print(f"Goal Node Coordinates: {goal_node_coords}")
