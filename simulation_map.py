import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import random
import time

# latitude and longitude for a portion of Waterloo, Ontario
bbox = (43.4680, 43.4760, -80.5350, -80.5200)  # (south, north, west, east)
default_maxspeed = 50

# Download the street network data for the specified bounding box
G = ox.graph_from_bbox(*bbox, network_type='drive')

# Plot the graph with adjusted parameters for better visibility
fig, ax = ox.plot_graph(
    G, 
    node_size=30,         
    edge_linewidth=2,
    edge_color='lightblue'
)

# Save the plot as a PNG file locally
# fig.savefig("waterloo_larger_area.png", dpi=300, bbox_inches='tight')
plt.close(fig)

# Initial signal states and their order
# signal_states = ['green', 'yellow', 'red']
signal_states = ['green', 'red']

# Function to add initial random signal states and delays to selected nodes
def add_initial_signal_states(graph, num_signals=5):
    nodes = list(graph.nodes)
    selected_nodes = random.sample(nodes, num_signals)
    for node in selected_nodes:
        initial_state = random.choice(signal_states)
        delay = random.randint(45, 60)  # Assign a random delay between 45 and 60 seconds
        graph.nodes[node]['signal_state'] = initial_state
        graph.nodes[node]['signal_index'] = signal_states.index(initial_state)
        graph.nodes[node]['delay'] = delay  # Store the delay for this node
        print(f"Node {node} assigned initial signal state: {initial_state} with delay: {delay} seconds")

# Function to update signal states based on individual delays
def update_signal_states(graph):
    for node, data in graph.nodes(data=True):
        if 'signal_state' in data:
            # Wait for the specific delay time for this node before updating its state
            time.sleep(data['delay'])
            # Update the signal index (mod 3 to cycle through 0, 1, 2)
            data['signal_index'] = (data['signal_index'] + 1) % len(signal_states)
            data['signal_state'] = signal_states[data['signal_index']]
            print(f"Node {node} updated to signal state: {data['signal_state']} after delay: {data['delay']} seconds")

# Add initial signal states and delays to 5 random nodes
add_initial_signal_states(G, num_signals=5)

# Iterate through the edges and set maxspeed if it is None
for u, v, key, data in G.edges(keys=True, data=True):
    if data.get('maxspeed') is None:
        data['maxspeed'] = default_maxspeed
        print(f"Set default maxspeed for edge from {u} to {v}: {data['maxspeed']} km/h")


# Simulate 10 cycles of signal updates
for cycle in range(1):
    print(f"--- Cycle {cycle + 1} ---")
    update_signal_states(G)
    print("--- Signal states updated ---")

# Function to print graph information
def custom_info(graph):
    num_nodes = graph.number_of_nodes()
    num_edges = graph.number_of_edges()
    info_str = f"Graph has {num_nodes} nodes and {num_edges} edges"
    return info_str


# Example: List edges and their relevant attributes
for u, v, key, data in G.edges(keys=True, data=True):
    length = data.get('length', None)  # Retrieve the length of the road segment
    maxspeed = data.get('maxspeed', None)  # Retrieve the speed limit (can be a list)
    oneway = data.get('oneway', None)  # Retrieve whether the road is one-way
    
    # Print the retrieved information
    print(f"Edge from {u} to {v}:")
    print(f"  Length: {length} meters")
    print(f"  Max Speed: {maxspeed}")
    print(f"  One-Way: {oneway}")


print(custom_info(G))