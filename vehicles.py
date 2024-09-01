import time


class Vehicle:
    def __init__(self, vehicle_id, start_node, destination_node, speed=25):
        self.vehicle_id = vehicle_id
        self.current_position = start_node
        self.destination = destination_node
        self.speed = speed
        self.state = 'waiting'
        self.route = []
        self.next_position = None

    def initialize_route(self, traffic_network, ctc_unit):
        """
        Initialize the vehicle's route as determined by the CTCU.
        The route is dynamically calculated based on real-time traffic conditions.
        
        :param traffic_network: The traffic network instance.
        :param ctc_unit: The Central Traffic Control Unit (CTCU) instance.
        """
        # Request the CTCU to calculate the best route using the BNART heuristic
        calculated_route = ctc_unit.calculate_best_route(self.current_position, self.destination, traffic_network)
        
        if calculated_route:
            self.route = calculated_route
            self.next_position = self.route.pop(0)
            self.state = 'moving'
        else:
            self.state = 'waiting'  # If no route could be calculated, remain in the waiting state

        print(f"Vehicle {self.vehicle_id} initialized with route: {self.route}")


    def update_position(self, new_position, traffic_network):
        """
        Update the vehicle's current position, taking into account delays due to traffic conditions
        and intersections.

        :param new_position: The new position to which the vehicle is moving.
        :param traffic_network: The traffic network instance to check for traffic conditions.
        """
        # Calculate any additional delay based on traffic conditions
        current_edge = (self.current_position, new_position)
        
        if current_edge in traffic_network.edge_info:
            traffic_density = traffic_network.edge_info[current_edge]['traffic_density']
            max_speed = traffic_network.edge_info[current_edge]['maxspeed']
            road_length = traffic_network.edge_info[current_edge]['length']

            # Calculate travel time with potential delays
            travel_time = road_length / max_speed  # basic travel time at max speed
            congestion_delay = traffic_density * (road_length / max_speed) * 0.01  # delay due to congestion
            intersection_delay = traffic_network.node_info.get(new_position, {}).get('delay', 0)  # delay at intersections

            # Total delay
            total_delay = congestion_delay + intersection_delay

            # Log the calculated delays for debugging purposes
            print(f"Vehicle {self.vehicle_id} moving from {self.current_position} to {new_position} "
                f"with delays - Congestion: {congestion_delay:.2f}s, Intersection: {intersection_delay:.2f}s, "
                f"Total: {total_delay:.2f}s")

            # Update the current position after applying the delay
            self.current_position = new_position
            time.sleep(total_delay)  # Simulate the delay in movement
        else:
            # If the edge info is not available, just move the vehicle to the new position
            self.current_position = new_position

        # Check if the vehicle has reached its destination
        if self.current_position == self.destination:
            self.arrive()



    def move(self, traffic_network, ctc_unit):
        """
        Move the vehicle to the next node along its route, updating the traffic network accordingly.
        If the vehicle encounters congestion, it may request a reroute from the CTCU.

        :param traffic_network: The traffic network instance to update traffic conditions.
        :param ctc_unit: The Central Traffic Control Unit (CTCU) instance for rerouting decisions.
        """
        if self.state == 'moving' and self.next_position:
            # Update the traffic density for the current and next positions
            traffic_network.update_traffic_density(self.current_position, self.next_position, self.vehicle_id)

            # Check the traffic condition on the next edge
            current_edge = (self.current_position, self.next_position)
            traffic_density = traffic_network.edge_info.get(current_edge, {}).get('traffic_density', 0)
            
            # Decision-making based on traffic conditions
            if traffic_density > ctc_unit.threshold_density:  # Assume the CTCU has a threshold for rerouting
                print(f"Vehicle {self.vehicle_id} encountering congestion on edge {current_edge}. Requesting reroute.")
                new_route = ctc_unit.calculate_best_route(self.current_position, self.destination, traffic_network)
                self.reroute(new_route)
            else:
                # Proceed to the next position
                self.update_position(self.next_position, traffic_network)
                
                # Move to the next node in the route if available
                if self.route:
                    self.next_position = self.route.pop(0)
                else:
                    self.arrive()  # If there's no more nodes, the vehicle has arrived

        elif self.state == 'rerouting':
            # If in rerouting state, attempt to reroute or stop if no viable route is found
            if self.route:
                self.state = 'moving'
                self.next_position = self.route.pop(0)
                print(f"Vehicle {self.vehicle_id} resumed moving after reroute.")
            else:
                self.stop()  # If no route is found, stop the vehicle
                print(f"Vehicle {self.vehicle_id} could not find a viable route and has stopped.")

        elif self.state == 'stopped':
            # If the vehicle is stopped, check for possible conditions to resume or remain stopped
            if self.next_position:
                # Check if the stop condition (e.g., temporary congestion) has been resolved
                traffic_density = traffic_network.edge_info.get(current_edge, {}).get('traffic_density', 0)
                if traffic_density <= ctc_unit.threshold_density:
                    self.state = 'moving'
                    print(f"Vehicle {self.vehicle_id} is resuming movement after stop.")
                else:
                    print(f"Vehicle {self.vehicle_id} remains stopped due to continued congestion.")
            else:
                print(f"Vehicle {self.vehicle_id} remains stopped with no further route planned.")


        def stop(self, reason="unknown"):
            """
            Stop the vehicle, typically used when the vehicle reaches its destination, in case of congestion, or other reasons.
            
            :param reason: The reason for stopping the vehicle (e.g., "destination", "congestion", "emergency").
            """
            self.state = 'stopped'
            self.next_position = None
            
            # Log the stop event with the reason
            print(f"Vehicle {self.vehicle_id} has stopped. Reason: {reason}.")
            
            # Optionally, communicate the stop event to the CTCU
            # traffic_network.report_stop(self.vehicle_id, self.current_position, reason)
            
            # Additional logic can be added here if necessary, e.g., handling emergency stops or recalculating routes


    def reroute(self, traffic_network, destination_node, ctc_unit):
        """
        Assign a new route to the vehicle, typically in response to traffic conditions.
        The rerouting logic is based on the BNART approach to find the best path that minimizes travel time.

        :param traffic_network: The current state of the traffic network.
        :param destination_node: The final destination for the vehicle.
        :param ctc_unit: The Central Traffic Control Unit (CTCU) instance for additional rerouting decisions.
        """
        # self.state = 'rerouting'
        current_node = self.current_position
        
        # Step 1: Get neighbors of the current node
        neighbors = traffic_network.get_neighbors(current_node)
        
        best_neighbor = None
        best_value = float('inf')
        
        # Step 2: Evaluate each neighbor based on traffic and distance to destination
        for neighbor in neighbors:
            if neighbor in self.route:  # Avoid loops
                continue

            traffic_time = traffic_network.get_traffic_time(current_node, neighbor)
            distance_to_destination = traffic_network.get_distance(neighbor, destination_node)
            
            # Normalize the evaluation metric (considering both traffic time and distance)
            evaluation_value = traffic_time + distance_to_destination
            
            if evaluation_value < best_value:
                best_value = evaluation_value
                best_neighbor = neighbor
        
        # Step 3: Update the route
        if best_neighbor:
            self.route = [best_neighbor]  # Start the new route with the best neighbor
            while best_neighbor != destination_node:
                neighbors = traffic_network.get_neighbors(best_neighbor)
                best_value = float('inf')
                next_best_neighbor = None
                
                for neighbor in neighbors:
                    if neighbor in self.route:  # Avoid loops
                        continue
                    
                    traffic_time = traffic_network.get_traffic_time(best_neighbor, neighbor)
                    distance_to_destination = traffic_network.get_distance(neighbor, destination_node)
                    
                    evaluation_value = traffic_time + distance_to_destination
                    
                    if evaluation_value < best_value:
                        best_value = evaluation_value
                        next_best_neighbor = neighbor
                
                if next_best_neighbor:
                    best_neighbor = next_best_neighbor
                    self.route.append(best_neighbor)
                else:
                    break  # No more valid neighbors
            
            self.next_position = self.route.pop(0)
            self.state = 'moving'
            print(f"Vehicle {self.vehicle_id} has been rerouted to new route: {self.route}")
        else:
            self.stop()  # If no valid reroute is found, stop the vehicle
            print(f"Vehicle {self.vehicle_id} could not be rerouted and has stopped.")


    def arrive(self, traffic_network):
        """
        Mark the vehicle as arrived at its destination and handle post-arrival processes.
        
        :param traffic_network: The current state of the traffic network.
        """
        self.state = 'arrived'
        self.next_position = None
        
        # Log the arrival event
        print(f"Vehicle {self.vehicle_id} has arrived at its destination (Node {self.destination}).")
        
        # Update the traffic network to reflect that the vehicle has completed its journey
        traffic_network.update_vehicle_arrival(self.vehicle_id, self.current_position)
        
        # Optionally, notify the CTCU about the arrival
        # traffic_network.notify_ctcu_of_arrival(self.vehicle_id, self.current_position)
        
        # Free up any resources or clear data related to the vehicle's journey
        self.route = []
        self.current_position = None  # Optionally reset position if necessary
        

    def is_moving(self):
        """Check if the vehicle is currently moving."""
        # Check if the vehicle's state is 'moving' or any other state that implies motion
        return self.state in ['moving', 'rerouting']

    def enter_network(self, traffic_network, ctc_unit):
        """
        Set the vehicle's state to 'entering' the network and perform the necessary initialization steps.
        This includes potentially interacting with the CTCU for initial route assignment and updating the traffic network.

        :param traffic_network: The traffic network instance that manages the road system.
        :param ctc_unit: The Central Traffic Control Unit (CTCU) instance for route assignment.
        """
        # Set the initial state of the vehicle
        self.state = 'entering'
        
        # Notify the traffic network that a new vehicle is entering
        traffic_network.add_vehicle(self.vehicle_id, self.current_position)
        
        # Request an initial route from the CTCU
        initial_route = ctc_unit.calculate_best_route(self.current_position, self.destination, traffic_network)
        
        # Initialize the vehicle's route with the provided initial route
        if initial_route:
            self.initialize_route(initial_route)
            print(f"Vehicle {self.vehicle_id} has entered the network and is starting with route: {self.route}")
        else:
            self.state = 'waiting'  # If no initial route is available, set the vehicle to 'waiting'
            print(f"Vehicle {self.vehicle_id} has entered the network but is waiting for a route.")


    def exit_network(self, traffic_network, ctc_unit):
        """
        Set the vehicle's state to 'exiting' the network and perform the necessary cleanup steps.
        This includes notifying the traffic network and the CTCU that the vehicle is leaving the system.

        :param traffic_network: The traffic network instance that manages the road system.
        :param ctc_unit: The Central Traffic Control Unit (CTCU) instance for managing traffic.
        """
        # Set the state to 'exiting'
        self.state = 'exiting'
        
        # Notify the traffic network that the vehicle is exiting
        traffic_network.remove_vehicle(self.vehicle_id, self.current_position)
        
        # Notify the CTCU that the vehicle is exiting
        ctc_unit.notify_vehicle_exit(self.vehicle_id)
        
        # Perform any additional cleanup or logging
        print(f"Vehicle {self.vehicle_id} has exited the network from position: {self.current_position}")
        
        # Reset the vehicle state or perform any other required finalization
        self.state = 'exited'
        self.current_position = None
        self.route = []
        self.next_position = None


    def share_edge(self, traffic_network, other_vehicle_id):
        """
        Manage the vehicle's behavior when sharing an edge with another vehicle.
        The vehicle will remain in a 'moving' state, but additional logic can be applied to handle
        sharing scenarios.

        :param traffic_network: The traffic network instance to update traffic conditions.
        :param other_vehicle_id: The ID of the other vehicle sharing the edge.
        """
        current_edge = (self.current_position, self.next_position)
        
        # Example logic: Check if the other vehicle should move first based on some criteria
        if traffic_network.should_yield(self.vehicle_id, other_vehicle_id):
            print(f"Vehicle {self.vehicle_id} is yielding to Vehicle {other_vehicle_id} on edge {current_edge}.")
            self.state = 'waiting'  # Temporarily wait if yielding
        else:
            print(f"Vehicle {self.vehicle_id} is moving ahead of Vehicle {other_vehicle_id} on edge {current_edge}.")
            self.state = 'moving'  # Continue moving

