from entities import Room, Artwork

# --- Museum Creation ---
# Initialize Rooms
rooms = {
    "1": Room(1, "Room 1", "Museum 1", is_entry=True, is_exit=True),
    "2": Room(2, "Room 2", "Museum 1"),
    "3": Room(3, "Room 3", "Museum 1"),
    "4": Room(4, "Room 4", "Museum 1"),
    "5": Room(5, "Room 5", "Museum 1"),
    "6": Room(6, "Room 6", "Museum 1"),
    "7": Room(7, "Room 7", "Museum 1"),
    "8": Room(8, "Room 8", "Museum 1"),
    "9": Room(9, "Room 9", "Museum 1", is_exit=True),
    "elevator_1": Room(10, "Elevator 1", "Museum 1", is_elevator=True),
    "elevator_2": Room(11, "Elevator 2", "Museum 1", is_elevator=True),
    "stairs_1": Room(13, "Stairs 1", "Museum 1", is_stairs=True),
    "stairs_2": Room(14, "Stairs 2", "Museum 1", is_stairs=True),
}

# --- Room Connections ---
# Horizontal connections
rooms["1"].adjacent_rooms = [rooms["2"], rooms["elevator_1"]]
rooms["2"].adjacent_rooms = [rooms["1"], rooms["3"], rooms["stairs_1"]]
rooms["3"].adjacent_rooms = [rooms["2"], rooms["stairs_2"]]

rooms["4"].adjacent_rooms = [rooms["5"], rooms["elevator_1"], rooms["elevator_2"]]
rooms["5"].adjacent_rooms = [rooms["4"], rooms["6"], rooms["stairs_1"]]
rooms["6"].adjacent_rooms = [rooms["5"], rooms["stairs_2"]]

rooms["7"].adjacent_rooms = [rooms["8"], rooms["elevator_2"]]
rooms["8"].adjacent_rooms = [rooms["7"], rooms["9"]]
rooms["9"].adjacent_rooms = [rooms["8"]]

# Elevators connections
rooms["elevator_1"].adjacent_rooms = [rooms["1"], rooms["4"]]
rooms["elevator_2"].adjacent_rooms = [rooms["4"], rooms["7"]]
rooms["elevator_3"].adjacent_rooms = [rooms["9"]]

# Stairs connections
rooms["stairs_1"].adjacent_rooms = [rooms["2"], rooms["5"]]
rooms["stairs_2"].adjacent_rooms = [rooms["3"], rooms["6"]]
rooms["stairs_3"].adjacent_rooms = [rooms["6"], rooms["9"]]