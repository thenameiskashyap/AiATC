# Explanation of the BFS Case Study on Airport Network Exploration

This code simulates an **airport network** and implements the **Breadth-First Search (BFS) algorithm** to find the shortest path between two airports. It also considers real-world challenges like **congestion, weather conditions, and fuel efficiency** when determining optimal flight paths.

---

## 1. Key Components of the Code

### **A. Airport Class**  
Represents an airport with:  
- **Code** (e.g., DEL for Delhi Airport)  
- **Name**  
- **Hub status** (whether it's a major hub)  
- **Facilities** (like maintenance or refueling)  

### **B. AirportNetwork Class**  
Manages the network of airports and their routes, handling congestion and weather-related disruptions.

#### **Attributes**  
- `airports`: Dictionary storing Airport objects `{airport_code: Airport}`  
- `routes`: Dictionary storing flight connections `{airport_code: [(destination, distance, fuel_efficiency, congestion)]}`  
- `congested_routes`: Set of congested flight paths  
- `weather_affected_routes`: Set of weather-disrupted flight paths  

#### **Methods**  
- `add_airport()`: Adds an airport to the network.  
- `add_route()`: Adds a bidirectional route between two airports, storing distance, fuel efficiency, and congestion levels.  
- `update_congestion()`: Updates congestion status of a flight path.  
- `update_weather()`: Updates weather conditions affecting a route.  
- `get_neighbors()`: Retrieves valid neighboring airports while avoiding congested/weather-affected routes.  
- `bfs_shortest_path()`: Uses BFS to find the shortest flight path, considering congestion and fuel efficiency.  
- `visualize_path()`: Displays a detailed flight path with distance, fuel efficiency, and congestion status.  

---

## 2. BFS Algorithm for Shortest Path  

The function **`bfs_shortest_path(start, goal, avoid_congestion, prioritize_fuel)`** implements BFS as follows:

### **Step-by-Step Working**  
1. **Initialize** a queue with `(current_airport, path_so_far, total_distance, total_fuel)`.  
2. Use a **visited set** to avoid re-visiting airports.  
3. **Loop until queue is empty:**  
   - Remove the **front airport** from the queue.  
   - If it matches the **destination**, return the path and distances.  
   - Get **valid neighboring airports**, avoiding congestion/weather if specified.  
   - Calculate **fuel consumption** based on distance and fuel efficiency.  
   - Push **unvisited neighbors** into the queue.  
4. If **no valid path exists**, return an infinite distance and fuel usage.  

---

## 3. Sample Airport Network  

The function **`create_sample_airport_network()`** initializes:  
- **20 airports** across India.  
- **Multiple flight routes** between them, with distances and fuel efficiencies.  
- **Congested routes**: DEL-BLR, BOM-HYD, etc.  
- **Weather-affected routes**: CCU-BBI, BLR-CCU, etc.  

---

## 4. Testing the Algorithm  

The **`main()`** function defines test cases:  
- **DEL → BOM** (Standard route avoiding congestion)  
- **DEL → BOM** (Ignoring congestion)  
- **DEL → BOM** (Prioritizing fuel efficiency)  
- **BLR → MAA** (Hub-to-hub flight)  

### **For each case:**  
- The function **finds and prints** the BFS path.  
- **Visualizes** the flight path, showing **distance, fuel efficiency, congestion, and weather**.




#                            Depth-First Search (DFS): Emergency Landing Planning

## **Overview**  
This project simulates an emergency landing scenario where an aircraft must locate the closest viable airport using **Depth-First Search (DFS)**. The system evaluates various factors such as **fuel availability, runway length, airport facilities, and weather conditions** to determine the best possible landing site.  

---

## **Problem Statement**  
A flight encounters an emergency and requires an immediate landing. The closest **suitable** airport must be identified using DFS, ensuring the aircraft can land safely.  

### **Challenges**  
- **Avoid revisiting already evaluated airports**  
- **Handle varying suitability of airports based on available facilities and weather**  
- **Manage decoy airports that falsely report full capabilities**  

---

## **Approach**  
### **1. Airport and Aircraft Modeling**  
- **Airport Class:** Represents an airport with attributes like **location, runway length, control tower, facilities, and weather conditions**.  
- **Aircraft Class:** Represents an aircraft with properties like **position, fuel remaining, and emergency status**.  

### **2. Emergency Classification**  
Different emergencies require specific facilities:  
- **Medical Emergency:** Requires **medical facilities**  
- **Fire Emergency:** Requires **fire response capabilities**  
- **Mechanical Failure:** Requires **maintenance support**  

### **3. Distance Calculation (Haversine Formula)**  
To determine the closest airports, the system calculates distances between **aircraft and airport locations** using the **Haversine formula**, which computes great-circle distances between latitude/longitude points.  

### **4. Depth-First Search (DFS) for Emergency Landing**  
DFS is used to explore nearby airports and determine **if the aircraft can land safely**:  
1. **Sort airports by distance** from the aircraft's position.  
2. **Check feasibility** (fuel, runway length, weather).  
3. **If an airport is unsuitable, move to the next closest option**.  
4. **Track visited airports** to prevent revisiting.  
5. **Verify decoy airports before selection** (50% chance they are unsuitable).  

---

## **Key Features**  
✔ **Sorting Airports by Distance**  
✔ **Handling Different Emergency Types**  
✔ **Verifying Airport Facilities & Conditions**  
✔ **Avoiding Revisited or Decoy Airports**  
✔ **Ensuring Feasibility Based on Fuel & Runway Requirements**  

---

#                                         Flight Path Planning System (Using DLS) 
 
This project is a flight path planning system that evaluates potential flight routes while considering factors such as weather conditions, air traffic congestion, airport suitability, and emergency landing options.  

## Features  
- **Airport Management**: Stores airport details including location, runway length, and emergency capabilities.  
- **Weather Monitoring**: Tracks weather conditions that affect flight paths, including severe storms, fog, and cyclones.  
- **Air Traffic Control**: Implements congestion levels in different air traffic zones to estimate delays.  
- **Flight Path Feasibility**: Checks if a direct flight path is possible based on weather and traffic conditions.  
- **Alternative Route Planning**: Uses Depth-Limited Search (DLS) to find alternate routes to suitable airports in case of emergencies.  
- **Distance and Time Estimation**: Calculates the distance between locations using the Haversine formula and estimates travel time considering delays.  



### Dependencies  
The project uses the following Python libraries:  
- `math` (for calculations)  
- `heapq` (for priority queues)  
- `collections` (for data structures)  




