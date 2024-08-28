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
                'vehicles_on_edge': []  # Track vehicles on this edge
            }

    def update_traffic_density(self, current_position, next_position, vehicle_id):
        """Update traffic density on the edge from current_position to next_position."""
        # Define the edge the vehicle is leaving (current_edge)
        current_edge = (current_position, next_position)
        
        # Define the edge the vehicle is moving to (next_edge)
        next_edge = (current_position, next_position)

        # Update the edge the vehicle is leaving
        if current_edge in self.edge_info:
            if vehicle_id in self.edge_info[current_edge]['vehicles_on_edge']:
                self.edge_info[current_edge]['vehicles_on_edge'].remove(vehicle_id)
                self.edge_info[current_edge]['traffic_density'] -= 1
        
        # Update the edge the vehicle is moving to
        if next_edge in self.edge_info:
            self.edge_info[next_edge]['vehicles_on_edge'].append(vehicle_id)
            self.edge_info[next_edge]['traffic_density'] += 1

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
