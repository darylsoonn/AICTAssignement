import osmnx as ox
import networkx as nx
from heapq import heappush, heappop
import time
from math import sqrt
import folium
from pyproj import Transformer
from geopy.geocoders import Nominatim

# Initialize the geocoder
geolocator = Nominatim(user_agent="route_planner")

def get_coordinates(location_name):
    """
    Convert a location name or postal code to latitude and longitude.
    """
    location = geolocator.geocode(location_name, exactly_one=True)
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError(f"Location '{location_name}' could not be geocoded.")

# Download the street network for a city
city_name = "Singapore"
G = ox.graph_from_place(city_name, network_type="drive")  # Load a drivable street network
G = ox.add_edge_speeds(G)  # Add speed data
G = ox.add_edge_travel_times(G)  # Add travel time data

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
def dfs_shortest_path(graph, start, goal):
    stack = [(start, [start])]
    visited = set()

    while stack:
        current, path = stack.pop()
        if current == goal:
            return path
        if current not in visited:
            visited.add(current)
            for neighbor in graph.neighbors(current):
                if neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))

    return None  # No path found

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
    queue = [(0, 0, start, [start])]
    while queue:
        _, cost, current, path = heappop(queue)
        if current == goal:
            return path
        visited.add(current)
        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                edge_data = min(graph.get_edge_data(current, neighbor).values(), key=lambda x: x.get("travel_time", float('inf')))
                edge_cost = edge_data["travel_time"]
                total_cost = cost + edge_cost
                priority = total_cost + heuristic(graph, neighbor, goal)
                heappush(queue, (priority, total_cost, neighbor, path + [neighbor]))

def euclidean_heuristic(graph, node, goal):
    x1, y1 = graph.nodes[node]["x"], graph.nodes[node]["y"]
    x2, y2 = graph.nodes[goal]["x"], graph.nodes[goal]["y"]
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

# Input start and goal locations
start_location = "Yew Tee MRT Station, Singapore"
goal_location = "Changi Airport, Singapore"

try:
    start_latlon = get_coordinates(start_location)
    goal_latlon = get_coordinates(goal_location)
    print(f"Start Location: {start_location}, Coordinates: {start_latlon}")
    print(f"Goal Location: {goal_location}, Coordinates: {goal_latlon}")
    start_node = ox.distance.nearest_nodes(G, X=start_latlon[1], Y=start_latlon[0])
    goal_node = ox.distance.nearest_nodes(G, X=goal_latlon[1], Y=goal_latlon[0])
except ValueError as e:
    print(e)
    exit()

if start_node == goal_node:
    print("Start and Goal nodes are the same. Searching alternative nearest nodes...")
    goal_node = list(G.neighbors(start_node))[0]

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
        path_length = sum(min(G[current][neighbor].values(), key=lambda x: x.get("travel_time", float('inf')))["travel_time"] for current, neighbor in zip(path[:-1], path[1:]))
        print(f"{name}:\n  Runtime: {end_time - start_time:.4f} seconds\n  Path Length: {path_length:.2f} seconds\n  Path: {path}\n")
    else:
        print(f"{name}: No path found.\n")

route = astar_shortest_path(G, start_node, goal_node, euclidean_heuristic)
route_coords = [(G.nodes[node]["y"], G.nodes[node]["x"]) for node in route]
route_map = folium.Map(location=route_coords[0], zoom_start=12)
folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.8).add_to(route_map)
route_map.save("route_map.html")
print("Route map saved as 'route_map.html'. Open this file in a browser to view the route.")
