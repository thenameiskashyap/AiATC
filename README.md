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


