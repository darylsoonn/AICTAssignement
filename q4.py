import numpy as np
import random
import heapq  # For Dijkstra's algorithm

traffic_network = {
    "A": {"B": {"time": 5, "capacity": 2}, "C": {"time": 10, "capacity": 3}},
    "B": {"A": {"time": 5, "capacity": 2}, "D": {"time": 15, "capacity": 2}},
    "C": {"A": {"time": 10, "capacity": 3}, "D": {"time": 20, "capacity": 1}},
    "D": {"B": {"time": 15, "capacity": 2}, "C": {"time": 20, "capacity": 1}}
}

vehicles = [
    {"start": "A", "end": "D", "time_window": (0, 30)},
    {"start": "B", "end": "C", "time_window": (0, 25)},
    {"start": "C", "end": "A", "time_window": (0, 35)}
]

def dijkstra(network, start, end):
    """Finds the shortest path using Dijkstra's Algorithm."""
    pq = [(0, start, [])]  
    visited = set()

    while pq:
        (cost, node, path) = heapq.heappop(pq)
        if node in visited:
            continue
        path = path + [node]
        visited.add(node)

        if node == end:
            return path

        for neighbor in network[node]:
            if neighbor not in visited:
                heapq.heappush(pq, (cost + network[node][neighbor]["time"], neighbor, path))

    return None  # No valid path

def generate_valid_routes(vehicles, network):
    """Generates valid initial routes using shortest paths."""
    routes = []
    for vehicle in vehicles:
        route = dijkstra(network, vehicle["start"], vehicle["end"])
        if route is None:
            print(f"⚠️ No valid path found for vehicle from {vehicle['start']} to {vehicle['end']}.")
        else:
            routes.append(route)
    return routes

def calculate_total_time(routes, network):
    """Calculates total travel time while enforcing capacity constraints."""
    total_time = 0
    road_usage = {}

    for i, route in enumerate(routes):
        vehicle_time = 0
        for j in range(len(route) - 1):
            start, end = route[j], route[j + 1]

            if end in network[start]:
                travel_time = network[start][end]["time"]
                max_capacity = network[start][end]["capacity"]

                road_key = tuple(sorted([start, end]))
                road_usage[road_key] = road_usage.get(road_key, 0) + 1

                if road_usage[road_key] > max_capacity:
                    print(f"⚠️ Road {start} -> {end} is over capacity!")
                    return float("inf")

                vehicle_time += travel_time
            else:
                print(f"⚠️ Invalid route: {start} -> {end}")
                return float("inf")

        start_time, max_time = vehicles[i]["time_window"]
        if not (start_time <= vehicle_time <= max_time):
            print(f"⚠️ Vehicle {i + 1} exceeds time window ({start_time}, {max_time})")
            return float("inf")

        total_time += vehicle_time
    return total_time

def simulated_annealing(vehicles, network, initial_temp=100, cooling_rate=0.95, max_iterations=1000):
    """Optimizes routes using Simulated Annealing."""
    current_routes = generate_valid_routes(vehicles, network)
    current_cost = calculate_total_time(current_routes, network)

    if current_cost == float("inf"):
        print("🚨 No valid initial routes found!")
        return None, float("inf")

    best_routes, best_cost = current_routes, current_cost
    temp = initial_temp

    for iteration in range(max_iterations):
        new_routes = [route[:] for route in current_routes]
        
        for route in new_routes:
            if len(route) > 3:  # Ensure there are at least two nodes to swap
                idx1, idx2 = sorted(random.sample(range(1, len(route) - 1), 2))
                route[idx1], route[idx2] = route[idx2], route[idx1]

        new_cost = calculate_total_time(new_routes, network)

        if new_cost < current_cost or random.uniform(0, 1) < np.exp((current_cost - new_cost) / temp):
            current_routes, current_cost = new_routes, new_cost

            if new_cost < best_cost:
                best_routes, best_cost = new_routes, new_cost

        temp *= cooling_rate
        if temp < 1e-3:
            break

    return best_routes, best_cost


def baseline_performance(vehicles, network):
    """Calculates baseline performance by taking direct routes."""
    total_time = 0
    routes = []
    for vehicle in vehicles:
        start, end = vehicle["start"], vehicle["end"]
        route = dijkstra(network, start, end)  
        if route:
            routes.append(route)
            total_time += sum(network[route[i]][route[i+1]]["time"] for i in range(len(route) - 1))
        else:
            total_time = float("inf")
    return routes, total_time

baseline_routes, baseline_time = baseline_performance(vehicles, traffic_network)
optimized_routes, optimized_time = simulated_annealing(vehicles, traffic_network)

print("\n🔹 **Baseline Routes & Travel Time:**")
for i, route in enumerate(baseline_routes):
    print(f"Vehicle {i + 1}: Route: {' -> '.join(route)}")
print(f"Total Baseline Travel Time: {baseline_time}")

print("\n🚀 **Optimized Routes & Travel Time:**")
if optimized_routes:
    for i, route in enumerate(optimized_routes):
        print(f"Vehicle {i + 1}: Route: {' -> '.join(route)}")
    print(f"Total Optimized Travel Time: {optimized_time}")

improvement = ((baseline_time - optimized_time) / baseline_time) * 100 if baseline_time > 0 else 0
print(f"\n📊 **Performance Improvement: {improvement:.2f}%**")
