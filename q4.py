import numpy as np
import random

traffic_network = {
    "A": {"B": 5, "C": 10},
    "B": {"A": 5, "D": 15},
    "C": {"A": 10, "D": 20},
    "D": {"B": 15, "C": 20}
}

vehicles = [
    {"start": "A", "end": "D"},
    {"start": "B", "end": "C"},
    {"start": "C", "end": "A"}
]

def calculate_total_time(routes, network):
    total_time = 0
    for route in routes:
        route_time = 0
        for i in range(len(route) - 1):
            start, end = route[i], route[i + 1]
            if end in network[start]:
                route_time += network[start][end]
            else:
                return float("inf")  
        total_time += route_time
    return total_time

def generate_initial_routes(vehicles, network):
    routes = []
    for vehicle in vehicles:
        nodes = list(network.keys())
        route = [vehicle["start"]] + random.sample(nodes, len(nodes)) + [vehicle["end"]]
        routes.append(route)
    return routes

def simulated_annealing(vehicles, network, initial_temp=100, cooling_rate=0.95, max_iterations=1000):
    current_routes = generate_initial_routes(vehicles, network)
    current_cost = calculate_total_time(current_routes, network)
    best_routes = current_routes
    best_cost = current_cost
    temp = initial_temp

    for iteration in range(max_iterations):
        new_routes = [route[:] for route in current_routes]
        for route in new_routes:
            if len(route) > 2:
                idx1, idx2 = random.sample(range(1, len(route) - 1), 2)
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

optimized_routes, optimized_time = simulated_annealing(vehicles, traffic_network)

print("Optimized Routes and Total Travel Time:")
for i, route in enumerate(optimized_routes):
    print(f"Vehicle {i + 1}: Route: {' -> '.join(route)}")
print(f"Total Optimized Travel Time: {optimized_time}")
