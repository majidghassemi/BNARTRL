import osmnx as ox
import networkx as nx

class TrafficNetwork:
    def __init__(self, bbox, default_maxspeed=50):
        self.bbox = bbox
        self.default_maxspeed = default_maxspeed
        self.graph = None
        self.node_info = {}
        self.edge_info = {}
        self.callbacks = []
        self._initialize_graph()

    def _initialize_graph(self):
        """Initialize the graph and populate node and edge information."""
        self.graph = ox.graph_from_bbox(*self.bbox, network_type='drive')
        self._populate_node_info()
        self._populate_edge_info()

    def _populate_node_info(self):
        """Populate node information in the node_info dictionary."""
        for node, data in self.graph.nodes(data=True):
            self.node_info[node] = {
                'signal_state': data.get('signal_state', None),
                'position': (data.get('x', None), data.get('y', None)),
                'connected_edges': list(self.graph.edges(node)),
            }

    def _populate_edge_info(self):
        """Populate edge information in the edge_info dictionary."""
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            if data.get('maxspeed') is None:
                data['maxspeed'] = self.default_maxspeed  # Set default maxspeed if not present

            self.edge_info[(u, v, key)] = {
                'start_node': u,
                'end_node': v,
                'length': data.get('length', None),
                'maxspeed': data['maxspeed'],
                'traffic_density': data.get('traffic_density', 0),  # Ensure traffic_density exists
            }

    def register_callback(self, callback):
        """Register a callback function to be called on signal state updates."""
        self.callbacks.append(callback)

    def update_signal_states(self):
        """Update the signal states for all nodes and notify registered callbacks."""
        signal_states = ['green', 'yellow', 'red']
        updated_signals = {}
        for node, info in self.node_info.items():
            current_state = info['signal_state']
            if current_state:
                next_index = (signal_states.index(current_state) + 1) % len(signal_states)
                self.node_info[node]['signal_state'] = signal_states[next_index]
                updated_signals[node] = signal_states[next_index]
        
        # Notify all registered callbacks of the update
        for callback in self.callbacks:
            callback(updated_signals)

    def get_signal_states(self):
        """Return the current signal states."""
        return {node: info['signal_state'] for node, info in self.node_info.items()}

    def print_node_info(self):
        """Prints the node information."""
        for node, info in self.node_info.items():
            print(f"Node {node}: Signal State = {info['signal_state']}, "
                  f"Position = {info['position']}, Connected Edges = {info['connected_edges']}")

    def print_edge_info(self):
        """Prints the edge information."""
        for edge, info in self.edge_info.items():
            print(f"Edge {edge}: Start Node = {info['start_node']}, End Node = {info['end_node']}, "
                  f"Length = {info['length']} meters, Max Speed = {info['maxspeed']} km/h, "
                  f"Traffic Density = {info['traffic_density']}")
