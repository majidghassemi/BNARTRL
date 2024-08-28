import osmnx as ox

class GraphGenerator:
    def __init__(self, bbox, network_type='drive', default_maxspeed=50):
        self.bbox = bbox
        self.network_type = network_type
        self.default_maxspeed = default_maxspeed
        self.graph = None

    def generate_graph(self):
        """Generates the graph using OSMnx for the specified bounding box."""
        self.graph = ox.graph_from_bbox(*self.bbox, network_type=self.network_type)
        self._set_default_maxspeed()
        return self.graph

    def _set_default_maxspeed(self):
        """Sets a default maxspeed for edges where it's missing."""
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            if data.get('maxspeed') is None:
                data['maxspeed'] = self.default_maxspeed
                print(f"Set default maxspeed for edge from {u} to {v}: {data['maxspeed']} km/h")

# Example usage:
# bbox = (43.4680, 43.4760, -80.5350, -80.5200)
# generator = GraphGenerator(bbox)
# graph = generator.generate_graph()