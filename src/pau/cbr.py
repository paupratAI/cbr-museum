import sqlite3
from entities import Museum, Room, Author, Theme, Period, Artwork, SpecificProblem, Match
from typing import List, Dict

class CBRSystem:
    def __init__(self):
        self.conn = sqlite3.connect('src/pau/db_cases.db')
        self.create_table()

    def create_table(self):
        """Creates the cases table in the database."""
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    num_people INTEGER,
                    favorite_author INTEGER,
                    favorite_period INTEGER,
                    favorite_theme TEXT,
                    guided_visit BOOLEAN,
                    minors BOOLEAN,
                    num_experts INTEGER,
                    route_artworks TEXT,
                    feedback TEXT,
                    utility REAL
                )
            ''')

    def calculate_similarity(self, problem: SpecificProblem, stored_problem: SpecificProblem) -> float:
        """Calculates the similarity between the current problem and a stored problem."""
        weights = {
            "num_people": 0.1,
            "favorite_author": 0.3,
            "favorite_period": 0.2,
            "favorite_theme": 0.2,
            "guided_visit": 0.1,
            "minors": 0.05,
            "num_experts": 0.05
        }
        similarity = 0

        # Compare the number of people (smaller difference means higher similarity)
        similarity += weights["num_people"] * (1 - abs(problem.num_people - stored_problem.num_people) / 50)

        # Compare the favorite author
        if problem.favorite_author == stored_problem.favorite_author:
            similarity += weights["favorite_author"]

        # Compare the favorite period
        if problem.favorite_period and stored_problem.favorite_period:
            similarity += weights["favorite_period"] * (1 - abs(problem.favorite_period - stored_problem.favorite_period) / 900)

        # Compare the favorite theme
        if problem.favorite_theme and problem.favorite_theme == stored_problem.favorite_theme:
            similarity += weights["favorite_theme"]

        # Compare if a guided visit is preferred
        if problem.guided_visit == stored_problem.guided_visit:
            similarity += weights["guided_visit"]

        # Compare if there are minors in the group
        if problem.minors == stored_problem.minors:
            similarity += weights["minors"]

        # Compare the number of experts in the group
        similarity += weights["num_experts"] * (1 - abs(problem.num_experts - stored_problem.num_experts) / max(problem.num_people, stored_problem.num_people))

        return similarity

    def retrieve_cases(self, problem: SpecificProblem, top_k=3):
        """Retrieves the most similar cases to the current problem."""
        query = "SELECT * FROM cases"
        rows = self.conn.execute(query).fetchall()

        # Convert rows to SpecificProblem and calculate similarity
        cases_with_similarity = []
        for row in rows:
            stored_problem = SpecificProblem(
                num_people=row[1],
                favorite_author=row[2],
                favorite_period=row[3],
                favorite_theme=row[4],
                guided_visit=bool(row[5]),
                minors=bool(row[6]),
                num_experts=row[7],
                utility=row[10]
            )
            similarity = self.calculate_similarity(problem, stored_problem)
            cases_with_similarity.append((row, similarity))

        # Sort by similarity and return top_k
        ranked_cases = sorted(cases_with_similarity, key=lambda x: x[1], reverse=True)
        return ranked_cases[:top_k]


    def store_case(self, problem: SpecificProblem, route_artworks: List[int], feedback: List[int]):
        """Stores a new case in the database if it does not already exist."""
        utility = sum(feedback) / len(feedback) if feedback else 0

        # Verify if the case already exists
        query = '''
            SELECT COUNT(*) FROM cases
            WHERE num_people = ? AND favorite_author = ? AND favorite_period = ? AND
                favorite_theme = ? AND guided_visit = ? AND minors = ? AND 
                num_experts = ? AND route_artworks = ? AND feedback = ?;
        '''
        params = (
            problem.num_people, problem.favorite_author, problem.favorite_period, problem.favorite_theme,
            problem.guided_visit, problem.minors, problem.num_experts,
            ','.join(map(str, route_artworks)), ','.join(map(str, feedback))
        )
        result = self.conn.execute(query, params).fetchone()

        if result[0] == 0:  # Case does not exist
            with self.conn:
                self.conn.execute('''
                    INSERT INTO cases (
                        num_people, favorite_author, favorite_period, favorite_theme, guided_visit, minors, num_experts, route_artworks, feedback, utility
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    problem.num_people, problem.favorite_author, problem.favorite_period, problem.favorite_theme,
                    problem.guided_visit, problem.minors, problem.num_experts,
                    ','.join(map(str, route_artworks)), ','.join(map(str, feedback)), utility
                ))

    def forget_cases(self, threshold=0.05):
        """Removes cases with low utility from the database."""
        with self.conn:
            self.conn.execute("DELETE FROM cases WHERE utility <= ?", (threshold,))

    def adapt_case(self, retrieved_case: Dict, new_problem: SpecificProblem):
        """Adapts a retrieved case to the new problem."""
        adapted_case = retrieved_case.copy()
        adapted_case["problem"] = new_problem
        return adapted_case


### How to use it: ###
cbr_system = CBRSystem()

stored_problem_1 = SpecificProblem(10, 1, 1600, "historical", True, False, 2, 5)
stored_problem_2 = SpecificProblem(15, 2, 1700, "religious", False, True, 3, 20)
stored_problem_3 = SpecificProblem(20, 3, 1800, "natural", True, True, 4, 30)
stored_problem_4 = SpecificProblem(25, 4, 1900, "modern", False, False, 5, 40)
stored_problem_5 = SpecificProblem(30, 5, 1000, "abstract", True, False, 6, 50)
stored_problem_6 = SpecificProblem(35, 6, 1100, "historical", False, True, 7, 2)
stored_problem_7 = SpecificProblem(40, 7, 1200, "religious", True, False, 8, 4)
stored_problem_8 = SpecificProblem(45, 8, 1300, "natural", False, True, 9, 34)
stored_problem_9 = SpecificProblem(50, 9, 1400, "modern", True, False, 10, 32)
stored_problem_10 = SpecificProblem(23, 10, 1500, "abstract", False, True, 11, 12)

cbr_system.store_case(stored_problem_1, [1, 2, 3], [4, 5, 3])
cbr_system.store_case(stored_problem_2, [4, 5, 6, 7], [5, 5])
cbr_system.store_case(stored_problem_3, [7, 8], [3, 4, 5, 6])
cbr_system.store_case(stored_problem_4, [9, 10, 11, 12, 13], [7, 8, 9])
cbr_system.store_case(stored_problem_5, [14, 15, 16], [10, 5, 6, 7, 3])
cbr_system.store_case(stored_problem_6, [17, 18, 19, 20], [11, 12, 13])
cbr_system.store_case(stored_problem_7, [21, 22], [14, 15, 16, 17])
cbr_system.store_case(stored_problem_8, [23, 24, 25, 26, 27], [18, 19])
cbr_system.store_case(stored_problem_9, [28, 29, 30], [20, 21, 22, 23, 24])
cbr_system.store_case(stored_problem_10, [31, 32, 33, 34], [25, 26, 27])

# Create a new problem
new_problem = SpecificProblem(12, 5, 1605, "abstract", True, False, 1, 10)

# Retrieve the most similar cases
retrieved_cases = cbr_system.retrieve_cases(new_problem)
print("Retrieved Cases:")
for case, similarity in retrieved_cases:
    print(f"Problem: id={case[0]}, num_people={case[1]}, favorite_author={case[2]}, "
          f"favorite_period={case[3]}, favorite_theme={case[4]}, "
          f"guided_visit={case[5]}, minors={case[6]}, num_experts={case[7]}, "
          f"Similarity: {similarity:.2f}")
