import osmnx as ox
import pickle
import os

os.makedirs("backend/data", exist_ok=True)

ox.settings.use_cache = True
ox.settings.timeout = 300
ox.settings.overpass_url = "https://gall.openstreetmap.de/api"

print("Extracting IIT Bombay walking network...")

G = ox.graph_from_point(
    (19.1334, 72.9133),
    dist=1500,
    network_type="all"
)

print(f"Nodes: {len(G.nodes)}, Edges: {len(G.edges)}")

with open("backend/data/graph.pkl", "wb") as f:
    pickle.dump(G, f)

print("Graph saved successfully")
ox.plot_graph(G)