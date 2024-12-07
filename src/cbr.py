import sqlite3
from entities import AbstractProblem, SpecificProblem, Author, Period, Theme
from typing import List, Dict
import json
import ast

class CBRSystem:
    def __init__(self):
        self.conn = sqlite3.connect('data/database.db')
        self.create_indices()

    def create_indices(self):
        """Create indices for faster query performance."""
        with self.conn:
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_preferred_author ON abstract_problems(preferred_author);")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_preferred_periods ON abstract_problems(preferred_periods);")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_group_type ON abstract_problems(group_type);")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_group_size ON abstract_problems(group_size);")


    def calculate_similarity(self, problem: AbstractProblem, group_size, group_type, art_knowledge, preferred_periods, preferred_author, preferred_themes, time_coefficient) -> float:
        """Calculates the similarity between the current problem and a stored problem."""
        weights = {
            "group_size": 0.05,
            "group_type": 0.1,
            "art_knowledge": 0.2,
            "preferred_periods": 0.2,
            "preferred_author": 0.2,
            "preferred_themes": 0.2,
            "time_coefficient": 0.05
        }
        similarity = 0

        # Group size
        diff_group_size = abs(problem.group_size - group_size)

        if diff_group_size == 0:
            similarity += weights["group_size"]
        elif diff_group_size == 1:
            similarity += weights["group_size"] * 0.5
        elif diff_group_size == 2:
            similarity += weights["group_size"] * 0.1
        
        # Group type
        if problem.group_type == group_type:
            similarity += weights["group_type"]
        
        # Art knowledge
        diff_art_knowledge = abs(problem.art_knowledge - art_knowledge)
        if diff_art_knowledge == 0:
            similarity += weights["art_knowledge"]
        elif diff_art_knowledge == 1:
            similarity += weights["art_knowledge"] * 0.5
        elif diff_art_knowledge == 2:
            similarity += weights["art_knowledge"] * 0.1
        
        # Preferred periods
        matched_periods = [
            period for period in problem.preferred_periods 
            if any(p.year_beginning <= period.year_beginning <= p.year_end or 
                p.year_beginning <= period.year_end <= p.year_end 
                for p in preferred_periods)
        ]
        if matched_periods:
            similarity += weights["preferred_periods"] * (len(matched_periods) / len(problem.preferred_periods))

        # Preferred author
        if problem.preferred_author:
            if problem.preferred_author.author_id == preferred_author.author_id:
                similarity += weights["preferred_author"]
            else:
                # Check overlapping periods with the preferred author
                matched_author_periods = [
                    period for period in problem.preferred_author.main_periods
                    if any(p.year_beginning <= period.year_beginning <= p.year_end or
                        p.year_beginning <= period.year_end <= p.year_end
                        for p in preferred_author.main_periods)
                ]
                if matched_author_periods:
                    similarity += weights["preferred_author"] * (len(matched_author_periods) / len(problem.preferred_author.main_periods))

        
        # Preferred themes
        if problem.preferred_themes[0] == preferred_themes[0]:
            similarity += weights["preferred_themes"]

        # Time coefficient
        diff_time_coefficient = abs(problem.time_coefficient - time_coefficient)
        if diff_time_coefficient == 0:
            similarity += weights["time_coefficient"]
        elif diff_time_coefficient < 0.2:
            similarity += weights["time_coefficient"] * 0.5
        elif diff_time_coefficient <= 0.5:
            similarity += weights["time_coefficient"] * 0.1

        return round(similarity, 2)


    def retrieve_cases(self, problem: AbstractProblem, top_k=3):
        """Retrieves the most similar cases to the current problem."""
        query = "SELECT * FROM abstract_problems"
        rows = self.conn.execute(query).fetchall()

        # Convert rows to AbstractProblem and calculate similarity
        cases_with_similarity = []
        for row in rows:
            # Deserialize periods
            stored_periods = deserialize_periods(row[4]) 
            # Deserialize author
            stored_author = deserialize_author(row[5])  
            # Calculate similarity
            similarity = self.calculate_similarity(
                problem,
                group_size=row[1],
                group_type=row[2],
                art_knowledge=row[3],
                preferred_periods=stored_periods,
                preferred_author=stored_author,
                preferred_themes = ast.literal_eval(row[6]),
                time_coefficient=row[7]
            )
            cases_with_similarity.append((row, similarity))

        # Sort by similarity and return top_k
        ranked_cases = sorted(cases_with_similarity, key=lambda x: x[1], reverse=True)
        return ranked_cases[:top_k]


    def store_case(self, problem: AbstractProblem, route_artworks: List[int], feedback: List[int]):
        """Stores a new case in the database if it does not already exist."""
        utility = sum(feedback) / len(feedback) if feedback else 0

        # Verify if the case already exists
        query = '''
            SELECT COUNT(*) FROM abstract_problems
            WHERE group_size = ? AND group_type = ? AND art_knowledge = ? AND
                preferred_periods = ? AND preferred_author = ? AND preferred_themes = ? AND 
                time_coefficient = ? AND route_artworks = ? AND feedback = ?;
        '''
        params = (
            problem.group_size, problem.group_type, problem.art_knowledge,
            problem.preferred_periods, problem.preferred_author, problem.preferred_themes,
            problem.time_coefficient
        )
        result = self.conn.execute(query, params).fetchone()

        if result[0] == 0:  # Case does not exist
            with self.conn:
                self.conn.execute('''
                    INSERT INTO abstract_problems (
                        group_size, group_type, art_knowledge, preferred_periods, preferred_author, preferred_themes, time_coefficient, route_artworks, feedback, utility
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    problem.group_size, problem.group_type, problem.art_knowledge,
                    problem.preferred_periods, problem.preferred_author, problem.preferred_themes,
                    problem.time_coefficient, ','.join(map(str, route_artworks)), 
                    ','.join(map(str, feedback)), utility
                ))

    def forget_cases(self, threshold=0.05):
        """Removes cases with low utility from the database."""
        with self.conn:
            self.conn.execute("DELETE FROM abstract_problems WHERE utility <= ?", (threshold,))

    def adapt_case(self):
        """Adapts a retrieved case to the new problem."""
        pass


def deserialize_periods(periods_json: str) -> List[Period]:
    """Transform a JSON string of periods into a list of Period objects."""
    periods = json.loads(periods_json)  
    return [
        Period(
            period_id=p['period_id'],
            year_beginning=p['year_beginning'],
            year_end=p['year_end'],
            themes=p.get('themes', []),
            period_name=p.get('period_name')
        )
        for p in periods
    ]

def deserialize_author(author_json: str) -> Author:
    """Deserializa un JSON de autor a un objeto Author."""
    author_data = json.loads(author_json)  
    return Author(
        author_id=author_data['author_id'],
        author_name=author_data['author_name'],
        main_periods=[
            Period(
                period_id=p['period_id'],
                year_beginning=p['year_beginning'],
                year_end=p['year_end'],
                themes=p.get('themes', []),
                period_name=p.get('period_name')
            )
            for p in author_data.get('main_periods', [])
        ]
    )

