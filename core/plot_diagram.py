import matplotlib.pyplot as plt
import networkx as nx
import os


def plot_routes_diagram(extracted_routes):
    G = nx.DiGraph()
    for file, routes in extracted_routes.items():
        for route in routes:
            path = route.split("'")[1]  # Extracting the path
            methods = route.split("'")[3]  # Extracting the HTTP methods
            node_label = f"{path}\n({methods})"
            G.add_node(node_label)
            G.add_edge(file.replace(".py", ""), node_label)  # Connecting routes to their respective files

    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)  # Positioning the nodes
    nx.draw(G, pos, with_labels=True, node_color="skyblue", node_size=3000, edge_color="gray", linewidths=1, font_size=10)

    plt.title("Visual Diagram of Routes in Project")
    plt.show()


def extract_routes_from_file(file_path):
    routes = []
    with open(file_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            if "@" in line and "route(" in line:
                routes.append(line.strip())
    return routes


def extract_all_routes():
    route_files = ["account_routes.py", "transaction_routes.py", "user_routes.py"]
    routes_directory_path = "routes"  # Update this path to the correct one
    extracted_routes = {}

    for file_name in route_files:
        file_path = os.path.join(routes_directory_path, file_name)
        routes = extract_routes_from_file(file_path)
        extracted_routes[file_name] = routes

    return extracted_routes


def plot_detailed_routes_diagram(extracted_routes):
    G = nx.DiGraph()
    for file, routes in extracted_routes.items():
        for route in routes:
            path = route.split("'")[1]  # Extracting the path
            methods = route.split("'")[3]  # Extracting the HTTP methods
            node_label = f"{path}\n({methods})"
            G.add_node(node_label)
            G.add_edge(file.replace(".py", ""), node_label)  # Connecting routes to their respective files

    plt.figure(figsize=(16, 12))
    pos = nx.spring_layout(G, seed=42)  # Positioning the nodes
    nx.draw(G, pos, with_labels=True, node_color="skyblue", node_size=3000, edge_color="gray", linewidths=1, font_size=10)

    plt.title("Detailed Visual Diagram of Routes in Project")
    plt.show()
