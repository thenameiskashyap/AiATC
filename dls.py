import math
import random
import heapq
from collections import defaultdict, deque

class Airport:
    def __init__(self, code, name, city, lat, lon, elevation, runway_length, emergency_capabilities=False):
        self.code = code
        self.name = name
        self.city = city
        self.lat = lat  # Latitude in degrees
        self.lon = lon  # Longitude in degrees
        self.elevation = elevation  # in feet
        self.runway_length = runway_length  # in feet
        self.emergency_capabilities = emergency_capabilities
        
    def __str__(self):
        return f"{self.code} - {self.name} ({self.city})"
    
    def __repr__(self):
        return self.__str__()


class WeatherCondition:
    def __init__(self, severity, affected_area, min_altitude=0, max_altitude=45000):
        """
        severity: 0-10 scale (0 = clear, 10 = severe)
        affected_area: tuple of ((lat1, lon1), (lat2, lon2)) defining a rectangular area
        min_altitude/max_altitude: altitude range affected by this weather (feet)
        """
        self.severity = severity
        self.affected_area = affected_area
        self.min_altitude = min_altitude
        self.max_altitude = max_altitude
    
    def affects_path(self, start_point, end_point, altitude):
        """Check if a path between two points at given altitude is affected by this weather"""
        if altitude < self.min_altitude or altitude > self.max_altitude:
            return False
            
        # Simple check if either endpoint is in the affected area
        lat1, lon1 = start_point
        lat2, lon2 = end_point
        
        (area_lat1, area_lon1), (area_lat2, area_lon2) = self.affected_area
        
        # Check if start point is in weather area
        if (min(area_lat1, area_lat2) <= lat1 <= max(area_lat1, area_lat2) and 
            min(area_lon1, area_lon2) <= lon1 <= max(area_lon1, area_lon2)):
            return True
            
        # Check if end point is in weather area
        if (min(area_lat1, area_lat2) <= lat2 <= max(area_lat1, area_lat2) and 
            min(area_lon1, area_lon2) <= lon2 <= max(area_lon1, area_lon2)):
            return True
            
        # Check if path intersects weather area (simplified)
        # This is a very simplified check and doesn't properly handle path intersection
        # A more sophisticated implementation would check if the great circle path intersects the rectangle
        return False


class AirTrafficZone:
    def __init__(self, name, area, congestion_level, min_altitude=0, max_altitude=60000):
        """
        name: Zone name
        area: tuple of ((lat1, lon1), (lat2, lon2)) defining a rectangular area
        congestion_level: 0-10 scale indicating traffic density
        min_altitude/max_altitude: altitude range affected (feet)
        """
        self.name = name
        self.area = area
        self.congestion_level = congestion_level
        self.min_altitude = min_altitude
        self.max_altitude = max_altitude
    
    def get_delay_factor(self, altitude):
        """Returns a delay factor (multiplier) based on congestion and altitude"""
        if altitude < self.min_altitude or altitude > self.max_altitude:
            return 1.0  # No delay outside altitude range
            
        # Lower altitudes often have more traffic
        altitude_factor = 1.5 - (altitude / self.max_altitude)
        
        # Combine with congestion level for total delay factor
        return 1.0 + (self.congestion_level / 10.0) * altitude_factor


class FlightPathPlanner:
    def __init__(self):
        self.airports = {}
        self.weather_conditions = []
        self.traffic_zones = []
        self.default_climb_rate = 1000  # feet per minute
        self.default_descent_rate = 1000  # feet per minute
        self.low_altitude_threshold = 10000  # feet, defines "low altitude" for technical issues
    
    def add_airport(self, airport):
        self.airports[airport.code] = airport
    
    def add_weather_condition(self, weather):
        self.weather_conditions.append(weather)
    
    def add_traffic_zone(self, zone):
        self.traffic_zones.append(zone)
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate great circle distance between two points in nautical miles"""
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 3440  # Radius of Earth in nautical miles
        
        return c * r
    
    def get_nearby_airports(self, lat, lon, max_distance=200):
        """Find airports within max_distance nautical miles of the given location"""
        nearby = []
        for airport in self.airports.values():
            distance = self.calculate_distance(lat, lon, airport.lat, airport.lon)
            if distance <= max_distance:
                nearby.append((airport, distance))
        
        # Sort by distance
        return sorted(nearby, key=lambda x: x[1])
    
    def filter_suitable_airports(self, aircraft_type, min_runway_length, emergency_required=False):
        """Filter airports based on runway length and emergency capabilities"""
        suitable = []
        for airport in self.airports.values():
            if airport.runway_length >= min_runway_length:
                if not emergency_required or airport.emergency_capabilities:
                    suitable.append(airport)
        return suitable
    
    def check_path_feasibility(self, start_lat, start_lon, end_lat, end_lon, altitude):
        """Check if a direct path is feasible given weather and traffic conditions"""
        # Check weather conditions
        for weather in self.weather_conditions:
            if weather.affects_path((start_lat, start_lon), (end_lat, end_lon), altitude):
                if weather.severity > 7:  # Severe weather makes path unfeasible
                    return False, f"Severe weather (level {weather.severity}) affecting path"
        
        # All checks passed
        return True, "Path is feasible"
    
    def estimate_travel_time(self, distance, aircraft_speed, altitude):
        """Estimate travel time considering traffic zones"""
        base_time = distance / aircraft_speed  # hours
        
        # Apply delay factors from traffic zones
        total_delay_factor = 1.0
        for zone in self.traffic_zones:
            delay = zone.get_delay_factor(altitude)
            total_delay_factor = max(total_delay_factor, delay)  # Use the worst delay
        
        return base_time * total_delay_factor
    
    def depth_limited_search(self, start_lat, start_lon, start_alt, aircraft_type, 
                            aircraft_speed, max_depth=5, altitude_constraint=10000):
        """
        Perform depth-limited search to find paths to suitable airports
        
        Parameters:
        - start_lat, start_lon: Starting position
        - start_alt: Starting altitude in feet
        - aircraft_type: Type of aircraft (affects runway requirements)
        - aircraft_speed: Speed in knots
        - max_depth: Maximum number of waypoints to consider
        - altitude_constraint: Maximum altitude allowed due to technical issues
        
        Returns:
        - List of viable paths to airports
        """
        # Define aircraft requirements
        if aircraft_type == "small":
            min_runway_length = 3000
        elif aircraft_type == "medium":
            min_runway_length = 5000
        else:  # large
            min_runway_length = 8000
        
        # Get suitable airports within range
        max_range = aircraft_speed * 3  # 3 hours of flying at cruise speed
        nearby_airports = self.get_nearby_airports(start_lat, start_lon, max_range)
        suitable_airports = [(airport, dist) for airport, dist in nearby_airports 
                            if airport.runway_length >= min_runway_length]
        
        if not suitable_airports:
            return []
        
        viable_paths = []
        
        # Helper function for recursive DLS
        def dls_recursive(curr_lat, curr_lon, curr_alt, path, depth, total_distance, total_time):
            if depth > max_depth:
                return
            
            # Find airports reachable from current position
            for airport, dist_to_airport in suitable_airports:
                direct_distance = self.calculate_distance(curr_lat, curr_lon, airport.lat, airport.lon)
                
                # Check if we can reach this airport directly while staying below altitude constraint
                feasible, reason = self.check_path_feasibility(
                    curr_lat, curr_lon, airport.lat, airport.lon, altitude_constraint
                )
                
                if feasible:
                    # Calculate time considering traffic
                    segment_time = self.estimate_travel_time(direct_distance, aircraft_speed, altitude_constraint)
                    new_total_time = total_time + segment_time
                    new_total_distance = total_distance + direct_distance
                    
                    # This is a viable path to an airport
                    new_path = path + [(airport.code, airport.lat, airport.lon, direct_distance, segment_time)]
                    viable_paths.append({
                        "path": new_path,
                        "total_distance": new_total_distance,
                        "total_time": new_total_time,
                        "airport": airport
                    })
            
            # If we haven't reached max depth, consider intermediate waypoints
            if depth < max_depth:
                # Create some potential waypoints by sampling around current position
                # This is simplified; a real implementation would use established waypoints or navigation points
                waypoints = []
                for _ in range(5):  # Try 5 random waypoints
                    # Random offset between -1 and 1 degree in each direction (very simplified)
                    lat_offset = (random.random() * 2 - 1) * 0.5
                    lon_offset = (random.random() * 2 - 1) * 0.5
                    new_lat = curr_lat + lat_offset
                    new_lon = curr_lon + lon_offset
                    waypoint_distance = self.calculate_distance(curr_lat, curr_lon, new_lat, new_lon)
                    
                    # Check feasibility to this waypoint
                    feasible, reason = self.check_path_feasibility(
                        curr_lat, curr_lon, new_lat, new_lon, altitude_constraint
                    )
                    
                    if feasible and waypoint_distance < 100:  # Limit waypoint distance
                        segment_time = self.estimate_travel_time(waypoint_distance, aircraft_speed, altitude_constraint)
                        waypoints.append((new_lat, new_lon, waypoint_distance, segment_time))
                
                # Recursively explore from each feasible waypoint
                for wp_lat, wp_lon, wp_dist, wp_time in waypoints:
                    new_path = path + [("WP", wp_lat, wp_lon, wp_dist, wp_time)]
                    new_total_distance = total_distance + wp_dist
                    new_total_time = total_time + wp_time
                    
                    dls_recursive(wp_lat, wp_lon, altitude_constraint, new_path, depth + 1, 
                                 new_total_distance, new_total_time)
        
        # Start the recursive DLS from initial position
        dls_recursive(start_lat, start_lon, start_alt, [], 0, 0, 0)
        
        # Sort paths by total time
        viable_paths.sort(key=lambda x: x["total_time"])
        
        return viable_paths

    def format_path_output(self, path_data):
        """Format path data for display"""
        result = []
        result.append(f"Path to {path_data['airport'].name} ({path_data['airport'].city}):")
        result.append(f"Total distance: {path_data['total_distance']:.1f} NM")
        result.append(f"Estimated time: {path_data['total_time']:.2f} hours")
        result.append("Route:")
        
        for i, (point_type, lat, lon, segment_dist, segment_time) in enumerate(path_data['path']):
            if point_type == "WP":
                result.append(f"  {i+1}. Waypoint at ({lat:.4f}, {lon:.4f}) - {segment_dist:.1f} NM, {segment_time*60:.1f} mins")
            else:
                result.append(f"  {i+1}. {point_type} ({lat:.4f}, {lon:.4f}) - {segment_dist:.1f} NM, {segment_time*60:.1f} mins")
        
        return "\n".join(result)


# Create and initialize the planner with Indian airports
def create_indian_airport_simulation():
    planner = FlightPathPlanner()
    
    # Add major Indian airports
    # Format: code, name, city, lat, lon, elevation(ft), runway_length(ft), emergency_capabilities
    indian_airports = [
        Airport("DEL", "Indira Gandhi International Airport", "Delhi", 28.5561, 77.1000, 777, 14534, True),
        Airport("BOM", "Chhatrapati Shivaji Maharaj International Airport", "Mumbai", 19.0896, 72.8656, 39, 12008, True),
        Airport("MAA", "Chennai International Airport", "Chennai", 12.9941, 80.1709, 52, 12001, True),
        Airport("BLR", "Kempegowda International Airport", "Bengaluru", 13.1979, 77.7063, 3000, 13123, True),
        Airport("HYD", "Rajiv Gandhi International Airport", "Hyderabad", 17.2403, 78.4294, 2000, 12917, True),
        Airport("CCU", "Netaji Subhas Chandra Bose International Airport", "Kolkata", 22.6520, 88.4463, 20, 11900, True),
        Airport("COK", "Cochin International Airport", "Kochi", 10.1520, 76.3920, 26, 12467, True),
        Airport("AMD", "Sardar Vallabhbhai Patel International Airport", "Ahmedabad", 23.0747, 72.6342, 189, 10499, False),
        Airport("PNQ", "Pune Airport", "Pune", 18.5793, 73.9089, 1942, 8300, False),
        Airport("GAU", "Lokpriya Gopinath Bordoloi International Airport", "Guwahati", 26.1075, 91.5859, 162, 9000, True),
        Airport("LKO", "Chaudhary Charan Singh International Airport", "Lucknow", 26.7606, 80.8893, 410, 9000, False),
        Airport("JAI", "Jaipur International Airport", "Jaipur", 26.8242, 75.8122, 1263, 9000, False),
        Airport("TRV", "Trivandrum International Airport", "Thiruvananthapuram", 8.4784, 76.9200, 15, 10499, False),
        Airport("IXC", "Chandigarh International Airport", "Chandigarh", 30.6735, 76.7885, 1012, 9000, False),
        Airport("IXM", "Madurai Airport", "Madurai", 9.8322, 78.0934, 459, 7500, False),
        Airport("VTZ", "Visakhapatnam Airport", "Visakhapatnam", 17.7215, 83.2243, 10, 10500, False),
        Airport("IXZ", "Veer Savarkar International Airport", "Port Blair", 11.6461, 92.7330, 14, 10500, False),
        Airport("IDR", "Devi Ahilyabai Holkar Airport", "Indore", 22.7218, 75.8011, 1850, 8000, False),
        Airport("ATQ", "Sri Guru Ram Dass Jee International Airport", "Amritsar", 31.7090, 74.7970, 756, 12000, False),
        Airport("IXR", "Birsa Munda Airport", "Ranchi", 23.3143, 85.3217, 2146, 8100, False)
    ]
    
    for airport in indian_airports:
        planner.add_airport(airport)
    
    # Add some weather conditions (monsoon, cyclones)
    # Northern India Monsoon
    planner.add_weather_condition(WeatherCondition(
        severity=8,
        affected_area=((25.0, 75.0), (30.0, 85.0)),
        min_altitude=0,
        max_altitude=20000
    ))
    
    # Coastal Cyclone near Chennai
    planner.add_weather_condition(WeatherCondition(
        severity=9,
        affected_area=((11.0, 79.0), (14.0, 82.0)),
        min_altitude=0,
        max_altitude=30000
    ))
    
    # Fog over Delhi
    planner.add_weather_condition(WeatherCondition(
        severity=6,
        affected_area=((28.0, 76.5), (29.0, 77.5)),
        min_altitude=0,
        max_altitude=5000
    ))
    
    # Add traffic zones
    # Delhi airspace
    planner.add_traffic_zone(AirTrafficZone(
        "Delhi TMA",
        ((28.0, 76.5), (29.0, 77.5)),
        congestion_level=9,
        min_altitude=0,
        max_altitude=15000
    ))
    
    # Mumbai airspace
    planner.add_traffic_zone(AirTrafficZone(
        "Mumbai TMA",
        ((18.5, 72.0), (19.5, 73.5)),
        congestion_level=8,
        min_altitude=0,
        max_altitude=15000
    ))
    
    # Bengaluru airspace
    planner.add_traffic_zone(AirTrafficZone(
        "Bengaluru TMA",
        ((12.8, 77.2), (13.5, 78.0)),
        congestion_level=7,
        min_altitude=0,
        max_altitude=15000
    ))
    
    return planner


# Demo function to run the simulation
def run_low_altitude_flight_path_demo():
    planner = create_indian_airport_simulation()
    
    # Simulate an aircraft with technical issues near Ahmedabad that needs to find a path
    # while staying at low altitude
    start_lat = 23.2
    start_lon = 72.8
    start_alt = 20000  # Starting at 20,000 feet but needs to descend
    aircraft_type = "medium"  # Medium-sized aircraft
    aircraft_speed = 300  # knots
    max_depth = 4  # Maximum number of waypoints to consider
    altitude_constraint = 8000  # Must stay below 8,000 feet due to technical issues
    
    print(f"Aircraft with technical issues near ({start_lat}, {start_lon})")
    print(f"Must stay below {altitude_constraint} feet due to pressurization problems")
    print(f"Searching for viable low-altitude paths to nearby airports...")
    
    paths = planner.depth_limited_search(
        start_lat, start_lon, start_alt, 
        aircraft_type, aircraft_speed, 
        max_depth, altitude_constraint
    )
    
    if not paths:
        print("No viable paths found!")
    else:
        print(f"\nFound {len(paths)} viable paths.")
        print("\nTop 3 recommended paths:")
        for i, path in enumerate(paths[:3]):
            print(f"\nOption {i+1}:")
            print(planner.format_path_output(path))
            print("-" * 50)


if __name__ == "__main__":
    run_low_altitude_flight_path_demo()