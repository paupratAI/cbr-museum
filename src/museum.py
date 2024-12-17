from entities import Room, Artwork
from ontology.art import artworks
import random
from collections import deque
from typing import List, Set, Tuple

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
for artwork in artworks.values():
    random_room = random.choice(normal_rooms)
    artwork.artwork_in_room = random_room

"""# Output to Verify Assignments
print("\n--- Artwork Assignments to Rooms ---")
for artwork in artworks.values():
    print(f"Artwork '{artwork.artwork_name}' (ID: {artwork.artwork_id}) is in '{artwork.artwork_in_room}'.")"""


def find_optimal_route(artwork_indices: List[int], reduced_mobility: bool = False) -> List[int]:
    """
    Finds the optimal route through the museum starting from an entry room,
    visiting all rooms containing the specified artworks, and exiting through an exit room.

    Parameters:
    - artwork_indices: List of integers representing the indices of artworks to visit.
    - reduced_mobility: If True, stairs cannot be used in the route.

    Returns:
    - A list of room_ids representing the optimal path. Returns an empty list if no path is found.
    """
    # Step 1: Map artwork indices to their respective rooms
    required_room_ids: Set[int] = set()
    for index in artwork_indices:
        artwork = artworks.get(index)
        if artwork and artwork.artwork_in_room:
            required_room_ids.add(artwork.artwork_in_room.room_id)
        else:
            raise ValueError(f"Artwork with index {index} does not exist or is not assigned to any room.")
    
    print('Step 1: Required Room IDs:', required_room_ids)

    if not required_room_ids:
        raise ValueError("No valid rooms found for the provided artwork indices.")

    # Step 2: Identify entry and exit rooms
    entry_room_ids: Set[int] = set()
    exit_room_ids: Set[int] = set()
    for room in rooms.values():
        if room.is_entry:
            entry_room_ids.add(room.room_id)
        if room.is_exit:
            exit_room_ids.add(room.room_id)

    print('Step 2: Entry Rooms:', entry_room_ids, 'Exit Rooms:', exit_room_ids)

    if not entry_room_ids:
        raise ValueError("No entry rooms defined in the museum.")
    if not exit_room_ids:
        raise ValueError("No exit rooms defined in the museum.")

    # Step 3: Initialize BFS
    queue: deque = deque()
    visited_states: Set[Tuple[int, Tuple[int, ...], Tuple[Tuple[int, int], ...]]] = set()

    for entry_room_id in entry_room_ids:
        initial_visited = set()
        if entry_room_id in required_room_ids:
            initial_visited.add(entry_room_id)
        
        initial_visitation_counts = {entry_room_id: 1}
        initial_path = [entry_room_id]
        
        # Create state key
        state_key = (
            entry_room_id,
            tuple(sorted(initial_visited)),
            tuple(sorted(initial_visitation_counts.items()))
        )
        
        queue.append((entry_room_id, initial_visited, initial_visitation_counts, initial_path))
        visited_states.add(state_key)

    print('Step 3: Initial Queue and Visited States Initialized.')

    # Step 4: BFS Loop
    while queue:
        current_room_id, visited_required, visitation_counts, path = queue.popleft()
        
        print(f"Exploring Room {current_room_id}, Visited Required: {visited_required}, Path: {path}")

        # Check if current room is an exit and all required rooms have been visited
        if current_room_id in exit_room_ids and visited_required == required_room_ids:
            print("Optimal Route Found!")
            return path

        current_room = rooms.get(str(current_room_id))
        if not current_room:
            continue  # Invalid room_id, skip

        # Explore adjacent rooms
        for adjacent_room in current_room.adjacent_rooms:
            # Constraint: If reduced_mobility is True, skip stairs
            if reduced_mobility and adjacent_room.is_stairs:
                continue

            next_room_id = adjacent_room.room_id

            # Update visited required rooms
            new_visited_required = set(visited_required)
            if next_room_id in required_room_ids:
                new_visited_required.add(next_room_id)

            # Update visitation counts
            new_visitation_counts = visitation_counts.copy()
            new_visitation_counts[next_room_id] = new_visitation_counts.get(next_room_id, 0) + 1

            # Prune if the room has been visited more times than its connections
            room_connections = len(adjacent_room.adjacent_rooms)
            if new_visitation_counts[next_room_id] > room_connections:
                print(f"Pruning Room {next_room_id}: Visited {new_visitation_counts[next_room_id]} times, allowed {room_connections}.")
                continue

            # Create a new path
            new_path = path + [next_room_id]

            # Create state key
            state_key = (
                next_room_id,
                tuple(sorted(new_visited_required)),
                tuple(sorted(new_visitation_counts.items()))
            )

            if state_key not in visited_states:
                visited_states.add(state_key)
                queue.append((next_room_id, new_visited_required, new_visitation_counts, new_path))
                print(f"Enqueued Room {next_room_id}, Visited Required: {new_visited_required}, Path: {new_path}")

    # If BFS completes without finding a valid path
    print("No optimal path found.")
    return []


# Example Usage

# Example: Artworks to visit
artwork_indices = [5357, 18709, 28067]  # List of artwork IDs

# Find optimal route
try:
    route = find_optimal_route(artwork_indices, reduced_mobility=True)
    print("\nOptimal Route:")
    print(" -> ".join(str(route)))
except ValueError as e:
    print(f"Error: {e}")