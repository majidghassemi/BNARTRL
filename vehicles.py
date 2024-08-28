class Vehicle:
    def __init__(self, vehicle_id, start_node, destination_node, speed=25):
        self.vehicle_id = vehicle_id
        self.current_position = start_node
        self.destination = destination_node
        self.speed = speed
        self.state = 'waiting'
        self.route = []
        self.next_position = None

    def initialize_route(self, route):
        """Initialize the vehicle's route as determined by the CTCU."""
        self.route = route
        if self.route:
            self.next_position = self.route.pop(0)
            self.state = 'moving'

    def update_position(self, new_position):
        """Update the vehicle's current position."""
        self.current_position = new_position
        if self.current_position == self.destination:
            self.arrive()

    def move(self, traffic_network):
        """Move the vehicle to the next node along its route, updating the traffic network accordingly."""
        if self.state == 'moving' and self.next_position:
            traffic_network.update_traffic_density(self.current_position, self.next_position, self.vehicle_id)

            self.update_position(self.next_position)

            if self.route:
                self.next_position = self.route.pop(0)  # Move to the next node in the route
            else:
                self.arrive()  # If there's no more nodes, the vehicle has arrived
        elif self.state == 'rerouting':
            pass

    def stop(self):
        """Stop the vehicle, typically used when the vehicle reaches its destination or in case of congestion."""
        self.state = 'stopped'

    def reroute(self, new_route):
        """Assign a new route to the vehicle, typically in response to traffic conditions."""
        self.state = 'rerouting'
        self.route = new_route
        if self.route:
            self.next_position = self.route.pop(0)
            self.state = 'moving'

    def arrive(self):
        """Mark the vehicle as arrived at its destination."""
        self.state = 'arrived'
        self.next_position = None
        print(f"Vehicle {self.vehicle_id} has arrived at its destination.")

    def is_moving(self):
        """Check if the vehicle is currently moving."""
        return self.state == 'moving'

    def enter_network(self):
        """Set the vehicle's state to entering the network."""
        self.state = 'entering'
        # Additional logic to handle the vehicle's entry into the network

    def exit_network(self):
        """Set the vehicle's state to exiting the network."""
        self.state = 'exiting'
        # Additional logic to handle the vehicle's exit from the network

    def share_edge(self):
        """Set the vehicle's state to sharing an edge with other vehicles."""
        self.state = 'sharing'
        # Additional logic to handle vehicle behavior when sharing a road segment
