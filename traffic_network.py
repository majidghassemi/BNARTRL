import random
import time

class TrafficNetwork:
    def __init__(self, graph, default_maxspeed=50):
        self.graph = graph
        self.default_maxspeed = default_maxspeed
        self.node_info = {}
        self.edge_info = {}
        self.signal_states = ['green', 'red']
        self.start_time = time.time()
        self._initialize_network()

    def _initialize_network(self):
        """Initializes the network by populating node and edge information."""
        self._populate_node_info()
        self._populate_edge_info()

    def _populate_node_info(self):
        """Populates the node information dictionary with initial data."""
        for node, data in self.graph.nodes(data=True):
            self.node_info[node] = {
                'signal_state': None,
                'position': (data.get('x', None), data.get('y', None)),
                'connected_edges': list(self.graph.edges(node)),
                'signal_index': None,
                'delay': None
            }

    def _populate_edge_info(self):
        """Populates the edge information dictionary."""
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            if data.get('maxspeed') is None:
                data['maxspeed'] = self.default_maxspeed

            self.edge_info[(u, v, key)] = {
                'start_node': u,
                'end_node': v,
                'length': data.get('length', None),
                'maxspeed': data['maxspeed'],
                'traffic_density': 0,
                'vehicles_on_edge': [],  # Track vehicles on this edge
                'arrival_times': {}  # Track the arrival time of each vehicle on this edge
            }

    def add_vehicle(self, vehicle_id, start_position):
        """Add a vehicle to the traffic network at the specified start position."""
        for edge_key, edge_data in self.edge_info.items():
            if edge_data['start_node'] == start_position:
                self.edge_info[edge_key]['vehicles_on_edge'].append(vehicle_id)
                self.edge_info[edge_key]['traffic_density'] += 1
                print(f"Vehicle {vehicle_id} added to edge starting at {start_position}.")
                return

    def remove_vehicle(self, vehicle_id, current_position):
        """Remove a vehicle from the traffic network at its current position."""
        for edge_key, edge_data in self.edge_info.items():
            if vehicle_id in edge_data['vehicles_on_edge']:
                self.edge_info[edge_key]['vehicles_on_edge'].remove(vehicle_id)
                self.edge_info[edge_key]['traffic_density'] -= 1
                self.edge_info[edge_key]['arrival_times'].pop(vehicle_id, None)
                print(f"Vehicle {vehicle_id} removed from edge starting at {current_position}.")
                return

    def update_traffic_density(self, current_position, next_position, vehicle_id):
        """Update traffic density on the edge from current_position to next_position."""
        current_edge = (current_position, next_position)

        # Record the arrival time of the vehicle on the edge it's moving to
        arrival_time = time.time()
        
        if current_edge in self.edge_info:
            if vehicle_id in self.edge_info[current_edge]['vehicles_on_edge']:
                self.edge_info[current_edge]['vehicles_on_edge'].remove(vehicle_id)
                self.edge_info[current_edge]['traffic_density'] -= 1
                self.edge_info[current_edge]['arrival_times'].pop(vehicle_id, None)
        
        next_edge = (current_position, next_position)
        if next_edge in self.edge_info:
            self.edge_info[next_edge]['vehicles_on_edge'].append(vehicle_id)
            self.edge_info[next_edge]['traffic_density'] += 1
            self.edge_info[next_edge]['arrival_times'][vehicle_id] = arrival_time

    def get_neighbors(self, node):
        """Get neighbors of the given node."""
        return list(self.graph.neighbors(node))

    def get_traffic_time(self, current_node, next_node):
        """
        Calculate the travel time on the edge between the given nodes, taking into account traffic density,
        road length, and speed limits.

        :param current_node: The starting node of the edge.
        :param next_node: The ending node of the edge.
        :return: The estimated travel time between the two nodes.
        """
        edge = (current_node, next_node, 0)  # Assuming a single edge between nodes
        if edge in self.edge_info:
            traffic_density = self.edge_info[edge]['traffic_density']
            max_speed = self.edge_info[edge]['maxspeed']
            road_length = self.edge_info[edge]['length']
            
            # Base time to travel the edge at max speed without traffic
            base_time = road_length / max_speed
            
            # Additional delay factor based on traffic density
            delay_factor = 1 + (traffic_density * 0.01)  # Example: 1% extra time per vehicle
            
            # Calculate the total estimated travel time
            travel_time = base_time * delay_factor
            return travel_time
        
        # If the edge is not found, return a large time to discourage using this path
        return float('inf')

    def should_yield(self, vehicle_id, other_vehicle_id, current_edge):
        """
        Determine if a vehicle should yield to another on a shared edge based on arrival times.

        :param vehicle_id: The ID of the current vehicle.
        :param other_vehicle_id: The ID of the other vehicle on the shared edge.
        :param current_edge: The edge where the decision is being made.
        :return: True if the current vehicle should yield, False otherwise.
        """
        arrival_times = self.edge_info[current_edge]['arrival_times']
        
        if vehicle_id in arrival_times and other_vehicle_id in arrival_times:
            return arrival_times[vehicle_id] > arrival_times[other_vehicle_id]
        return False  # Default to not yielding if arrival times are not available

    def update_shared_edge(self, vehicle_id, other_vehicle_id, current_edge):
        """
        Update the traffic network to manage shared edge scenarios where two vehicles are on the same edge.
        This function will manage the interaction between vehicles, adjusting speeds, managing priorities,
        and ensuring safe passage based on arrival times and other factors.

        :param vehicle_id: The ID of the current vehicle.
        :param other_vehicle_id: The ID of the other vehicle on the shared edge.
        :param current_edge: The edge where the vehicles are sharing space.
        """
        # Retrieve the arrival times of both vehicles
        arrival_times = self.edge_info[current_edge]['arrival_times']
        
        # Determine which vehicle arrived first
        if arrival_times[vehicle_id] < arrival_times[other_vehicle_id]:
            first_vehicle_id = vehicle_id
            second_vehicle_id = other_vehicle_id
        else:
            first_vehicle_id = other_vehicle_id
            second_vehicle_id = vehicle_id

        print(f"Vehicle {first_vehicle_id} arrived first on edge {current_edge}. Managing shared edge scenario.")

        # Speed adjustment: Give the first vehicle priority, and adjust the speed of the second vehicle
        speed_adjustment_factor = 0.8  # Example: The second vehicle reduces speed to 80% of its original speed
        self._adjust_speed(second_vehicle_id, current_edge, speed_adjustment_factor)

        # Optionally, you could add logic to further manage priorities or determine right-of-way
        # This could involve stopping one vehicle temporarily or other forms of coordination

        # Log the shared edge scenario
        print(f"Vehicle {first_vehicle_id} has priority on edge {current_edge}. "
              f"Vehicle {second_vehicle_id} speed adjusted.")

    def _adjust_speed(self, vehicle_id, current_edge, adjustment_factor):
        """
        Adjust the speed of the specified vehicle on the given edge.

        :param vehicle_id: The ID of the vehicle whose speed is being adjusted.
        :param current_edge: The edge where the speed adjustment is being applied.
        :param adjustment_factor: The factor by which to adjust the vehicle's speed (e.g., 0.8 for 80%).
        """
        # Find the vehicle's original speed
        for edge_key, edge_data in self.edge_info.items():
            if edge_key == current_edge and vehicle_id in edge_data['vehicles_on_edge']:
                original_speed = edge_data['maxspeed']
                adjusted_speed = original_speed * adjustment_factor
                # Update the edge information with the adjusted speed (for the specific vehicle)
                print(f"Vehicle {vehicle_id} on edge {current_edge} speed adjusted from {original_speed} to {adjusted_speed}.")
                break

    def add_initial_signal_states(self, num_signals=4):
        """Randomly assigns initial signal states and delays to selected nodes."""
        nodes = list(self.node_info.keys())
        selected_nodes = random.sample(nodes, num_signals)
        for node in selected_nodes:
            initial_state = random.choice(self.signal_states)
            delay = random.randint(35, 60)
            self.node_info[node]['signal_state'] = initial_state
            self.node_info[node]['signal_index'] = self.signal_states.index(initial_state)
            self.node_info[node]['delay'] = delay
            print(f"Node {node} assigned initial signal state: {initial_state} with delay: {delay} seconds")

    def update_signal_states(self):
        """Updates the signal states based on random timing in a non-blocking manner."""
        current_time = time.time()
        for node, info in self.node_info.items():
            if info['signal_state'] is not None:
                elapsed_time = current_time - self.start_time
                if elapsed_time >= info['delay']:
                    # Update the signal state
                    info['signal_index'] = (info['signal_index'] + 1) % len(self.signal_states)
                    info['signal_state'] = self.signal_states[info['signal_index']]
                    print(f"Node {node} updated to signal state: {info['signal_state']} after delay: {info['delay']} seconds")
                    # Reset the delay timer
                    info['delay'] = random.randint(35, 60)
                    self.start_time = current_time

    def get_signal_states(self):
        """Returns the current signal states."""
        return {node: info['signal_state'] for node, info in self.node_info.items()}
