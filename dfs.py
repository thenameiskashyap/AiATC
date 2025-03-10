import math
from collections import namedtuple
from typing import List, Set, Dict, Tuple, Optional

# Define data structures
Position = namedtuple('Position', ['latitude', 'longitude'])
EmergencyType = namedtuple('EmergencyType', ['name', 'severity', 'required_facilities'])

class Airport:
    def __init__(self, airport_id: str, name: str, position: Position, 
                 runway_length: float, has_control_tower: bool, 
                 facilities: Dict[str, bool], weather_condition: str = "clear"):
        self.id = airport_id
        self.name = name
        self.position = position
        self.runway_length = runway_length  # in meters
        self.has_control_tower = has_control_tower
        self.facilities = facilities  # Dict of available facilities
        self.weather_condition = weather_condition
        self.is_decoy = False  # Default is not a decoy
        
    def has_medical_facilities(self) -> bool:
        return self.facilities.get('medical', False)
    
    def has_maintenance_capabilities(self) -> bool:
        return self.facilities.get('maintenance', False)
        
    def has_fire_response(self) -> bool:
        return self.facilities.get('fire_response', False)
    
    def is_limited_facility(self) -> bool:
        # An airport is considered limited if it lacks at least two major facilities
        major_facilities = ['medical', 'maintenance', 'fire_response', 'refueling']
        available_count = sum(1 for f in major_facilities if self.facilities.get(f, False))
        return available_count <= 2
    
    def mark_as_decoy(self):
        """Mark this airport as a decoy with limited actual capabilities"""
        self.is_decoy = True
    
    def __str__(self) -> str:
        return f"Airport {self.id}: {self.name} at {self.position}"


class Aircraft:
    def __init__(self, flight_id: str, position: Position, 
                 fuel_remaining: float, aircraft_type: str):
        self.id = flight_id
        self.position = position
        self.fuel_remaining = fuel_remaining  # in minutes of flight time
        self.aircraft_type = aircraft_type
        self.emergency_status = None
    
    def declare_emergency(self, emergency_type: EmergencyType):
        """Declare an emergency for this aircraft"""
        self.emergency_status = emergency_type
        
    def can_reach_airport(self, airport: Airport) -> bool:
        """Determine if the aircraft has enough fuel to reach the airport"""
        distance = calculate_distance(self.position, airport.position)
        # Simple model: 1 distance unit = 1 minute of fuel
        return self.fuel_remaining >= distance
    
    def __str__(self) -> str:
        status = "EMERGENCY: " + self.emergency_status.name if self.emergency_status else "Normal"
        return f"Aircraft {self.id} ({self.aircraft_type}) at {self.position} - Status: {status}"


# Utility functions
def calculate_distance(pos1: Position, pos2: Position) -> float:
    """Calculate the distance between two positions using the Haversine formula"""
    # Convert latitude and longitude from degrees to radians
    lat1, lon1 = math.radians(pos1.latitude), math.radians(pos1.longitude)
    lat2, lon2 = math.radians(pos2.latitude), math.radians(pos2.longitude)
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    
    return c * r


def sort_by_distance(position: Position, airports: List[Airport]) -> List[Airport]:
    """Sort airports by distance from the given position"""
    return sorted(airports, key=lambda airport: calculate_distance(position, airport.position))


def meets_minimum_requirements(airport: Airport, aircraft: Aircraft) -> bool:
    """Check if the airport meets minimum requirements for landing"""
    # Get required runway length based on aircraft type
    required_length = {
        'small': 1000,
        'medium': 2000,
        'large': 3000,
        'jumbo': 3500
    }.get(aircraft.aircraft_type.lower(), 2000)
    
    # Check weather conditions
    weather_suitable = airport.weather_condition not in ['severe_storm', 'hurricane', 'tornado']
    
    # Basic requirement: sufficient runway length and acceptable weather
    return airport.runway_length >= required_length and weather_suitable


def verify_emergency_landing_capability(airport: Airport, emergency_type: EmergencyType) -> bool:
    """Additional verification for airports with limited facilities or marked as decoys"""
    if airport.is_decoy:
        # Decoy airports require extra scrutiny - 50% chance they're not actually suitable
        # In a real system, this would involve checking against a verified database
        import random
        if random.random() < 0.5:
            return False
    
    # Check if the airport has the required facilities for this emergency
    for facility in emergency_type.required_facilities:
        if not airport.facilities.get(facility, False):
            return False
    
    return True


def is_suitable_for_emergency(airport: Airport, aircraft: Aircraft) -> bool:
    """Determine if the airport is suitable for the emergency landing"""
    # First, check if the aircraft can reach this airport with remaining fuel
    if not aircraft.can_reach_airport(airport):
        return False
    
    # Then check minimum requirements
    if not meets_minimum_requirements(airport, aircraft):
        return False
    
    # No emergency declared, any airport meeting minimum requirements is fine
    if not aircraft.emergency_status:
        return True
    
    emergency_type = aircraft.emergency_status
    
    # Verify specific emergency needs
    if emergency_type.name == "medical":
        if not airport.has_medical_facilities():
            return False
    elif emergency_type.name == "fire":
        if not airport.has_fire_response():
            return False
    elif emergency_type.name == "mechanical":
        if not airport.has_maintenance_capabilities():
            return False
    
    # Additional verification for limited facility airports
    if airport.is_limited_facility() or airport.is_decoy:
        return verify_emergency_landing_capability(airport, emergency_type)
    
    return True


def emergency_landing_dfs(aircraft: Aircraft, airports: List[Airport], 
                          max_depth: int = None, visited: Set[str] = None, 
                          depth: int = 0) -> Optional[Airport]:
    """
    Find a suitable airport for emergency landing using DFS
    
    Parameters:
    - aircraft: The aircraft requiring emergency landing
    - airports: List of available airports
    - max_depth: Maximum search depth (optional)
    - visited: Set of already visited airport IDs
    - depth: Current search depth
    
    Returns:
    - Suitable airport or None if none found
    """
    if visited is None:
        visited = set()
    
    # Check max depth for safety
    if max_depth is not None and depth >= max_depth:
        return None
    
    # Sort airports by distance from current position for efficiency
    sorted_airports = sort_by_distance(aircraft.position, airports)
    
    for airport in sorted_airports:
        if airport.id not in visited:
            visited.add(airport.id)
            
            # Check if this airport is suitable for emergency landing
            if is_suitable_for_emergency(airport, aircraft):
                return airport
            
            # If not suitable, continue searching from this point
            # In a real scenario, this would consider the new position after moving toward this airport
            new_position = Position(
                (aircraft.position.latitude + airport.position.latitude) / 2,
                (aircraft.position.longitude + airport.position.longitude) / 2
            )
            
            # Update aircraft position and fuel for this hypothetical move
            remaining_distance = calculate_distance(new_position, airport.position)
            distance_traveled = calculate_distance(aircraft.position, new_position)
            
            # Create a copy of the aircraft to avoid modifying the original
            new_aircraft = Aircraft(
                aircraft.id,
                new_position,
                aircraft.fuel_remaining - distance_traveled,
                aircraft.aircraft_type
            )
            if aircraft.emergency_status:
                new_aircraft.declare_emergency(aircraft.emergency_status)
            
            # Skip this path if we don't have enough fuel to continue
            if new_aircraft.fuel_remaining <= 0:
                continue
                
            result = emergency_landing_dfs(new_aircraft, airports, max_depth, visited, depth + 1)
            if result:
                return result
    
    return None  # No suitable airport found


# Test the implementation with Indian airports
def create_test_scenario():
    """Create a test scenario with Indian airports and aircraft"""
    # Create airports based on real Indian airports
    airports = [
        Airport("DEL", "Indira Gandhi International Airport", 
                Position(28.5561, 77.0994), 4430, True,
                {'medical': True, 'maintenance': True, 'fire_response': True, 'refueling': True},
                "clear"),
        
        Airport("BOM", "Chhatrapati Shivaji Maharaj International Airport",
                Position(19.0896, 72.8656), 3660, True,
                {'medical': True, 'maintenance': True, 'fire_response': True, 'refueling': True},
                "rain"),
        
        Airport("MAA", "Chennai International Airport",
                Position(12.9941, 80.1709), 3658, True,
                {'medical': True, 'maintenance': True, 'fire_response': True, 'refueling': True},
                "clear"),
        
        Airport("HYD", "Rajiv Gandhi International Airport",
                Position(17.2403, 78.4294), 4260, True,
                {'medical': True, 'maintenance': True, 'fire_response': True, 'refueling': True},
                "clear"),
        
        Airport("BLR", "Kempegowda International Airport",
                Position(13.1986, 77.7066), 4000, True,
                {'medical': True, 'maintenance': True, 'fire_response': True, 'refueling': True},
                "fog"),
        
        Airport("CCU", "Netaji Subhas Chandra Bose International Airport",
                Position(22.6520, 88.4467), 3627, True,
                {'medical': True, 'maintenance': True, 'fire_response': True, 'refueling': True},
                "clear"),
        
        Airport("GOI", "Goa International Airport",
                Position(15.3808, 73.8314), 3400, True,
                {'medical': True, 'maintenance': True, 'fire_response': True, 'refueling': True},
                "clear"),
        
        # Airport with good medical but limited maintenance
        Airport("NAG", "Dr. Babasaheb Ambedkar International Airport",
                Position(21.0922, 79.0490), 3200, True,
                {'medical': True, 'maintenance': False, 'fire_response': True, 'refueling': True},
                "clear"),
        
        # Airport with good maintenance but no medical
        Airport("IXR", "Birsa Munda Airport",
                Position(23.3143, 85.3217), 2713, True,
                {'medical': False, 'maintenance': True, 'fire_response': True, 'refueling': True},
                "clear"),
        
        # Small airport with just fire response
        Airport("JLR", "Jabalpur Airport",
                Position(23.1778, 80.0520), 2380, True,
                {'medical': False, 'maintenance': False, 'fire_response': True, 'refueling': True},
                "clear"),
        
        # Decoy airport - falsely reporting full capabilities
        Airport("IDR", "Devi Ahilyabai Holkar Airport",
                Position(22.7236, 75.8017), 2750, True,
                {'medical': True, 'maintenance': True, 'fire_response': True, 'refueling': True},
                "clear")
    ]
    
    # Mark the decoy airport
    airports[-1].mark_as_decoy()
    
    # Create an aircraft with an emergency near Nagpur (central India)
    # Position it between Nagpur and Jabalpur to make both viable options
    aircraft = Aircraft("AI302", Position(21.1500, 79.0500), 200, "large")
    
    # Declare different types of emergencies
    emergencies = {
        "medical": EmergencyType("medical", 8, ["medical"]),
        "fire": EmergencyType("fire", 9, ["fire_response"]),
        "mechanical": EmergencyType("mechanical", 6, ["maintenance"])
    }
    
    return airports, aircraft, emergencies


def run_test():
    """Run the emergency landing test with DFS"""
    airports, aircraft, emergencies = create_test_scenario()
    
    print(f"Starting position: {aircraft.position} (Between Jabalpur and Nagpur, Central India)")
    print(f"Aircraft: {aircraft.id}, Type: {aircraft.aircraft_type}, Fuel remaining: {aircraft.fuel_remaining} minutes")
    print(f"\nAvailable airports:")
    
    for airport in airports:
        distance = calculate_distance(aircraft.position, airport.position)
        print(f"  - {airport.name} ({airport.id}) - Distance: {distance:.2f} km")
        
        # Print details about facilities
        facilities = []
        if airport.facilities.get('medical', False):
            facilities.append("Medical")
        if airport.facilities.get('maintenance', False):
            facilities.append("Maintenance")
        if airport.facilities.get('fire_response', False):
            facilities.append("Fire Response")
        if airport.facilities.get('refueling', False):
            facilities.append("Refueling")
            
        print(f"    Facilities: {', '.join(facilities)}")
        print(f"    Runway Length: {airport.runway_length} meters, Weather: {airport.weather_condition}")
        
        if airport.is_decoy:
            print("    * This is a decoy airport with potentially limited actual capabilities")
        if airport.is_limited_facility():
            print("    * This airport has limited facilities")
    
    print("\nTesting different emergency scenarios:")
    
    for emergency_name, emergency_type in emergencies.items():
        print(f"\n---- {emergency_name.upper()} EMERGENCY ----")
        aircraft.declare_emergency(emergency_type)
        
        suitable_airport = emergency_landing_dfs(aircraft, airports, max_depth=3)
        
        if suitable_airport:
            distance = calculate_distance(aircraft.position, suitable_airport.position)
            print(f"Found suitable airport: {suitable_airport.name} ({suitable_airport.id})")
            print(f"Distance: {distance:.2f} km")
            
            # Print facilities available
            facilities = []
            for facility, available in suitable_airport.facilities.items():
                if available:
                    facilities.append(facility.replace('_', ' ').title())
            print(f"Available facilities: {', '.join(facilities)}")
            
            # Show why this airport was selected
            if emergency_name == "medical" and suitable_airport.has_medical_facilities():
                print("This airport has medical facilities required for a medical emergency.")
            elif emergency_name == "fire" and suitable_airport.has_fire_response():
                print("This airport has fire response capabilities required for a fire emergency.")
            elif emergency_name == "mechanical" and suitable_airport.has_maintenance_capabilities():
                print("This airport has maintenance capabilities required for a mechanical emergency.")
        else:
            print(f"No suitable airport found for {emergency_name} emergency!")


if __name__ == "__main__":
    run_test()