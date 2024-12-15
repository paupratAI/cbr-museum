import sqlite3
import json
import math

def save_in_sqlite3(cases_data: list[dict]):
    """
    Save the case data in the SQLite.

    Args:
        cases_data (list[dict]): List with case data dictionaries containing the following:
        - group_id (int): The group ID.
        - group_size (int): The group size.
        - group_type (str): The group type.
        - art_knowledge (int): The art knowledge level.
        - preferred_periods_ids (list[int]): The list of preferred periods IDs of the group.
        - preferred_author_name (str): The preferred author name of the group.
        - preferred_themes (list[str]): The list of preferred themes of the group.
        - reduced_mobility (int): 1 if the group has reduced mobility, 0 otherwise.
        - time_coefficient (float): The time coefficient.
        - time_limit (float): The time limit for the group visit.
        - group_description (str): The group description.
        - ordered_artworks (list[int]): The list of ordered arwork IDs of the group.
        - ordered_artworks_matches (list[float]): The list of ordered artwork matches of the group.
        - visited_artworks_count (int): The number of visited artworks.
        - rating (int): The rating of the group.
        - textual_feedback (str): The textual feedback of the group.
        - only_elevator (int): 1 if the group should use only the elevator, 0 otherwise.
        - time_coefficient_correction (str): The time coefficient correction.
        - artwork_to_remove (str): The artwork to remove, if any (None otherwise).
        - guided_visit (int): 1 if the group should have a guided visit, 0 otherwise.
    """

    conn = sqlite3.connect("data/database.db")
    cursor = conn.cursor()

    # Create the cases table if it does not exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        case_id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        group_size INTEGER,
        group_type TEXT,
        art_knowledge INTEGER,
        preferred_periods_ids TEXT,
        preferred_author_name TEXT,
        preferred_themes TEXT,
        reduced_mobility BOOLEAN,
        time_coefficient REAL,
        time_limit REAL,
        group_description TEXT,
        ordered_artworks TEXT,
        ordered_artworks_matches TEXT,
        visited_artworks_count INTEGER,
        rating INTEGER,
        textual_feedback TEXT,
        only_elevator BOOLEAN,
        time_coefficient_correction TEXT,
        artwork_to_remove TEXT,
        guided_visit BOOLEAN
    )
    """)
    
    # Insert into cases
    for case_data in cases_data:
        cursor.execute(
        """
        INSERT INTO cases
        (group_id, group_size, group_type, art_knowledge, preferred_periods_ids, preferred_author_name, preferred_themes, reduced_mobility, time_coefficient, time_limit, group_description, ordered_artworks, ordered_artworks_matches, visited_artworks_count, rating, textual_feedback, only_elevator, time_coefficient_correction, artwork_to_remove, guided_visit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        , (
            case_data["group_id"],
            case_data["group_size"],
            case_data["group_type"],
            case_data["art_knowledge"],
            json.dumps(case_data["preferred_periods_ids"]),
            case_data["preferred_author_name"],
            json.dumps(case_data["preferred_themes"]),
            case_data["reduced_mobility"],
            case_data["time_coefficient"],
            case_data["time_limit"],
            case_data["group_description"],
            json.dumps(case_data["ordered_artworks"]),
            json.dumps(case_data["ordered_artworks_matches"]),
            case_data["visited_artworks_count"],
            case_data["rating"],
            case_data["textual_feedback"],
            case_data["only_elevator"],
            case_data["time_coefficient_correction"],
            case_data["artwork_to_remove"],
            case_data["guided_visit"]
        ))

    conn.commit()
    conn.close()

def calculate_default_time(dimension: int, complexity: int, relevance: str) -> int:
    """Calculate default time based on dimension, complexity, and relevance."""
    relevance_multiplier = 1 if relevance == "High" else 0.5
    default_time = ((math.pow(dimension, 0.25) + math.log(complexity, 10)) / 2) + relevance_multiplier
    return int(default_time)