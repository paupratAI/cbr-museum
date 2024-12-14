import sqlite3
from entities import AbstractProblem, SpecificProblem, Author, Period, Theme
from typing import List
import json
import ast
from dataclasses import asdict

from clustering import Clustering
from ontology.periods import periods
from ontology.themes import theme_instances
from authors import authors

class CBR:
    def __init__(self, db_path='./data/database.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row 
        self.create_indices()
        self.ensure_columns()

    def create_indices(self):
        """Create indices for faster query performance."""
        with self.conn:
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_cluster ON abstract_problems(cluster);")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_count ON abstract_problems(usage_count);")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_utility ON abstract_problems(utility);")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_redundancy ON abstract_problems(redundancy);")


    def ensure_columns(self):
        """Ensure necessary columns (utility, usage_count, redundancy) exist in the table."""
        cursor = self.conn.execute("PRAGMA table_info(abstract_problems)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'usage_count' not in columns:
            self.conn.execute("ALTER TABLE abstract_problems ADD COLUMN usage_count INTEGER DEFAULT 0")
        if 'redundancy' not in columns:
            self.conn.execute("ALTER TABLE abstract_problems ADD COLUMN redundancy REAL DEFAULT 0.0")
        if 'utility' not in columns:
            self.conn.execute("ALTER TABLE abstract_problems ADD COLUMN utility REAL DEFAULT 0.0")
        self.conn.commit()

    def calculate_similarity(
        self, 
        problem_group_size: int,
        problem_group_type: str,
        problem_art_knowledge: int,
        problem_preferred_periods: List[Period],
        problem_preferred_author: Author,
        problem_preferred_themes: List[str],
        problem_time_coefficient: float,
        stored_group_size: int, 
        stored_group_type: str, 
        stored_art_knowledge: int, 
        stored_preferred_periods_id: List[int],
        stored_preferred_author: Author,
        stored_preferred_themes: List[str],
        stored_time_coefficient: float
    ) -> float:
        """
        Calculates the similarity between the provided parameters of a problem
        and those of a stored case directly, without needing an AbstractProblem object.
        """
        weights = {
            "group_size": 0.05,
            "group_type": 0.1,
            "art_knowledge": 0.2,
            "preferred_periods": 0.2,
            "preferred_author": 0.2,
            "preferred_themes": 0.2,
            "time_coefficient": 0.05
        }
        similarity = 0.0

        # Group size
        diff_group_size = abs(problem_group_size - stored_group_size)
        if diff_group_size == 0:
            similarity += weights["group_size"]
        elif diff_group_size == 1:
            similarity += weights["group_size"] * 0.5
        elif diff_group_size == 2:
            similarity += weights["group_size"] * 0.1

        # Group type
        if problem_group_type == stored_group_type:
            similarity += weights["group_type"]

        # Art knowledge
        diff_art_knowledge = abs(problem_art_knowledge - stored_art_knowledge)
        if diff_art_knowledge == 0:
            similarity += weights["art_knowledge"]
        elif diff_art_knowledge == 1:
            similarity += weights["art_knowledge"] * 0.5
        elif diff_art_knowledge == 2:
            similarity += weights["art_knowledge"] * 0.1

        # Preferred periods
        matched_periods = 0
        for period_id in stored_preferred_periods_id:
            for p in problem_preferred_periods:
                if period_id == p.period_id:
                    matched_periods += 1
        if matched_periods > 0:
            similarity += weights["preferred_periods"] * (1 - abs(len(stored_preferred_periods_id) - matched_periods))

        # Preferred author
        if problem_preferred_author:
            if problem_preferred_author.author_id == stored_preferred_author.author_id:
                similarity += weights["preferred_author"]
            else:
                # Check overlapping periods with the preferred author
                matched_author_periods = [
                    period for period in problem_preferred_author.main_periods
                    if any(
                        p.year_beginning <= period.year_beginning <= p.year_end or
                        p.year_beginning <= period.year_end <= p.year_end
                        for p in stored_preferred_author.main_periods
                    )
                ]
                if matched_author_periods:
                    similarity += weights["preferred_author"] * 0.8 * (
                        len(matched_author_periods) / len(problem_preferred_author.main_periods)
                    )

        # Preferred themes
        if problem_preferred_themes and stored_preferred_themes and problem_preferred_themes[0] == stored_preferred_themes[0]:
            similarity += weights["preferred_themes"]

        # Time coefficient
        diff_time_coefficient = abs(problem_time_coefficient - stored_time_coefficient)
        if diff_time_coefficient == 0:
            similarity += weights["time_coefficient"]
        elif diff_time_coefficient < 0.2:
            similarity += weights["time_coefficient"] * 0.5
        elif diff_time_coefficient <= 0.5:
            similarity += weights["time_coefficient"] * 0.1

        return round(similarity, 2)


    def retrieve_cases(self, problem: AbstractProblem, top_k=3):
        """
        Retrieves the most similar cases to the given problem and updates their usage_count.
        Only retrieves cases with a rating greater than 2.
        """
        query = """
            SELECT * 
            FROM abstract_problems 
            WHERE cluster = ? 
        """
        params = (problem.cluster,)
        rows = self.conn.execute(query, params).fetchall()
        cases_with_similarity = []
        for row in rows:
            stored_periods_id = [p['period_id'] for p in json.loads(row['preferred_periods'])]

            author_data = json.loads(row['preferred_author'])
            stored_author = Author(
                author_id=author_data['author_id'],
                author_name=author_data["author_name"],
                main_periods=[Period(period_id=p['period_id']) for p in author_data.get('main_periods', [])]
            )

            preferred_themes = ast.literal_eval(row['preferred_themes'])

            similarity = self.calculate_similarity(
                problem_group_size=problem.group_size,
                problem_group_type=problem.group_type,
                problem_art_knowledge=problem.art_knowledge,
                problem_preferred_periods=problem.preferred_periods,
                problem_preferred_author=problem.preferred_author,
                problem_preferred_themes=problem.preferred_themes,
                problem_time_coefficient=problem.time_coefficient,
                stored_group_size=row['group_size'],
                stored_group_type=row['group_type'],
                stored_art_knowledge=row['art_knowledge'],
                stored_preferred_periods_id=stored_periods_id,
                stored_preferred_author=stored_author,
                stored_preferred_themes=preferred_themes,
                stored_time_coefficient=row['time_coefficient']
            )

            feedback = row['feedback']
            distance = similarity * feedback

            cases_with_similarity.append((row, distance))

            # Sort by distance and return top_k
            ranked_cases = sorted(cases_with_similarity, key=lambda x: x[1], reverse=True)
            selected_cases = ranked_cases[:top_k]

            # Update usage_count
            for case, dist in selected_cases:
                self.increment_usage_count(case['id']) 

            return selected_cases

    def increment_usage_count(self, case_id):
        """Increments usage_count each time a case is retrieved."""
        cursor = self.conn.execute("SELECT usage_count FROM abstract_problems WHERE id = ?", (case_id,))
        result = cursor.fetchone()
        if result is not None and result[0] is not None:
            usage_count = result[0]
        else:
            usage_count = 0

        usage_count += 1
        self.conn.execute("UPDATE abstract_problems SET usage_count = ? WHERE id = ?", (usage_count, case_id))
        self.conn.commit()

    def store_case(self, specific_problem: SpecificProblem, user_feedback: int, visited_count: int, clustering: 'Clustering'):
        """
        Stores a SpecificProblem and its corresponding AbstractProblem in the database.

        :param specific_problem: SpecificProblem instance containing user-defined details.
        :param user_feedback: User feedback on the recommended route (1-5).
        :param visited_count: Number of artworks visited in the recommended route.
        :param clustering: An instance of the Clustering class used for assigning clusters.
        """
        
        abstract_problem = AbstractProblem(specific_problem, periods, authors, theme_instances)

        cursor = self.conn.cursor()

        # Insert SpecificProblem into the specific_problems table
        cursor.execute("""
            INSERT INTO specific_problems
            (group_id, num_people, favorite_author, favorite_period, favorite_theme, guided_visit, minors, num_experts, past_museum_visits, group_description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            specific_problem.group_id,
            specific_problem.num_people,
            specific_problem.favorite_author,
            specific_problem.favorite_period,
            specific_problem.favorite_theme,
            1 if specific_problem.guided_visit else 0,
            1 if specific_problem.minors else 0,
            specific_problem.num_experts,
            specific_problem.past_museum_visits,
            specific_problem.group_description
        ))
        specific_problem_id = specific_problem.group_id

        # Prepare JSON-serialized fields for AbstractProblem
        preferred_periods_json = json.dumps(
            [asdict(p) for p in abstract_problem.preferred_periods],
            ensure_ascii=False
        )
        preferred_author_json = json.dumps(
            asdict(abstract_problem.preferred_author),
            ensure_ascii=False
        ) if abstract_problem.preferred_author else None
        preferred_themes_json = json.dumps(abstract_problem.preferred_themes, ensure_ascii=False)

        # Assign the cluster using the Clustering system
        new_case = {
            'num_people': specific_problem.num_people,
            'favorite_author': specific_problem.favorite_author,
            'favorite_period': specific_problem.favorite_period,
            'favorite_theme': specific_problem.favorite_theme,
            'guided_visit': 1 if specific_problem.guided_visit else 0,
            'minors': 1 if specific_problem.minors else 0,
            'num_experts': specific_problem.num_experts,
            'past_museum_visits': specific_problem.past_museum_visits
        }
        cluster = clustering.classify_new_case(new_case)

        # Insert AbstractProblem into the abstract_problems table
        cursor.execute("""
            INSERT INTO abstract_problems
            (specific_problem_id, group_id, group_size, group_type, art_knowledge, preferred_periods, preferred_author, preferred_themes, time_coefficient, ordered_artworks, ordered_artworks_matches, visited_artworks_count, group_description, rating, cluster)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            specific_problem_id,
            abstract_problem.group_id,
            abstract_problem.group_size,
            abstract_problem.group_type,
            abstract_problem.art_knowledge,
            preferred_periods_json,
            preferred_author_json,
            preferred_themes_json,
            abstract_problem.time_coefficient,
            json.dumps([], ensure_ascii=False),  
            json.dumps([], ensure_ascii=False),  
            visited_count,
            abstract_problem.group_description,
            user_feedback,  
            cluster
        ))
        self.conn.commit()

    def forget_cases(self, threshold=0.15):
        """Removes cases with low utility from the database."""
        with self.conn:
            self.conn.execute("DELETE FROM abstract_problems WHERE utility <= ?", (threshold,))

    def adapt_case(self):
        """Adapts a retrieved case to a new problem if needed."""
        pass

    def calculate_redundancy(self):
        """
        Calculate redundancy for each case.
        Redundancy is defined as the fraction of other cases that are very similar (>0.9) to this one.
        """
        cursor = self.conn.execute("SELECT * FROM abstract_problems")
        all_cases = cursor.fetchall()

        cases = []
        for row in all_cases:
            author_data = json.loads(row['preferred_author']) if row['preferred_author'] else {}
            stored_author = Author(
                author_id=author_data.get('author_id', None),
                author_name=author_data.get('author_name', ""),
                main_periods=[Period(period_id=p['period_id']) for p in author_data.get('main_periods', [])]
            )

            stored_periods = json.loads(row['preferred_periods']) if row['preferred_periods'] else []
            periods_list = [Period(period_id=p['period_id']) for p in stored_periods]
            themes = ast.literal_eval(row['preferred_themes']) if row['preferred_themes'] else []

            case_params = {
                "group_size": row['group_size'],
                "group_type": row['group_type'],
                "art_knowledge": row['art_knowledge'],
                "preferred_periods": periods_list,
                "preferred_author": stored_author,
                "preferred_themes": themes,
                "time_coefficient": row['time_coefficient']
            }
            cases.append((row['id'], case_params))

        total_cases = len(cases)
        for i, (case_id, case_params) in enumerate(cases):
            if total_cases <= 1:
                redundancy = 0
            else:
                count_similar = 0
                for j, (other_id, other_params) in enumerate(cases):
                    if i == j:
                        continue

                    sim = self.calculate_similarity(
                        problem_group_size=case_params["group_size"],
                        problem_group_type=case_params["group_type"],
                        problem_art_knowledge=case_params["art_knowledge"],
                        problem_preferred_periods=case_params["preferred_periods"],
                        problem_preferred_author=case_params["preferred_author"],
                        problem_preferred_themes=case_params["preferred_themes"],
                        problem_time_coefficient=case_params["time_coefficient"],
                        stored_group_size=other_params["group_size"],
                        stored_group_type=other_params["group_type"],
                        stored_art_knowledge=other_params["art_knowledge"],
                        stored_preferred_periods_id=[p.period_id for p in other_params["preferred_periods"]],
                        stored_preferred_author=other_params["preferred_author"],
                        stored_preferred_themes=other_params["preferred_themes"],
                        stored_time_coefficient=other_params["time_coefficient"]
                    )

                    if sim > 0.9:
                        count_similar += 1
                redundancy = count_similar / (total_cases - 1)
                redundancy = round(redundancy, 2)

            self.conn.execute("UPDATE abstract_problems SET redundancy = ? WHERE id = ?", (redundancy, case_id))
        self.conn.commit()

    def calculate_utility(self):
        """
        Recalculate utility considering the rating, usage_count, and redundancy.
        
        Steps:
        - Compute a feedback list from ordered_artworks_matches and rating using get_feedback_list().
        - normalized_feedback = average(feedback_list)/5.0 (if rating is given on scale 1-5)
        - normalized_usage = usage_count / max_usage_count
        - non_redundancy_factor = (1 - redundancy)
        - utility = 0.5 * normalized_feedback + 0.3 * normalized_usage + 0.2 * non_redundancy_factor
        """
        self.ensure_columns()
        self.calculate_redundancy()

        cursor = self.conn.execute("SELECT MAX(usage_count) FROM abstract_problems")
        max_usage = cursor.fetchone()[0]
        if max_usage is None or max_usage == 0:
            max_usage = 1

        # Retrieve required data for all cases
        cursor = self.conn.execute("SELECT id, ordered_artworks_matches, rating, usage_count, redundancy FROM abstract_problems")
        rows = cursor.fetchall()

        for case_id, ordered_artworks_matches_str, rating, usage_count, redundancy in rows:
            feedback_list = self.get_feedback_list(ordered_artworks_matches_str, rating)
            if feedback_list:
                avg_feedback = sum(feedback_list) / len(feedback_list)
            else:
                avg_feedback = 0.0

            normalized_feedback = avg_feedback / 5.0
            normalized_usage = usage_count / max_usage
            non_redundancy_factor = 1 - redundancy
            if non_redundancy_factor < 0:
                non_redundancy_factor = 0

            utility = (0.5 * normalized_feedback) + (0.3 * normalized_usage) + (0.2 * non_redundancy_factor)
            utility = round(utility, 2)
            self.conn.execute("UPDATE abstract_problems SET utility = ? WHERE id = ?", (utility, case_id))

        self.conn.commit()

    def get_feedback_list(self, ordered_artworks_matches_str: str, rating: float) -> List[float]:
        """
        Given the ordered_artworks_matches (a string representation of matches) and a single rating value,
        produce a feedback list where each element corresponds to one artwork.
        
        The logic:
        - Parse ordered_artworks_matches to get a list of numeric match values.
        - Find the maximum match value.
        - For each match value, the feedback is scaled based on (match / max_match) * rating,
        but we also enforce a minimum threshold so that feedback values remain closer to the original rating.
        
        If ordered_artworks_matches_str is empty or rating is 0, returns an empty list.
        """

        if not ordered_artworks_matches_str or rating is None or rating == 0:
            return []

        try:
            matches = list(map(float, ordered_artworks_matches_str.split(',')))
        except ValueError:
            # If parsing fails or empty string
            return []

        if not matches:
            return []

        max_match = max(matches)
        if max_match == 0:
            # Avoid division by zero
            return [rating for _ in matches]

        # Define a minimum fraction of the rating that no feedback should fall below (70% of the rating)
        min_fraction = 0.7
        min_feedback = rating * min_fraction

        feedback_list = []
        for m in matches:
            scaled_value = (m / max_match) * rating
            # Enforce the minimum feedback threshold
            if scaled_value < min_feedback:
                scaled_value = min_feedback
            feedback_list.append(scaled_value)

        return feedback_list



'''if __name__ == '__main__':
    cbr = CBR()
    
    cbr.calculate_redundancy()
    print("Redundancy calculated.")

    cbr.calculate_utility()
    print("Utility calculated.")'''
