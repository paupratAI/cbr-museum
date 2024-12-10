import sqlite3
from entities import AbstractProblem, SpecificProblem, Author, Period, Theme
from typing import List, Dict
import json
import ast

class CBR:
    def __init__(self, db_path='./data/database.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_indices()

    def create_indices(self):
        """Create indices for faster query performance."""
        with self.conn:
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_preferred_author ON abstract_problems(preferred_author);")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_art_knowledge ON abstract_problems(art_knowledge);")


    def calculate_similarity(self, problem: AbstractProblem, group_size, group_type, art_knowledge, preferred_periods_id, preferred_author, preferred_themes, time_coefficient) -> float:
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
        matched_periods = 0
        for period_id in preferred_periods_id:
            for p in problem.preferred_periods:
                if period_id == p.period_id:
                    matched_periods += 1
        if matched_periods > 0:
            similarity += weights["preferred_periods"] * (1 - abs(len(preferred_periods_id) - matched_periods))

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
                    similarity += weights["preferred_author"]*0.8 * (len(matched_author_periods) / len(problem.preferred_author.main_periods))

        
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


    def retrieve_cases(self, problem: AbstractProblem, top_k=50):
        """Retrieves the most similar cases to the current problem."""
        #query = "SELECT * FROM abstract_problems"
        #rows = self.conn.execute(query).fetchall()

        query = '''
            SELECT * FROM abstract_problems
            WHERE preferred_author = ? OR art_knowledge = ?
        '''
        params = (problem.preferred_author.author_id, problem.art_knowledge)
        rows = self.conn.execute(query, params).fetchall()


        # Convert rows to AbstractProblem and calculate similarity
        cases_with_similarity = []
        for row in rows:
            stored_periods_id = [p['period_id'] for p in json.loads(row[5])]
            
            # Deserialize author
            author_data = json.loads(row[6])  
            stored_author = Author(author_id=author_data['author_id'], main_periods=[Period(period_id=p['period_id']) for p in author_data.get('main_periods', [])])
        
            # Calculate similarity
            similarity = self.calculate_similarity(
                problem,
                group_size=row[2],
                group_type=row[3],
                art_knowledge=row[4],
                preferred_periods_id=stored_periods_id,
                preferred_author=stored_author,
                preferred_themes = ast.literal_eval(row[7]),
                time_coefficient=row[8]
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



