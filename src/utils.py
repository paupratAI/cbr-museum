import pandas as pd
import sqlite3
import json
from dataclasses import asdict
import math
import random

def save_in_sqlite3(results: list):
    # results es una lista de tuplas (AbstractProblem, AbstractSolution, visited_artworks_count)

    conn = sqlite3.connect("../data/database.db")
    cursor = conn.cursor()

    # Crear tablas si no existen
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

    # Añadimos visited_artworks_count a abstract_problems
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
        time_coefficient REAL,
        ordered_artworks TEXT,
        ordered_artworks_matches TEXT,
        visited_artworks_count INTEGER,
        group_description TEXT,
        rating REAL,
        FOREIGN KEY(specific_problem_id) REFERENCES specific_problems(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS abstract_solutions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        abstract_problem_id INTEGER,
        max_score INTEGER,
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

    # Desempaquetamos las tres variables en el bucle
    for ap, asol, visited_count in results:
        sp = ap.specific_problem

        # Insertar SpecificProblem
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

        # Serializar campos complejos de AbstractProblem a JSON
        preferred_periods_json = json.dumps([asdict(p) for p in ap.preferred_periods], ensure_ascii=False)
        preferred_author_json = json.dumps(asdict(ap.preferred_author), ensure_ascii=False) if ap.preferred_author else None
        preferred_themes_json = json.dumps(ap.preferred_themes, ensure_ascii=False)

        # Ordenar matches para obtener match_types en el mismo orden que ordered_artworks
        sorted_matches = sorted(asol.matches, key=lambda m: m.match_type, reverse=True)
        ordered_artworks_str = ",".join(map(str, asol.ordered_artworks))
        ordered_match_types = [m.match_type for m in sorted_matches]
        ordered_match_types_str = ",".join(map(str, ordered_match_types))

        # Insertar AbstractProblem, incluyendo visited_artworks_count
        cursor.execute("""
        INSERT INTO abstract_problems
        (specific_problem_id, group_id, group_size, group_type, art_knowledge, preferred_periods, preferred_author, preferred_themes, time_coefficient, ordered_artworks, ordered_artworks_matches, visited_artworks_count, group_description, rating)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            specific_problem_id,
            ap.group_id,
            ap.group_size,
            ap.group_type,
            ap.art_knowledge,
            preferred_periods_json,
            preferred_author_json,
            preferred_themes_json,
            ap.time_coefficient,
            ordered_artworks_str,
            ordered_match_types_str,
            visited_count,
            ap.group_description,
            float(round(random.uniform(0, 5), 1)) # Random rating
        ))
        abstract_problem_id = cursor.lastrowid

        # Insertar AbstractSolution
        cursor.execute("""
        INSERT INTO abstract_solutions
        (abstract_problem_id, max_score)
        VALUES (?, ?)
        """, (
            abstract_problem_id,
            asol.max_score
        ))
        abstract_solution_id = cursor.lastrowid

        # Insertar Matches
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
    """Calcula el tiempo predeterminado basado en la dimensión, complejidad y relevancia."""
    relevance_multiplier = 1 if relevance == "High" else 0.5
    default_time = ((math.pow(dimension, 0.25) + math.log(complexity, 10)) / 2) + relevance_multiplier
    return int(default_time)