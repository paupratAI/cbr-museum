import pandas as pd
import sqlite3

def save_in_sqlite3(results: list):
    # Guardar en una base de datos SQLite
    # Conectar a la base de datos (creará el archivo si no existe)
    conn = sqlite3.connect("data/database.db")
    cursor = conn.cursor()

    # Crear la tabla si no existe
    # Ajusta las columnas al tipo de datos que necesitas
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

    # Insertar cada registro en la tabla
    for record in results:
        cursor.execute("""
        INSERT INTO specific_problems
        (num_people, favorite_author, favorite_period, favorite_theme, guided_visit, minors, num_experts, past_museum_visits)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record['num_people'],
            record['favorite_author'],
            record['favorite_period'],
            record['favorite_theme'],
            record['guided_visit'],
            record['minors'],
            record['num_experts'],
            record['past_museum_visits']
        ))

    # Confirmar transacciones
    conn.commit()
    conn.close()