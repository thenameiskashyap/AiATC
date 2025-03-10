"""
Breadth-First Search (BFS): Airport Network Exploration

Narrative: An air traffic controller must identify the shortest path for flights 
between connected airports while avoiding congested airspaces.

Challenge features:
- Accounts for dynamic changes in available routes due to weather or maintenance
- Handles scenarios where multiple airports serve as hubs
- Extension: Includes constraints like prioritizing fuel-efficient routes
"""

import heapq
from collections import deque
import random

class Airport:
    def __init__(self, code, name, is_hub=False, facilities=None):
        self.code = code
        self.name = name
        self.is_hub = is_hub
        self.facilities = facilities or []
    
    def __str__(self):
        hub_status = "HUB" if self.is_hub else ""
        return f"{self.code}: {self.name} {hub_status}"

class AirportNetwork:
    def __init__(self):
        self.airports = {}  # code -> Airport object
        self.routes = {}    # code -> list of (destination_code, distance, fuel_efficiency, congestion)
        self.congested_routes = set()  # set of (origin, destination) tuples that are congested
        self.weather_affected_routes = set()  # set of (origin, destination) tuples affected by weather
    
    def add_airport(self, airport):
        """Add an airport to the network"""
        self.airports[airport.code] = airport
        if airport.code not in self.routes:
            self.routes[airport.code] = []
    
    def add_route(self, origin, destination, distance, fuel_efficiency=5):
        """Add a bidirectional route between airports with distance and fuel efficiency (1-10)"""
        if origin not in self.routes:
            self.routes[origin] = []
        if destination not in self.routes:
            self.routes[destination] = []
        
        # Default congestion level (0-10)
        congestion = random.randint(0, 3)
        
        # Add bidirectional routes
        self.routes[origin].append((destination, distance, fuel_efficiency, congestion))
        self.routes[destination].append((origin, distance, fuel_efficiency, congestion))
    
    def update_congestion(self, origin, destination, is_congested):
        """Update congestion status for a route"""
        if is_congested:
            self.congested_routes.add((origin, destination))
            self.congested_routes.add((destination, origin))  # For bidirectional routes
        else:
            self.congested_routes.discard((origin, destination))
            self.congested_routes.discard((destination, origin))
    
    def update_weather(self, origin, destination, is_affected):
        """Update weather-affected status for a route"""
        if is_affected:
            self.weather_affected_routes.add((origin, destination))
            self.weather_affected_routes.add((destination, origin))  # For bidirectional routes
        else:
            self.weather_affected_routes.discard((origin, destination))
            self.weather_affected_routes.discard((destination, origin))
    
    def get_neighbors(self, airport_code, avoid_congestion=True, prioritize_fuel=False):
        """
        Get neighboring airports, optionally considering congestion and fuel efficiency
        
        Parameters:
        - airport_code: The origin airport code
        - avoid_congestion: If True, avoids routes with high congestion
        - prioritize_fuel: If True, prioritizes fuel-efficient routes
        
        Returns: List of (destination, distance, fuel_efficiency, congestion)
        """
        neighbors = []
        for dest, dist, fuel, cong in self.routes.get(airport_code, []):
            # Skip congested routes or weather-affected routes if avoiding congestion
            if avoid_congestion and ((airport_code, dest) in self.congested_routes or 
                                     (airport_code, dest) in self.weather_affected_routes):
                continue
            neighbors.append((dest, dist, fuel, cong))
        
        # Sort by fuel efficiency if prioritizing fuel
        if prioritize_fuel:
            neighbors.sort(key=lambda x: (-x[2], x[1]))  # Sort by fuel efficiency (desc), then distance (asc)
        
        return neighbors
    
    def bfs_shortest_path(self, start, goal, avoid_congestion=True, prioritize_fuel=False):
        """
        Find the shortest path from start to goal using BFS
        
        Parameters:
        - start: Starting airport code
        - goal: Destination airport code
        - avoid_congestion: If True, avoids congested routes
        - prioritize_fuel: If True, prioritizes fuel-efficient routes
        
        Returns: (path, total_distance, total_fuel_consumption)
        """
        if start not in self.airports or goal not in self.airports:
            return None, float('inf'), float('inf')
        
        # Queue for BFS
        queue = deque([(start, [start], 0, 0)])  # (current, path, distance_so_far, fuel_consumption)
        visited = set([start])
        
        while queue:
            current, path, distance, fuel_consumption = queue.popleft()
            
            # Goal check
            if current == goal:
                return path, distance, fuel_consumption
            
            # Get neighbors based on preferences
            neighbors = self.get_neighbors(current, avoid_congestion, prioritize_fuel)
            
            for neighbor, dist, fuel_eff, congestion in neighbors:
                if neighbor not in visited:
                    # Calculate fuel consumption inversely proportional to efficiency (1-10)
                    fuel_used = dist * (11 - fuel_eff) / 10
                    
                    new_path = path + [neighbor]
                    new_distance = distance + dist
                    new_fuel = fuel_consumption + fuel_used
                    
                    queue.append((neighbor, new_path, new_distance, new_fuel))
                    visited.add(neighbor)
        
        # No path found
        return None, float('inf'), float('inf')
    
    def visualize_path(self, path):
        """Visualize the path for the flight"""
        if not path:
            print("No valid path found.")
            return
        
        print("\nFlight Path:")
        print("-" * 50)
        
        for i in range(len(path)-1):
            origin = path[i]
            destination = path[i+1]
            
            # Find the route details
            route_details = None
            for dest, dist, fuel, cong in self.routes[origin]:
                if dest == destination:
                    route_details = (dist, fuel, cong)
                    break
            
            if route_details:
                dist, fuel, cong = route_details
                congestion_status = "CONGESTED" if (origin, destination) in self.congested_routes else ""
                weather_status = "WEATHER AFFECTED" if (origin, destination) in self.weather_affected_routes else ""
                
                print(f"{self.airports[origin]} → {self.airports[destination]} " +
                      f"({dist} km, Fuel Eff: {fuel}/10, Congestion: {cong}/10) {congestion_status} {weather_status}")
            else:
                print(f"{self.airports[origin]} → {self.airports[destination]} (Details unavailable)")
        
        print("-" * 50)


def create_sample_airport_network():
    """Create a sample airport network with multiple airports and routes"""
    network = AirportNetwork()
    
    # Creating airports (code, name, is_hub, facilities)
    airports = [
    Airport("DEL", "Indira Gandhi International", True, ["Maintenance", "Refueling"]),
    Airport("BOM", "Chhatrapati Shivaji Maharaj International", True, ["Maintenance", "Refueling"]),
    Airport("BLR", "Kempegowda International", True, ["Maintenance", "Refueling"]),
    Airport("MAA", "Chennai International", True, ["Maintenance", "Refueling"]),
    Airport("HYD", "Rajiv Gandhi International", True, ["Maintenance", "Refueling"]),
    Airport("CCU", "Netaji Subhas Chandra Bose International", False, ["Refueling"]),
    Airport("AMD", "Sardar Vallabhbhai Patel International", False, ["Maintenance", "Refueling"]),
    Airport("PNQ", "Pune International", False, ["Refueling"]),
    Airport("COK", "Cochin International", False, ["Maintenance"]),
    Airport("GOI", "Goa International", False, ["Refueling"]),
    Airport("JAI", "Jaipur International", False, ["Refueling"]),
    Airport("LUH", "Ludhiana Airport", False, []),
    Airport("IXC", "Chandigarh International", False, ["Refueling"]),
    Airport("VNS", "Lal Bahadur Shastri International", False, []),
    Airport("PAT", "Jay Prakash Narayan International", False, ["Maintenance"]),
    Airport("LKO", "Chaudhary Charan Singh International", False, ["Refueling"]),
    Airport("BBI", "Biju Patnaik International", False, []),
    Airport("IXB", "Bagdogra Airport", False, ["Maintenance"]),
    Airport("TRV", "Trivandrum International", False, []),
    Airport("IXM", "Madurai International", False, []),
]

    
    # Add airports to the network
    for airport in airports:
        network.add_airport(airport)
    
    # Add routes between airports (origin, destination, distance, fuel_efficiency)
    routes = [
    ("DEL", "JAI", 260, 8),
    ("DEL", "BLR", 1700, 7),
    ("DEL", "MAA", 2200, 8),
    ("DEL", "BOM", 1400, 7),
    ("DEL", "LKO", 500, 9),
    ("DEL", "IXC", 250, 9),
    ("BOM", "GOI", 450, 8),
    ("BOM", "PNQ", 150, 9),
    ("BOM", "AMD", 530, 8),
    ("BOM", "HYD", 710, 7),
    ("BLR", "HYD", 570, 8),
    ("BLR", "CCU", 1900, 7),
    ("BLR", "MAA", 350, 9),
    ("MAA", "COK", 600, 8),
    ("MAA", "TRV", 620, 8),
    ("HYD", "VNS", 1200, 6),
    ("HYD", "PNQ", 850, 7),
    ("HYD", "CCU", 1500, 7),
    ("CCU", "IXB", 500, 9),
    ("CCU", "BBI", 450, 8),
    ("CCU", "PAT", 600, 8),
    ("AMD", "PNQ", 550, 7),
    ("PNQ", "GOI", 450, 8),
    ("COK", "TRV", 220, 9),
    ("LKO", "BBI", 950, 7),
    ("IXC", "LUH", 150, 9),
    ("VNS", "PAT", 250, 9),
    ("TRV", "IXM", 320, 8),
]

    
    for origin, destination, distance, fuel_efficiency in routes:
        network.add_route(origin, destination, distance, fuel_efficiency)
    
    # Simulate some congested routes
    congested_routes = [
        ("DEL", "BLR"),
        ("BOM", "HYD"),
        ("MAA", "COK"),
        ("AMD", "PNQ"),
    ]
    
    for origin, destination in congested_routes:
        network.update_congestion(origin, destination, True)
    
    # Simulate some weather-affected routes
    weather_affected_routes = [
        ("CCU", "BBI"),
        ("HYD", "VNS"),
        ("BLR", "CCU"),
    ]
    
    for origin, destination in weather_affected_routes:
        network.update_weather(origin, destination, True)
    
    return network


def main():
    # Create a sample airport network
    network = create_sample_airport_network()
    
    # Test scenarios
    test_scenarios = [
        {
            "start": "DEL",
            "goal": "BOM",
            "avoid_congestion": True,
            "prioritize_fuel": False,
            "description": "Standard route from DEL to BOM, avoiding congestion"
        },
        {
            "start": "DEL",
            "goal": "BOM",
            "avoid_congestion": False,
            "prioritize_fuel": False,
            "description": "Route from DEL to BOM, ignoring congestion"
        },
        {
            "start": "DEL",
            "goal": "BOM",
            "avoid_congestion": True,
            "prioritize_fuel": True,
            "description": "Fuel-efficient route from DEL to BOM, avoiding congestion"
        },
        {
            "start": "BLR",
            "goal": "MAA",
            "avoid_congestion": True,
            "prioritize_fuel": False,
            "description": "Route from hub (BLR) to MAA, avoiding congestion"
        }
    ]

    
    # Run the scenarios
    for scenario in test_scenarios:
        print("\n" + "="*80)
        print(f"Scenario: {scenario['description']}")
        print("="*80)
        
        # Find shortest path using BFS
        path, distance, fuel = network.bfs_shortest_path(
            scenario['start'], 
            scenario['goal'],
            scenario['avoid_congestion'],
            scenario['prioritize_fuel']
        )
        
        # Display the results
        print(f"\nFlying from {network.airports[scenario['start']]} to {network.airports[scenario['goal']]}")
        print(f"Avoid congestion: {scenario['avoid_congestion']}")
        print(f"Prioritize fuel efficiency: {scenario['prioritize_fuel']}")
        
        if path:
            print(f"\nPath found: {' → '.join(path)}")
            print(f"Total distance: {distance} km")
            print(f"Estimated fuel consumption: {fuel:.2f} units")
            network.visualize_path(path)
        else:
            print("\nNo path found between the given airports.")


if __name__ == "__main__":
    main()