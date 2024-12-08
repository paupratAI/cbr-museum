import pandas as pd
import sqlite3
import json
from dataclasses import asdict
import math

def save_in_sqlite3(results: list):
    # results es una lista de tuplas (AbstractProblem, AbstractSolution)

    conn = sqlite3.connect("data/database.db")
    cursor = conn.cursor()

    # Crear tablas si no existen
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS specific_problems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        num_people INTEGER,
        favorite_author INTEGER,
        favorite_period INTEGER,
        favorite_theme TEXT,
        guided_visit BOOLEAN,
        minors BOOLEAN,
        num_experts INTEGER,
        past_museum_visits INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS abstract_problems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        specific_problem_id INTEGER,
        group_size INTEGER,
        group_type TEXT,
        art_knowledge INTEGER,
        preferred_periods TEXT,
        preferred_author TEXT,
        preferred_themes TEXT,
        time_coefficient REAL,
        ordered_artworks TEXT,
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

    for ap, asol in results:
        sp = ap.specific_problem
        # Insertar SpecificProblem
        cursor.execute("""
        INSERT INTO specific_problems
        (num_people, favorite_author, favorite_period, favorite_theme, guided_visit, minors, num_experts, past_museum_visits)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sp.num_people,
            sp.favorite_author,
            sp.favorite_period,
            sp.favorite_theme,
            1 if sp.guided_visit else 0,
            1 if sp.minors else 0,
            sp.num_experts,
            sp.past_museum_visits
        ))
        specific_problem_id = cursor.lastrowid

        # Serializar campos complejos de AbstractProblem a JSON
        preferred_periods_json = json.dumps([asdict(p) for p in ap.preferred_periods], ensure_ascii=False)
        preferred_author_json = json.dumps(asdict(ap.preferred_author), ensure_ascii=False) if ap.preferred_author else None
        preferred_themes_json = json.dumps(ap.preferred_themes, ensure_ascii=False)

        # Convertir la lista de artworks ordenados en un string separado por comas
        ordered_artworks_str = ",".join(map(str, asol.ordered_artworks))

        # Insertar AbstractProblem
        cursor.execute("""
        INSERT INTO abstract_problems
        (specific_problem_id, group_size, group_type, art_knowledge, preferred_periods, preferred_author, preferred_themes, time_coefficient, ordered_artworks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            specific_problem_id,
            ap.group_size,
            ap.group_type,
            ap.art_knowledge,
            preferred_periods_json,
            preferred_author_json,
            preferred_themes_json,
            ap.time_coefficient,
            ordered_artworks_str
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