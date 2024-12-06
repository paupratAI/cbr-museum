import sqlite3
from entities import Museum, Room, Author, Theme, Period, Artwork, SpecificProblem, Match

class DatabaseManager:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def load_museums(self):
        self.cursor.execute("SELECT * FROM museums")
        museums = []
        for row in self.cursor.fetchall():
            museum_id, museum_name = row[:2]
            rooms = self.load_rooms(museum_id)
            auxiliary_rooms = [room for room in rooms if room.is_entry or room.is_exit]
            museums.append(Museum(museum_id, museum_name, rooms, auxiliary_rooms))
        return museums

    def load_rooms(self, museum_id: int):
        self.cursor.execute("SELECT * FROM rooms WHERE museum_id=?", (museum_id,))
        rooms = []
        for row in self.cursor.fetchall():
            room_id, room_in_museum, is_entry, is_exit, is_stairs, is_elevator, room_name = row
            rooms.append(Room(
                room_id=room_id,
                room_in_museum=room_in_museum,
                is_entry=bool(is_entry),
                is_exit=bool(is_exit),
                is_stairs=bool(is_stairs),
                is_elevator=bool(is_elevator),
                room_name=room_name
            ))
        return rooms

    def load_artworks(self):
        self.cursor.execute("SELECT * FROM artworks")
        artworks = []
        for row in self.cursor.fetchall():
            (
                artwork_id, artwork_name, artwork_in_room, created_by, 
                artwork_in_period, artwork_theme, dimension, relevance, complexity, default_time
            ) = row
            author = self.load_author(created_by)
            period = self.load_period(artwork_in_period)
            artworks.append(Artwork(
                artwork_id=artwork_id,
                artwork_name=artwork_name,
                artwork_in_room=artwork_in_room,
                created_by=author,
                artwork_in_period=period,
                artwork_theme=artwork_theme,
                dimension=dimension,
                relevance=relevance,
                complexity=complexity,
                default_time=default_time
            ))
        return artworks

    def load_author(self, author_id: int):
        self.cursor.execute("SELECT * FROM authors WHERE author_id=?", (author_id,))
        row = self.cursor.fetchone()
        if row:
            author_id, author_name = row[:2]
            main_periods = self.load_periods_for_author(author_id)
            return Author(author_id, author_name, main_periods)
        return None

    def load_period(self, period_id: int):
        self.cursor.execute("SELECT * FROM periods WHERE period_id=?", (period_id,))
        row = self.cursor.fetchone()
        if row:
            period_id, year_beginning, year_end, themes, period_name = row
            themes = themes.split(",")  # Assuming themes are stored as CSV
            return Period(period_id, year_beginning, year_end, themes, period_name)
        return None

    def load_periods_for_author(self, author_id: int):
        self.cursor.execute("SELECT * FROM periods WHERE author_id=?", (author_id,))
        return [self.load_period(row[0]) for row in self.cursor.fetchall()]

    def close(self):
        self.conn.close()

# Inicialization

# EXECUTAR QUAN ESTIGUI CREAT EL DATASET
'''
db_manager = DatabaseManager("museum_database.db")
museums = db_manager.load_museums()
artworks = db_manager.load_artworks()
db_manager.close()
'''