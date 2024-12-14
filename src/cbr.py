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

        if 'usage_count' not in columns:
            self.conn.execute("ALTER TABLE abstract_problems ADD COLUMN usage_count INTEGER DEFAULT 0")
        if 'redundancy' not in columns:
            self.conn.execute("ALTER TABLE abstract_problems ADD COLUMN redundancy REAL DEFAULT 0.0")
        if 'utility' not in columns:
            self.conn.execute("ALTER TABLE abstract_problems ADD COLUMN utility REAL DEFAULT 0.0")
        self.conn.commit()

    def calculate_similarity(self, problem: AbstractProblem, group_size, group_type, art_knowledge,
                             preferred_periods_id, preferred_author, preferred_themes, time_coefficient) -> float:
        """
        Calculates the similarity between the current problem and a stored problem.
        Weights are assigned to each feature and a weighted sum is returned.
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
                    similarity += weights["preferred_author"] * 0.8 * (len(matched_author_periods) / len(problem.preferred_author.main_periods))

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
        """
        Retrieves the most similar cases to the given problem and updates their usage_count.
        
        Column order:
        0: id
        1: group_id
        2: specific_problem_id
        3: group_size
        4: group_type
        5: art_knowledge
        6: preferred_periods (JSON)
        7: preferred_author (JSON)
        8: preferred_themes (string)
        9: time_coefficient
        10: ordered_artworks
        11: ordered_artworks_matches
        12: visited_artworks_count
        13: group_description
        14: rating (single numeric value)
        15: (not used)
        16: (not used)
        17: cluster
        18: usage_count
        19: redundancy
        20: utility
        """
        query = "SELECT * FROM abstract_problems WHERE cluster = ?"
        params = (problem.cluster,)
        rows = self.conn.execute(query, params).fetchall()
        cases_with_similarity = []
        for row in rows:
            stored_periods_id = [p['period_id'] for p in json.loads(row[6])]

            author_data = json.loads(row[7])
            stored_author = Author(
                author_id=author_data['author_id'],
                author_name=author_data["author_name"],
                main_periods=[Period(period_id=p['period_id']) for p in author_data.get('main_periods', [])]
            )

            preferred_themes = ast.literal_eval(row[8])

            similarity = self.calculate_similarity(
                problem,
                group_size=row[3],
                group_type=row[4],
                art_knowledge=row[5],
                preferred_periods_id=stored_periods_id,
                preferred_author=stored_author,
                preferred_themes=preferred_themes,
                time_coefficient=row[9]
            )
            cases_with_similarity.append((row, similarity))

        # Sort by similarity and return top_k
        ranked_cases = sorted(cases_with_similarity, key=lambda x: x[1], reverse=True)
        selected_cases = ranked_cases[:top_k]

        # Update usage_count
        for case, sim in selected_cases:
            self.increment_usage_count(case[0])  # case[0] is id

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

    def store_case(self, problem: AbstractProblem, route_artworks: List[int], rating: int):
        """
        Stores a new case in the database. 
        Note: rating is a single numeric value. Feedback list is derived from rating and ordered_artworks_matches.
        
        0: id
        1: group_id
        2: specific_problem_id
        3: group_size
        4: group_type
        5: art_knowledge
        6: preferred_periods 
        7: preferred_author
        8: preferred_themes
        9: time_coefficient
        10: ordered_artworks
        11: ordered_artworks_matches
        12: visited_artworks_count
        13: group_description
        14: rating
        15: 
        16: 
        17: cluster
        18: usage_count
        19: redundancy
        20: utility
        """
        # Convert periods and author to JSON
        periods_json = json.dumps([{'period_id': p.period_id} for p in problem.preferred_periods])
        author_json = json.dumps({
            'author_id': problem.preferred_author.author_id,
            'author_name': problem.preferred_author.author_name,
            'main_periods': [{'period_id': p.period_id} for p in problem.preferred_author.main_periods]
        }) if problem.preferred_author else json.dumps({})

        # Initially, ordered_artworks_matches and visited_artworks_count are empty or zero
        ordered_artworks =  None
        ordered_artworks_matches = []  # To be updated later if needed
        visited_artworks_count = 0
        group_description = ''  # If needed
        cluster = problem.cluster
        usage_count = 0
        redundancy = 0.0
        utility = 0.0

        self.conn.execute('''
            INSERT INTO abstract_problems (
                group_id,
                specific_problem_id,
                group_size,
                group_type,
                art_knowledge,
                preferred_periods,
                preferred_author,
                preferred_themes,
                time_coefficient,
                ordered_artworks,
                ordered_artworks_matches,
                visited_artworks_count,
                group_description,
                rating,
                cluster,
                usage_count,
                redundancy,
                utility
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            None,  # group_id if needed
            problem.specific_problem_id if hasattr(problem, 'specific_problem_id') else None,
            problem.group_size,
            problem.group_type,
            problem.art_knowledge,
            periods_json,
            author_json,
            str(problem.preferred_themes),
            problem.time_coefficient,
            ordered_artworks,
            ordered_artworks_matches,
            visited_artworks_count,
            group_description,
            rating,
            cluster,
            usage_count,
            redundancy,
            utility
        ))
        self.conn.commit()

    def forget_cases(self, threshold=0.05):
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
        for c in all_cases:
            # 0: id
            # 1: group_id
            # 2: specific_problem_id
            # 3: group_size
            # 4: group_type
            # 5: art_knowledge
            # 6: preferred_periods (JSON)
            # 7: preferred_author (JSON)
            # 8: preferred_themes (string)
            # 9: time_coefficient
            # 10: ordered_artworks
            # 11: ordered_artworks_matches
            # 12: visited_artworks_count
            # 13: group_description
            # 14: rating
            # 15: 
            # 16:
            # 17: cluster
            # 18: usage_count
            # 19: redundancy
            # 20: utility

            author_data = json.loads(c[7]) if c[7] else {}
            stored_author = Author(
                author_id=author_data.get('author_id', None),
                author_name=author_data.get('author_name', ""),
                main_periods=[Period(period_id=p['period_id']) for p in author_data.get('main_periods', [])]
            )

            stored_periods = json.loads(c[6]) if c[6] else []
            periods_list = [Period(period_id=p['period_id']) for p in stored_periods]
            themes = ast.literal_eval(c[8]) if c[8] else []

            pseudo_problem = AbstractProblem(
                specific_problem=None,
                available_periods=None,
                available_authors=None,
                available_themes=None
            )
            pseudo_problem.group_size = c[3]
            pseudo_problem.group_type = c[4]
            pseudo_problem.art_knowledge = c[5]
            pseudo_problem.preferred_periods = periods_list
            pseudo_problem.preferred_author = stored_author
            pseudo_problem.preferred_themes = themes
            pseudo_problem.time_coefficient = c[9]
            pseudo_problem.cluster = c[17]

            cases.append((c[0], pseudo_problem))

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
    feedback_list = cbr.get_feedback_list("9.4,7.9,7.8,7.6,7.5,2.8,2.8,2.7,2.7,2.7", 4.5)
    print(feedback_list)'''