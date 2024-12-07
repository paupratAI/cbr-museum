from entities import Museum, Room, Author, Theme, Period, Artwork, SpecificProblem, Match
from typing import List, Dict

class CBRSystem:
    def __init__(self):
        self.case_library = []

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
        ranked_cases = sorted(
            [(stored_case, self.calculate_similarity(problem, stored_case["problem"])) for stored_case in self.case_library],
            key=lambda x: x[1],
            reverse=True
        )
        return ranked_cases[:top_k]

    def store_case(self, problem: SpecificProblem, route_artworks: List[int], feedback: List[int]):
        """Stores a new case in the library."""
        case = {
            "problem": problem,
            "route_artworks": route_artworks,
            "feedback": feedback,
            "utility": sum(feedback) / len(feedback) if feedback else 0
        }
        self.case_library.append(case)

    def forget_cases(self, threshold=0.05):
        """Removes cases with low utility."""
        self.case_library = [case for case in self.case_library if case["utility"] > threshold]

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

cbr_system.store_case(stored_problem_1, [1, 2, 3], [4, 5, 3])
cbr_system.store_case(stored_problem_2, [4, 5, 6], [5, 5, 4])
cbr_system.store_case(stored_problem_3, [7, 8, 9], [3, 4, 5])

# Create a new problem
new_problem = SpecificProblem(12, 1, 1605, "historical", True, False, 1, 10)

# Retrieve the most similar cases
retrieved_cases = cbr_system.retrieve_cases(new_problem)
print("Retrieved Cases:")
for case, similarity in retrieved_cases:
    print(f"Problem: {case['problem']}, Similarity: {similarity:.2f}")