import csv
import random

# Load locations from CSV
def load_locations(file_path):
    locations = []
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            locations.append({
                "name": row["name"].lower(),  # Convert to lowercase for case-insensitive matching
                "speed_limit": int(row["speed_limit"]),
                "has_signal": row["has_signal"].lower() == "true"
            })
    return locations

# Display 5 random example locations
def display_random_locations(locations):
    print("\nExample Locations:")
    random_locations = random.sample(locations, min(5, len(locations)))
    for loc in random_locations:
        print(f"{loc['name'].title()} (Speed Limit: {loc['speed_limit']} km/h, Signal: {loc['has_signal']})")

# Prompt user for vehicle data
def get_vehicle_data(locations):

    location_name = input("\nEnter location name: ").strip().lower()
    location = next((loc for loc in locations if loc["name"] == location_name), None)

    if not location:
        print("Invalid location name. Try again.")
        return get_vehicle_data(locations)

    speed = int(input(f"Enter vehicle speed at {location['name'].title()}: "))
    signal_status = None
    if location["has_signal"]:
        signal_status = input("Enter signal status (red/green): ").strip().lower()

    return {
        "location": location,
        "speed": speed,
        "signal_status": signal_status
    }

# Validate vehicle data
def validate_vehicle_input(vehicle):
    location = vehicle["location"]
    violations = []

    # Rule 1: Speed limit violation
    if vehicle["speed"] > location["speed_limit"]:
        violations.append(f"Speeding violation at {location['name'].title()}. Speed: {vehicle['speed']} km/h, Limit: {location['speed_limit']} km/h")

    # Rule 2: Signal violation
    if location["has_signal"] and vehicle["signal_status"] == "red" and vehicle["speed"] > 0:
        violations.append(f"Red light violation at {location['name'].title()}.")

    return violations

# Main function
def main():
    locations = load_locations("./data/q2-location.csv")
    print("Traffic Rule Violation Detection System")

    display_random_locations(locations)  # Show example locations

    while True:
        example_locations = display_random_locations(locations)
        vehicle = get_vehicle_data(locations)
        violations = validate_vehicle_input(vehicle)
        print("\nViolations Detected:")
        if violations:
            for violation in violations:
                print(f"- {violation}")
        else:
            print("No violations detected.")
        
        if input("\nCheck another vehicle? (yes/no): ").lower() != "yes":
            break

if __name__ == "__main__":
    main()

