from dataclasses import dataclass, field
from typing import List, Dict
from collections import deque
import random
import networkx as nx
import matplotlib.pyplot as plt

# --- Entities and Ontology Definitions ---

@dataclass
class Room:
    room_id: int
    museum: str
    is_entry: bool
    is_exit: bool
    is_stairs: bool
    is_elevator: bool
    room_name: str
    adjacent_rooms: List['Room'] = field(default_factory=list)
    artworks_id_in_room: List[int] = field(default_factory=list)

# Sample artworks dictionary (Artwork ID mapped to Artwork Name)
artworks: Dict[int, str] = {
    5357: "Starry Night",
    18709: "Mona Lisa",
    28067: "The Scream",
    39456: "The Persistence of Memory",
    48290: "Girl with a Pearl Earring",
    57321: "The Night Watch",
    63485: "Guernica",
    71234: "The Kiss",
    82345: "The Birth of Venus",
    93456: "American Gothic"
}

# --- Museum Creation ---

# Initialize Rooms
rooms = {
    "1": Room(1, "Museum 1", is_entry=True, is_exit=False, is_stairs=False, is_elevator=False, room_name="Room 1"),
    "2": Room(2, "Museum 1", is_entry=False, is_exit=False, is_stairs=False, is_elevator=False, room_name="Room 2"),
    "3": Room(3, "Museum 1", is_entry=False, is_exit=False, is_stairs=False, is_elevator=False, room_name="Room 3"),
    "4": Room(4, "Museum 1", is_entry=False, is_exit=False, is_stairs=False, is_elevator=False, room_name="Room 4"),
    "5": Room(5, "Museum 1", is_entry=False, is_exit=False, is_stairs=False, is_elevator=False, room_name="Room 5"),
    "6": Room(6, "Museum 1", is_entry=False, is_exit=False, is_stairs=False, is_elevator=False, room_name="Room 6"),
    "7": Room(7, "Museum 1", is_entry=False, is_exit=False, is_stairs=False, is_elevator=False, room_name="Room 7"),
    "8": Room(8, "Museum 1", is_entry=False, is_exit=False, is_stairs=False, is_elevator=False, room_name="Room 8"),
    "9": Room(9, "Museum 1", is_entry=False, is_exit=True, is_stairs=False, is_elevator=False, room_name="Room 9"),
    "10": Room(10, "Museum 1", is_entry=False, is_exit=False, is_stairs=False, is_elevator=True, room_name="Elevator 1"),
    "11": Room(11, "Museum 1", is_entry=False, is_exit=False, is_stairs=False, is_elevator=True, room_name="Elevator 2"),
    "12": Room(12, "Museum 1", is_entry=False, is_exit=False, is_stairs=True, is_elevator=False, room_name="Stairs 1"),
    "13": Room(13, "Museum 1", is_entry=False, is_exit=False, is_stairs=True, is_elevator=False, room_name="Stairs 2"),
    "14": Room(14, "Museum 1", is_entry=False, is_exit=False, is_stairs=True, is_elevator=False, room_name="Stairs 3"),
}

# --- Room Connections ---
# Horizontal connections
rooms["1"].adjacent_rooms = [rooms["2"], rooms["10"]]
rooms["2"].adjacent_rooms = [rooms["1"], rooms["3"], rooms["12"]]
rooms["3"].adjacent_rooms = [rooms["2"], rooms["13"]]

rooms["4"].adjacent_rooms = [rooms["5"], rooms["10"], rooms["11"]]
rooms["5"].adjacent_rooms = [rooms["4"], rooms["6"], rooms["12"]]
rooms["6"].adjacent_rooms = [rooms["5"], rooms["13"], rooms["14"]]

rooms["7"].adjacent_rooms = [rooms["8"], rooms["11"]]
rooms["8"].adjacent_rooms = [rooms["7"], rooms["9"]]
rooms["9"].adjacent_rooms = [rooms["8"], rooms["14"]]

# Elevators connections
rooms["10"].adjacent_rooms = [rooms["1"], rooms["4"]]
rooms["11"].adjacent_rooms = [rooms["4"], rooms["7"]]

# Stairs connections
rooms["12"].adjacent_rooms = [rooms["2"], rooms["5"]]
rooms["13"].adjacent_rooms = [rooms["3"], rooms["6"]]
rooms["14"].adjacent_rooms = [rooms["6"], rooms["9"]]

# --- Artworks ---
# Assign artworks to rooms
# Normal rooms (the ones that are not in the elevator or stairs)

normal_room_keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

normal_rooms = [rooms[key] for key in normal_room_keys]

random.seed(42)
for artwork in artworks.keys():  # Artwork ids
    random_room = random.choice(normal_rooms)
    random_room.artworks_id_in_room.append(artwork)

@dataclass
class Node:
    room: Room
    rooms_path: List[Room]

def find_route(artworks_to_visit, only_elevators: bool = False):
    needed_rooms = []
    for artwork_id in artworks_to_visit:
        room = next(room for room in rooms.values() if artwork_id in room.artworks_id_in_room)
        if room not in needed_rooms:
            needed_rooms.append(room)

    entry_room = next(room for room in rooms.values() if room.is_entry)

    start_node = Node(room=entry_room, rooms_path=[entry_room])

    queue = deque([start_node])

    while queue:
        current_node = queue.popleft()

        if current_node.room.is_exit:
            if all(room in current_node.rooms_path for room in needed_rooms):
                return [room.room_id for room in current_node.rooms_path]

        for adjacent_room in current_node.room.adjacent_rooms:
            if only_elevators and adjacent_room.is_stairs:
                continue
            else:
                new_node = Node(room=adjacent_room, rooms_path=current_node.rooms_path + [adjacent_room])
                queue.append(new_node)

    return []

def plot_route(route: List[int]):
    G = nx.Graph()

    # Add all rooms as nodes
    for room in rooms.values():
        G.add_node(room.room_id, 
                   room=room.room_name,
                   is_entry=room.is_entry,
                   is_exit=room.is_exit,
                   is_stairs=room.is_stairs,
                   is_elevator=room.is_elevator)

    # Add edges based on adjacent rooms
    for room in rooms.values():
        for adjacent in room.adjacent_rooms:
            G.add_edge(room.room_id, adjacent.room_id)

    # Define node colors based on room types
    node_colors = []
    for node in G.nodes(data=True):
        room = node[1]
        if room['is_entry']:
            node_colors.append('green')
        elif room['is_exit']:
            node_colors.append('red')
        elif room['is_elevator']:
            node_colors.append('blue')
        elif room['is_stairs']:
            node_colors.append('orange')
        else:
            node_colors.append('lightblue')

    # Define edge colors based on connection types
    edge_colors = []
    for edge in G.edges():
        room1 = rooms[str(edge[0])] if str(edge[0]) in rooms else rooms[str(edge[0])]
        room2 = rooms[str(edge[1])] if str(edge[1]) in rooms else rooms[str(edge[1])]
        if room1.is_elevator and room2.is_elevator:
            edge_colors.append('blue')
        elif room1.is_stairs and room2.is_stairs:
            edge_colors.append('orange')
        elif (room1.is_elevator and not room2.is_elevator) or (room2.is_elevator and not room1.is_elevator):
            edge_colors.append('purple')
        elif (room1.is_stairs and not room2.is_stairs) or (room2.is_stairs and not room1.is_stairs):
            edge_colors.append('brown')
        else:
            edge_colors.append('black')

    pos = nx.spring_layout(G, seed=42)  # Positions for all nodes

    plt.figure(figsize=(14, 10))
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800, alpha=0.9)

    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2)

    # Draw labels
    labels = {room.room_id: room.room_name for room in rooms.values()}
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')

    # Highlight the route
    if route:
        route_edges = list(zip(route, route[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=route_edges, edge_color='red', width=4)

        # Highlight the nodes in the route
        nx.draw_networkx_nodes(G, pos, nodelist=route, node_color='yellow', node_size=1000, alpha=0.7)

    # Create custom legends
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Entry Room', markerfacecolor='green', markersize=15),
        Line2D([0], [0], marker='o', color='w', label='Exit Room', markerfacecolor='red', markersize=15),
        Line2D([0], [0], marker='o', color='w', label='Elevator Room', markerfacecolor='blue', markersize=15),
        Line2D([0], [0], marker='o', color='w', label='Stairs Room', markerfacecolor='orange', markersize=15),
        Line2D([0], [0], marker='o', color='w', label='Normal Room', markerfacecolor='lightblue', markersize=15),
        Line2D([0], [0], color='black', lw=2, label='Normal Connection'),
        Line2D([0], [0], color='blue', lw=2, label='Elevator Connection'),
        Line2D([0], [0], color='orange', lw=2, label='Stairs Connection'),
        Line2D([0], [0], color='red', lw=4, label='Route Path'),
        Line2D([0], [0], marker='o', color='w', label='Route Node', markerfacecolor='yellow', markersize=15)
    ]

    # Position the legend outside the plot area
    plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1), fontsize='medium')

    plt.title("Museum Layout and Route Visualization", fontsize=16)
    plt.axis('off')
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.show()

# --- Test ---
if __name__ == "__main__":
    artworks_to_visit = [5357, 18709, 28067]
    route = find_route(artworks_to_visit, only_elevators=True)
    print("Route Path:")
    for room_id in route:
        room_instance = next(room for room in rooms.values() if room.room_id == room_id)
        print(f"Room {room_instance.room_id} ({room_instance.room_name}) --> {room_instance.artworks_id_in_room}")

    # Plot the route
    plot_route(route)
