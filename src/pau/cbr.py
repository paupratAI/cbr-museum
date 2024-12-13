import sqlite3
from entities import AbstractProblem, SpecificProblem, Author, Period, Theme
from typing import List
import json
import ast

class CBR:
    def __init__(self, db_path='./data/database.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_indices()
        self.ensure_columns()

    def create_indices(self):
        """Create indices for faster query performance."""
        with self.conn:
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_cluster ON abstract_problems(cluster);")

    def ensure_columns(self):
        """Ensure necessary columns (utility, usage_count, redundancy) exist in the table."""
        cursor = self.conn.execute("PRAGMA table_info(abstract_problems)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'utility' not in columns:
            self.conn.execute("ALTER TABLE abstract_problems ADD COLUMN utility REAL DEFAULT 0.0")
        if 'usage_count' not in columns:
            self.conn.execute("ALTER TABLE abstract_problems ADD COLUMN usage_count INTEGER DEFAULT 0")
        if 'redundancy' not in columns:
            self.conn.execute("ALTER TABLE abstract_problems ADD COLUMN redundancy REAL DEFAULT 0.0")
        self.conn.commit()

    def calculate_similarity(self, problem: AbstractProblem, group_size, group_type, art_knowledge,
                             preferred_periods_id, preferred_author, preferred_themes, time_coefficient) -> float:
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
        if problem.preferred_themes and preferred_themes and problem.preferred_themes[0] == preferred_themes[0]:
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
        """Retrieves the most similar cases to the current case, updates usage_count."""
        query = '''
            SELECT * FROM abstract_problems
            WHERE cluster = ?
        '''
        params = (problem.cluster,)
        rows = self.conn.execute(query, params).fetchall()
        cases_with_similarity = []
        for row in rows:
            # Según el nuevo orden:
            # 0: id
            # 1: specific_problem_id
            # 2: group_size
            # 3: group_type
            # 4: art_knowledge
            # 5: preferred_periods 
            # 6: preferred_author
            # 7: preferred_themes 
            # 8: time_coefficient
            # 9: ordered_artworks
            # 10: ordered_artworks_matches
            # 11: visited_artworks_count
            # 12: cluster
            # 13: utility
            # 14: usage_count
            # 15: redundancy

            stored_periods_id = [p['period_id'] for p in json.loads(row[5])]

            author_data = json.loads(row[6])
            stored_author = Author(author_id=author_data['author_id'], author_name=author_data["author_name"],
                                   main_periods=[Period(period_id=p['period_id']) for p in author_data.get('main_periods', [])])

            preferred_themes = ast.literal_eval(row[7])

            # Calculate similarity
            similarity = self.calculate_similarity(
                problem,
                group_size=row[2],
                group_type=row[3],
                art_knowledge=row[4],
                preferred_periods_id=stored_periods_id,
                preferred_author=stored_author,
                preferred_themes=preferred_themes,
                time_coefficient=row[8]
            )
            cases_with_similarity.append((row, similarity))

        # Sort by similarity and return top_k
        ranked_cases = sorted(cases_with_similarity, key=lambda x: x[1], reverse=True)
        selected_cases = ranked_cases[:top_k]

        # Update usage_count for the selected cases
        for case, sim in selected_cases:
            self.increment_usage_count(case[0])  # case[0] is id

        return selected_cases

    def increment_usage_count(self, case_id):
        """Increment usage_count each time a case is retrieved for recommendation."""
        cursor = self.conn.execute("SELECT usage_count FROM abstract_problems WHERE id = ?", (case_id,))
        result = cursor.fetchone()
        if result is not None and result[0] is not None:
            usage_count = result[0]
        else:
            usage_count = 0

        usage_count += 1
        self.conn.execute("UPDATE abstract_problems SET usage_count = ? WHERE id = ?", (usage_count, case_id))
        self.conn.commit()


    def store_case(self, problem: AbstractProblem, route_artworks: List[int], feedback: List[int]):
        """Stores a new case in the database."""
        pass
        """
        utility = sum(feedback) / (len(feedback) * 5.0) if feedback else 0
        # Initial usage_count = 0
        # Initial redundancy = 0
        # Convert problem.preferred_periods and problem.preferred_author to JSON
        periods_json = json.dumps([{'period_id': p.period_id} for p in problem.preferred_periods])
        author_json = json.dumps({
            'author_id': problem.preferred_author.author_id,
            'author_name': problem.preferred_author.author_name,
            'main_periods': [{'period_id': p.period_id} for p in problem.preferred_author.main_periods]
        }) if problem.preferred_author else json.dumps({})
        
        self.conn.execute('''
            INSERT INTO abstract_problems (
                group_size, group_type, art_knowledge,
                preferred_periods, preferred_author,
                preferred_themes, time_coefficient,
                ordered_artworks, ordered_artworks_matches,
                visited_artworks_count, cluster, utility, usage_count, redundancy
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            problem.group_size,
            problem.group_type,
            problem.art_knowledge,
            periods_json,
            author_json,
            str(problem.preferred_themes),
            problem.time_coefficient,
            ','.join(map(str, route_artworks)),
            '',  # ordered_artworks_matches 
            0,   # visited_artworks_count inicial
            problem.cluster,
            utility,
            0,  # usage_count
            0.0 # redundancy
        ))
        self.conn.commit()
        """

    def forget_cases(self, threshold=0.05):
        """Removes cases with low utility from the database."""
        with self.conn:
            self.conn.execute("DELETE FROM abstract_problems WHERE utility <= ?", (threshold,))

    def adapt_case(self):
        """Adapts a retrieved case to the new problem."""
        pass

    def calculate_redundancy(self):
        """
        Calculate redundancy for each case.
        Redundancy is the fraction of other cases that are very similar to this one.
        Consider cases with similarity > 0.9 as 'redundant'.
        """
        # Recuperamos todos los casos con el orden de columnas ya definido
        cursor = self.conn.execute("SELECT * FROM abstract_problems")
        all_cases = cursor.fetchall()

        cases = []
        for c in all_cases:
            # c[0]: id
            # c[1]: specific_problem_id
            # c[2]: group_size
            # c[3]: group_type
            # c[4]: art_knowledge
            # c[5]: preferred_periods (JSON)
            # c[6]: preferred_author (JSON)
            # c[7]: preferred_themes
            # c[8]: time_coefficient
            # c[9]: ordered_artworks
            # c[10]: ordered_artworks_matches
            # c[11]: visited_artworks_count
            # c[12]: cluster
            # c[13]: utility
            # c[14]: usage_count
            # c[15]: redundancy

            author_data = json.loads(c[6]) if c[6] else {}
            stored_author = Author(
                author_id=author_data.get('author_id', None),
                author_name=author_data.get('author_name', ""),
                main_periods=[Period(period_id=p['period_id']) for p in author_data.get('main_periods', [])]
            )

            stored_periods = json.loads(c[5]) if c[5] else []
            periods_list = [Period(period_id=p['period_id']) for p in stored_periods]

            themes = ast.literal_eval(c[7]) if c[7] else []

            # Crear el pseudo_problem respetando el orden de columnas
            pseudo_problem = AbstractProblem(specific_problem=None, available_periods=None, available_authors=None, available_themes=None)

            pseudo_problem.group_size=c[2]
            pseudo_problem.group_type=c[3]
            pseudo_problem.art_knowledge=c[4]
            pseudo_problem.preferred_periods=periods_list
            pseudo_problem.preferred_author=stored_author
            pseudo_problem.preferred_themes=themes
            pseudo_problem.time_coefficient=c[8]
            pseudo_problem.cluster=c[12]

            cases.append((c[0], pseudo_problem))  # c[0] es el id del caso

        total_cases = len(cases)
        for i, (case_id, case_problem) in enumerate(cases):
            if total_cases <= 1:
                redundancy = 0
            else:
                count_similar = 0
                for j, (other_id, other_problem) in enumerate(cases):
                    if i == j:
                        continue
                    sim = self.calculate_similarity(
                        case_problem,
                        group_size=other_problem.group_size,
                        group_type=other_problem.group_type,
                        art_knowledge=other_problem.art_knowledge,
                        preferred_periods_id=[p.period_id for p in other_problem.preferred_periods],
                        preferred_author=other_problem.preferred_author,
                        preferred_themes=other_problem.preferred_themes,
                        time_coefficient=other_problem.time_coefficient
                    )
                    if sim > 0.9:
                        count_similar += 1
                redundancy = count_similar / (total_cases - 1)

            self.conn.execute("UPDATE abstract_problems SET redundancy = ? WHERE id = ?", (redundancy, case_id))
        self.conn.commit()


    def calculate_utility(self):
        """
        Recalculate utility considering feedback, usage_count, and redundancy.
        Utility formula (example):
        - normalized_feedback = avg_feedback/5.0 (feedback from 1 to 5)
        - normalize usage_count by dividing by max usage_count found
        - redundancy reduces utility, so use (1 - redundancy) as a factor
        - utility = 0.5 * normalized_feedback + 0.3 * normalized_usage + 0.2 * (1 - redundancy)
        """
        # Ensure columns and recalculate redundancy first
        self.ensure_columns()
        self.calculate_redundancy()

        # Get max usage_count to normalize usage
        cursor = self.conn.execute("SELECT MAX(usage_count) FROM abstract_problems")
        max_usage = cursor.fetchone()[0]
        if max_usage is None or max_usage == 0:
            max_usage = 1  # Avoid division by zero

        # Retrieve all cases
        cursor = self.conn.execute("SELECT id, feedback, usage_count, redundancy FROM abstract_problems")
        rows = cursor.fetchall()

        for case_id, feedback_str, usage_count, redundancy in rows:
            if feedback_str:
                feedback_values = list(map(int, feedback_str.split(',')))
                avg_feedback = sum(feedback_values)/len(feedback_values) if feedback_values else 0
            else:
                avg_feedback = 0
            normalized_feedback = avg_feedback / 5.0

            # Normalize usage_count
            normalized_usage = usage_count / max_usage

            # (1 - redundancy)
            non_redundancy_factor = 1 - redundancy
            if non_redundancy_factor < 0:
                non_redundancy_factor = 0

            # Weighted combination
            utility = (0.5 * normalized_feedback) + (0.3 * normalized_usage) + (0.2 * non_redundancy_factor)
            self.conn.execute("UPDATE abstract_problems SET utility = ? WHERE id = ?", (utility, case_id))

        self.conn.commit()
