import pandas as pd
import sqlite3
import json
from dataclasses import asdict
import math
import random

def save_in_sqlite3(results: list):
    # results is a list of tuples (AbstractProblem, AbstractSolution, visited_artworks_count, full_feedback)

    conn = sqlite3.connect("../data/database.db")
    cursor = conn.cursor()

    # Create tables if they do not exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS specific_problems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        num_people INTEGER,
        favorite_author INTEGER,
        favorite_period INTEGER,
        favorite_theme TEXT,
        guided_visit BOOLEAN,
        minors BOOLEAN,
        num_experts INTEGER,
        past_museum_visits INTEGER,
        group_description TEXT
    )
    """)

    # Create the abstract_problems table with the new variables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS abstract_problems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        specific_problem_id INTEGER,
        group_size INTEGER,
        group_type TEXT,
        art_knowledge INTEGER,
        preferred_periods TEXT,
        preferred_author TEXT,
        preferred_themes TEXT,
        ordered_artworks TEXT,
        ordered_artworks_matches TEXT,
        visited_artworks_count INTEGER,
        group_description TEXT,
        rating REAL,  -- Float for n.n/5
        feedback TEXT,
        only_elevator BOOLEAN,  -- Binary from Yes/No
        time_coefficient TEXT,  -- Shorter/Equal/Longer
        artwork_to_remove TEXT,
        guided_visit BOOLEAN,  -- Binary from Yes/No
        FOREIGN KEY(specific_problem_id) REFERENCES specific_problems(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS abstract_solutions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        abstract_problem_id INTEGER,
        max_score INTEGER,
        average_visited_matching INTEGER,
        FOREIGN KEY(abstract_problem_id) REFERENCES abstract_problems(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        abstract_solution_id INTEGER,
        artwork_id INTEGER,
        artwork_name TEXT,
        artwork_theme TEXT,
        match_type INTEGER,
        artwork_time REAL,
        FOREIGN KEY(abstract_solution_id) REFERENCES abstract_solutions(id)
    )
    """)

    # Unpack the variables in the loop
    for ap, asol, visited_count, full_feedback in results:
        sp = ap.specific_problem

        # Process full_feedback variables
        rating_value = float(full_feedback["evaluation"])  # Use the actual rating
        feedback_text = full_feedback["feedback"]  # Feedback as text
        only_elevator_binary = 1 if full_feedback["only_elevator"] else 0
        time_coefficient_text = full_feedback["time_coefficient"]  # Shorter/Equal/Longer
        artwork_to_remove_text = full_feedback["artwork_to_remove"]  # Artwork name
        guided_visit_binary = 1 if full_feedback["guided_visit"] else 0

        # Insert into specific_problems
        cursor.execute("""
        INSERT INTO specific_problems
        (group_id, num_people, favorite_author, favorite_period, favorite_theme, guided_visit, minors, num_experts, past_museum_visits, group_description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sp.group_id,
            sp.num_people,
            sp.favorite_author,
            sp.favorite_period,
            sp.favorite_theme,
            1 if sp.guided_visit else 0,
            1 if sp.minors else 0,
            sp.num_experts,
            sp.past_museum_visits,
            sp.group_description
        ))
        specific_problem_id = cursor.lastrowid

        # Serialize complex fields of AbstractProblem to JSON
        preferred_periods_json = json.dumps([asdict(p) for p in ap.preferred_periods], ensure_ascii=False)
        preferred_author_json = json.dumps(asdict(ap.preferred_author), ensure_ascii=False) if ap.preferred_author else None
        preferred_themes_json = json.dumps(ap.preferred_themes, ensure_ascii=False)

        # Order matches by match_type to match the order of ordered_artworks
        sorted_matches = sorted(asol.matches, key=lambda m: m.match_type, reverse=True)
        ordered_artworks_json = json.dumps(asol.ordered_artworks, ensure_ascii=False)
        ordered_match_types_json = json.dumps([m.match_type for m in sorted_matches], ensure_ascii=False)

        # Insert into abstract_problems
        cursor.execute("""
        INSERT INTO abstract_problems
        (specific_problem_id, group_id, group_size, group_type, art_knowledge, preferred_periods, preferred_author, preferred_themes, ordered_artworks, ordered_artworks_matches, visited_artworks_count, group_description, rating, feedback, only_elevator, time_coefficient, artwork_to_remove, guided_visit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            specific_problem_id,
            ap.group_id,
            ap.group_size,
            ap.group_type,
            ap.art_knowledge,
            preferred_periods_json,
            preferred_author_json,
            preferred_themes_json,
            ordered_artworks_json,
            ordered_match_types_json,
            visited_count,
            ap.group_description,
            rating_value,  # Actual evaluation value
            feedback_text,
            only_elevator_binary,  # 1 or 0 for Yes/No
            time_coefficient_text,  # Shorter/Equal/Longer
            artwork_to_remove_text,  # Text of the artwork
            guided_visit_binary  # 1 or 0 for Yes/No
        ))
        abstract_problem_id = cursor.lastrowid

        # Insert into abstract_solutions
        cursor.execute("""
        INSERT INTO abstract_solutions
        (abstract_problem_id, max_score, average_visited_matching)
        VALUES (?, ?, ?)
        """, (
            abstract_problem_id,
            asol.max_score,
            round(asol.avg_score, 2)
        ))
        abstract_solution_id = cursor.lastrowid

        # Insert into matches
        for m in asol.matches:
            cursor.execute("""
            INSERT INTO matches
            (abstract_solution_id, artwork_id, artwork_name, artwork_theme, match_type, artwork_time)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                abstract_solution_id,
                m.artwork.artwork_id,
                m.artwork.artwork_name,
                m.artwork.artwork_theme,
                m.match_type,
                m.artwork_time
            ))

    conn.commit()
    conn.close()

def calculate_default_time(dimension: int, complexity: int, relevance: str) -> int:
    """Calculate default time based on dimension, complexity, and relevance."""
    relevance_multiplier = 1 if relevance == "High" else 0.5
    default_time = ((math.pow(dimension, 0.25) + math.log(complexity, 10)) / 2) + relevance_multiplier
    return int(default_time)