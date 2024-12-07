import pandas as pd
import sqlite3
import json
from dataclasses import asdict

def save_in_sqlite3(results: list):
    # results es una lista de AbstractProblem

    conn = sqlite3.connect("data/database.db")
    cursor = conn.cursor()

    # Crear la tabla si no existe
    # 7 columnas: group_size, group_type, art_knowledge, preferred_periods, preferred_author, preferred_themes, time_coefficient
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS abstract_problems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_size INTEGER,
        group_type TEXT,
        art_knowledge INTEGER,
        preferred_periods TEXT,
        preferred_author TEXT,
        preferred_themes TEXT,
        time_coefficient REAL
    )
    """)

    # Insertar cada registro en la tabla
    for ap in results:
        # Convertir objetos complejos a algo serializable
        preferred_periods_json = json.dumps([asdict(p) for p in ap.preferred_periods], ensure_ascii=False)
        preferred_author_json = json.dumps(asdict(ap.preferred_author), ensure_ascii=False) if ap.preferred_author else None
        preferred_themes_json = json.dumps(ap.preferred_themes, ensure_ascii=False)

        cursor.execute("""
        INSERT INTO abstract_problems
        (group_size, group_type, art_knowledge, preferred_periods, preferred_author, preferred_themes, time_coefficient)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            ap.group_size,
            ap.group_type,
            ap.art_knowledge,
            preferred_periods_json,
            preferred_author_json,
            preferred_themes_json,
            ap.time_coefficient
        ))

    conn.commit()
    conn.close()