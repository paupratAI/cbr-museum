from dataclasses import dataclass, field, asdict
import json
import random 
from entities import Author, Period, Style, Artwork, AbstractProblem, SpecificSolution
from ontology.periods import periods
from ontology.themes import theme_instances
from authors import authors
from ontology.art_theme_pairs import art_theme_pairs

from preferences_generator import PreferencesGenerator, TimeLimitGenerator
from utils import save_in_sqlite3, calculate_default_time
from entities import AbstractSolution
from utils import save_in_sqlite3
from cbr import CBR
from feedback import generate_and_parse_museum_feedback


@dataclass
class GenArtArgs():

    data: list = field(default_factory=list)
    reference_preferences_proportion: float = 0.75
    num_artworks: int = 50
    num_cases: int = 2000
    format: str = "sqlite"

    def __post_init__(self):
        with open("data/sorted_artworks.json", "r", encoding="utf-8") as file:
            self.data = json.load(file)

class ArtGenerator:
    def __init__(self, args: GenArtArgs):
        self.args = args
        self.artworks = []
        self.authors_set = set()
        self.results = []
        self.cases_data = []

    def prepare_artworks(self):
        artworks_data = self.args.data[:self.args.num_artworks]
        for artwork in artworks_data:
            author_name = artwork["created_by"]
            author = authors[author_name]
            self.authors_set.add(author)

            name = artwork["artwork_name"]
            
            year = artwork["artwork_in_period"]
            matching_periods = [p for p in periods if p.year_beginning <= year <= p.year_end]
            period = matching_periods if matching_periods else [random.choice(periods)]

            artwork_id = artwork["artwork_id"]
            theme_name = art_theme_pairs[artwork_id]

            styles = [Style(style_name=s) for s in artwork["style"]]
            dimension = int(artwork["dimension"])
            relevance = True if artwork["relevance"] == "High" else False
            complexity = int(artwork["complexity"])
            default_time = calculate_default_time(dimension, complexity, relevance)

            artwork_instance = Artwork(
                artwork_id=artwork_id,
                artwork_name=name,
                artwork_in_room=None,
                created_by=author,
                artwork_in_period=period,
                artwork_theme=theme_name,
                artwork_style=styles,
                dimension=dimension,
                relevance=relevance,
                complexity=complexity,
                default_time=default_time
            )
            self.artworks.append(artwork_instance)

    def generate_cases(self):
        pg = PreferencesGenerator(themes=theme_instances, authors=list(self.authors_set))
        num_reference_samples = int(self.args.num_cases * self.args.reference_preferences_proportion)
        data_sample = pg.generate_sample_data(num_reference_samples=num_reference_samples, num_total_samples=self.args.num_cases)

        for i, sp in enumerate(data_sample):
            print(f"Generating case {i+1}/{self.args.num_cases} ({((i+1)/self.args.num_cases)*100:.2f}%)", end="\r")

            abs_prob = AbstractProblem(
                specific_problem=sp,
                available_periods=periods,
                available_authors=list(self.authors_set),
                available_themes=theme_instances
            )

            abs_sol = AbstractSolution(related_to_AbstractProblem=abs_prob)
            abs_sol.compute_matches(artworks=self.artworks)

            t = TimeLimitGenerator(low=35, high=400)
            time = t.generate()
            reduced_mobility = random.choices([True, False], weights=[0.15, 0.85], k=1)[0]

            spec_sol = SpecificSolution(
                related_to_AbstractSolution=abs_sol,
                reduced_mobility=reduced_mobility,
                total_days=1,
                daily_minutes=time,
            )
            spec_sol.distribute_artworks()

            textual_feedback = random.choice(["full", "short", "None"])

            full_feedback = generate_and_parse_museum_feedback(
                group_size=abs_prob.group_size,
                group_type=abs_prob.group_type,
                group_description=abs_prob.group_description,
                reduced_mobility=reduced_mobility,
                art_knowledge_level=abs_prob.art_knowledge,
                preferred_periods=abs_prob.preferred_periods,
                preferred_authors=abs_prob.preferred_author,
                preferred_themes=abs_prob.preferred_themes,
                time_coefficient=abs_prob.time_coefficient,
                proposed_paintings=spec_sol.day_assignments,
                route_score=abs_sol.avg_score,
                perfect_route_score=10,
                textual_feedback=textual_feedback
            )

            self.results.append((abs_prob, abs_sol, spec_sol.visited_artworks_count, full_feedback))

            case_data = {
                "group_id": abs_prob.group_id,
                "group_size": abs_prob.group_size,
                "group_type": abs_prob.group_type,
                "art_knowledge": abs_prob.art_knowledge,
                "preferred_periods_ids": [p.period_id for p in abs_prob.preferred_periods],
                "preferred_author_name": abs_prob.preferred_author.author_name if abs_prob.preferred_author else None,
                "preferred_themes": abs_prob.preferred_themes,
                "reduced_mobility": reduced_mobility,
                "time_coefficient": abs_prob.time_coefficient,
                "time_limit": time,
                "group_description": abs_prob.group_description,
                "ordered_artworks": abs_sol.ordered_artworks,
                "ordered_artworks_matches": [m.match_type for m in sorted(abs_sol.matches, key=lambda m: m.match_type, reverse=True)],
                "visited_artworks_count": spec_sol.visited_artworks_count,
                "rating": full_feedback["evaluation"],
                "textual_feedback": full_feedback["feedback"],
                "only_elevator": full_feedback["only_elevator"],
                "time_coefficient_correction": full_feedback["time_coefficient"],
                "artwork_to_remove": full_feedback["artwork_to_remove"],
                "guided_visit": full_feedback["guided_visit"]
            }

            self.cases_data.append(case_data)

    def save_results(self):
        if self.args.format == "json":
            serializable_results = []
            for abs_prob, _, _, _ in self.results:
                abs_prob_dict = {
                    "group_id": abs_prob.group_id,
                    "group_size": abs_prob.group_size,
                    "group_type": abs_prob.group_type,
                    "art_knowledge": abs_prob.art_knowledge,
                    "preferred_periods": [asdict(p) for p in abs_prob.preferred_periods],
                    "preferred_author": asdict(abs_prob.preferred_author) if abs_prob.preferred_author else None,
                    "preferred_themes": abs_prob.preferred_themes,
                    "time_coefficient": abs_prob.time_coefficient,
                    "group_description": abs_prob.group_description
                }
                serializable_results.append(abs_prob_dict)

            with open("../data/database.json", "w", encoding="utf-8") as f:
                json.dump(serializable_results, f, ensure_ascii=False, indent=4)

        elif self.args.format == "sqlite":
            """
            case_data (dict): Dictionary with the case data containing the follwing keys:
            - group_id (int): The group ID.
            - group_size (int): The group size.
            - group_type (str): The group type.
            - art_knowledge (int): The art knowledge level.
            - preferred_periods_ids (list[int]): The list of preferred periods IDs of the group.
            - preferred_author_name (str): The preferred author name of the group.
            - preferred_themes (list[str]): The list of preferred subthemes of the group.
            - reduced_mobility (int): 1 if the group has reduced mobility, 0 otherwise.
            - time_coefficient (float): The time coefficient.
            - time_limit (float): The time limit for the group visit.
            - group_description (str): The group description.
            - ordered_artworks (list[int]): The list of ordered arwork IDs of the group.
            - ordered_artworks_matches (list[float]): The list of ordered artwork matches of the group.
            - visited_artworks_count (int): The number of visited artworks.
            - rating (int): The rating of the group.
            - textual_feedback (str): The textual feedback of the group.
            - only_elevator (int): 1 if the group should use only the elevator, 0 otherwise.
            - time_coefficient_correction (str): The time coefficient correction.
            - artwork_to_remove (str): The artwork to remove, if any (None otherwise).
            - guided_visit (int): 1 if the group should have a guided visit, 0 otherwise.
            """
            save_in_sqlite3(cases_data=self.cases_data)

    def run(self):
        self.prepare_artworks()
        self.generate_cases()
        self.save_results()


if __name__ == "__main__":
    gen_art_args = GenArtArgs()
    art_generator = ArtGenerator(gen_art_args)
    art_generator.run()