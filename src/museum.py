from entities import Room, Artwork
from ontology.art import artworks
import random
from collections import deque
from typing import List, Set, Tuple
from dataclasses import dataclass

# --- Museum Creation ---

# Initialize Rooms
rooms = {
    "1": Room(1, "Museum 1", is_entry=True, is_exit=True, is_stairs=False, is_elevator=False, room_name="Room 1"),
    "2": Room(2, "Museum 1", is_entry=False, is_exit=False, is_stairs=False, is_elevator=False, room_name="Room 2"),
    "3": Room(3, "Museum 1", is_entry=False, is_exit=False, is_stairs=False, is_elevator=False, room_name="Room 3"),
    "4": Room(4, "Museum 1", is_entry=False, is_exit=False, is_stairs=False, is_elevator=False, room_name="Room 4"),
    "5": Room(5, "Museum 1", is_entry=False, is_exit=False, is_stairs=False, is_elevator=False, room_name="Room 5"),
    "6": Room(6, "Museum 1", is_entry=False, is_exit=False, is_stairs=False, is_elevator=False, room_name="Room 6"),
    "7": Room(7, "Museum 1", is_entry=False, is_exit=False, is_stairs=False, is_elevator=False, room_name="Room 7"),
    "8": Room(8, "Museum 1", is_entry=False, is_exit=False, is_stairs=False, is_elevator=False, room_name="Room 8"),
    "9": Room(9, "Museum 1", is_entry=False, is_exit=True, is_stairs=False, is_elevator=False, room_name="Room 9"),
    "elevator_1": Room(10, "Museum 1", is_entry=False, is_exit=False, is_stairs=False, is_elevator=True, room_name="Elevator 1"),
    "elevator_2": Room(11, "Museum 1", is_entry=False, is_exit=False, is_stairs=False, is_elevator=True, room_name="Elevator 2"),
    "stairs_1": Room(12, "Museum 1", is_entry=False, is_exit=False, is_stairs=True, is_elevator=False, room_name="Stairs 1"),
    "stairs_2": Room(13, "Museum 1", is_entry=False, is_exit=False, is_stairs=True, is_elevator=False, room_name="Stairs 2"),
    "stairs_3": Room(14, "Museum 1", is_entry=False, is_exit=False, is_stairs=True, is_elevator=False, room_name="Stairs 3"),
}

# --- Room Connections ---
# Horizontal connections
rooms["1"].adjacent_rooms = [rooms["2"], rooms["elevator_1"]]
rooms["2"].adjacent_rooms = [rooms["1"], rooms["3"], rooms["stairs_1"]]
rooms["3"].adjacent_rooms = [rooms["2"], rooms["stairs_2"]]

rooms["4"].adjacent_rooms = [rooms["5"], rooms["elevator_1"], rooms["elevator_2"]]
rooms["5"].adjacent_rooms = [rooms["4"], rooms["6"], rooms["stairs_1"]]
rooms["6"].adjacent_rooms = [rooms["5"], rooms["stairs_2"], rooms["stairs_3"]]

rooms["7"].adjacent_rooms = [rooms["8"], rooms["elevator_2"]]
rooms["8"].adjacent_rooms = [rooms["7"], rooms["9"]]
rooms["9"].adjacent_rooms = [rooms["8"], rooms["stairs_3"]]

# Elevators connections
rooms["elevator_1"].adjacent_rooms = [rooms["1"], rooms["4"]]
rooms["elevator_2"].adjacent_rooms = [rooms["4"], rooms["7"]]

# Stairs connections
rooms["stairs_1"].adjacent_rooms = [rooms["2"], rooms["5"]]
rooms["stairs_2"].adjacent_rooms = [rooms["3"], rooms["6"]]
rooms["stairs_3"].adjacent_rooms = [rooms["6"], rooms["9"]]


# --- Artworks ---
# Assign artworks to rooms
# Normal roots (the ones that are not in the elevator or stairs)

normal_rooms = [rooms["1"], rooms["2"], rooms["3"], rooms["4"], rooms["5"], rooms["6"], rooms["7"], rooms["8"], rooms["9"]]

random.seed(42)
for artwork in artworks.keys(): # Artwork ids
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

# --- Test ---
if __name__ == "__main__":
    artworks_to_visit = [5357, 18709, 28067]
    route = find_route(artworks_to_visit, only_elevators=False)
    for room_id in route:
        room_instance = next(room for room in rooms.values() if room.room_id == room_id)
        print(f"Room {room_instance.room_id} ({room_instance.room_name}) --> {room_instance.artworks_id_in_room}")
    