import networkx as nx
import matplotlib.pyplot as plt

# Initialize the directed graph
G = nx.DiGraph()

# Define nodes with attributes (intersections and non-intersections)
nodes_with_attributes = {
    1: {'type': 'non-intersection'}, 2: {'type': 'non-intersection'},
    3: {'type': 'intersection'}, 4: {'type': 'intersection'},
    5: {'type': 'intersection'}, 6: {'type': 'intersection'},
    7: {'type': 'intersection'}, 8: {'type': 'non-intersection'},
    9: {'type': 'non-intersection'}, 10: {'type': 'intersection'},
    11: {'type': 'intersection'}, 12: {'type': 'non-intersection'}
}

# Add nodes to the graph with attributes
for node, attrs in nodes_with_attributes.items():
    G.add_node(node, **attrs)

# Define edges (road segments between nodes)
edges = [
    (1, 3), (2, 3), (3, 4), (4, 5), (4, 6), (5, 7), 
    (6, 7), (7, 8), (8, 9), (9, 10), (10, 11), (11, 12),
    (3, 6), (5, 10), (7, 11)  # Additional connections for more complexity
]

# Add the edges to the graph
G.add_edges_from(edges)

# Visualization - Color nodes based on their type
node_colors = ['red' if G.nodes[node]['type'] == 'intersection' else 'blue' for node in G.nodes]

# Generate positions for all nodes
pos = nx.spring_layout(G)

# Draw the graph
nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=700, edge_color='gray')

# Add a legend
plt.legend(handles=[
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Intersection'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='Non-Intersection')
])

# Show the plot
plt.show()

# Save the graph visualization to a file
plt.savefig("networkx_12_node_graph.png", dpi=300, bbox_inches='tight')
