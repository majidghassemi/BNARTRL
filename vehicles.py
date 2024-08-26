class Vehicle:
    def __init__(self, vehicle_id, start_node, destination_node, speed=25):
        self.vehicle_id = vehicle_id
        self.current_position = start_node  # Start node of the vehicle
        self.destination = destination_node
        self.speed = speed
        self.state = 'moving'  # 'stopped', 'moving'
        self.route = []  # List of nodes representing the planned route

    def update_position(self, new_position):
        self.current_position = new_position

    def stop(self):
        self.state = 'stopped'

    def move(self):
        self.state = 'moving'
