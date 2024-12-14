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
    num_artworks: int = 10
    num_cases: int = 100
    format: str = "sqlite"

    def __post_init__(self):
        with open("../data/sorted_artworks.json", "r", encoding="utf-8") as file:
            self.data = json.load(file)

if __name__ == "__main__":
    gen_art_args = GenArtArgs()
    artworks_data = gen_art_args.data[:gen_art_args.num_artworks]
    authors_s = set()
    artworks = []
    for artwork in artworks_data:
        author_name = artwork["created_by"]
        author = authors[author_name] 
        authors_s.add(author)

        name = artwork["artwork_name"]

        # Select a valid period in case the year of the artwork does not belong to any of the periods; we will select a random one
        year = artwork["artwork_in_period"]
        random.shuffle(periods)
        period = next((p for p in periods if p.year_beginning <= year <= p.year_end), periods[0])

        # Theme and style
        id = artwork["artwork_id"]
        theme_name = art_theme_pairs[id]

        styles = []
        for style in artwork["style"]:
            style = Style(style_name=style)
            styles.append(style)

        # Other features of the artwork
        dimension = int(artwork["dimension"])
        relevance = True if artwork["relevance"] == "High" else False
        complexity = int(artwork["complexity"])

        # Calculate the default time
        default_time = calculate_default_time(dimension, complexity, relevance)

        # Create the instance of Artwork
        artwork_instance = Artwork(
            artwork_id=id,
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
        artworks.append(artwork_instance)
    
    # Create a preferences generator
    results = []
    pg = PreferencesGenerator(themes=theme_instances, authors=list(authors_s))
    num_reference_samples = int(gen_art_args.num_cases * gen_art_args.reference_preferences_proportion)
    data_sample = pg.generate_sample_data(num_reference_samples=num_reference_samples, num_total_samples=gen_art_args.num_cases)

    for sp in data_sample:
        abs_prob = AbstractProblem(
            specific_problem=sp,
            available_periods=periods,
            available_authors=list(authors_s),
            available_themes=theme_instances
        )

        abs_sol = AbstractSolution(related_to_AbstractProblem=abs_prob)
        abs_sol.compute_matches(artworks=artworks)

        t = TimeLimitGenerator(low=20, high=120)
        time = t.generate()

        # Generate reduce_mobility with weights of 0.85 False and 0.15 True
        reduced_mobility = random.choices([True, False], weights=[0.15, 0.85], k=1)[0]

        spec_sol = SpecificSolution(
            related_to_AbstractSolution=abs_sol,
            reduced_mobility=reduced_mobility,
            total_days=1,      
            daily_minutes=time,
        )
        spec_sol.distribute_artworks()

        textual_feedback = random.choice(["full", "short", "None"])

        full_feedback = generate_and_parse_museum_feedback(abs_sol.group_size, abs_sol.group_type, abs_sol.group_description,
                                                           abs_sol.reduced_mobility, abs_sol.art_knowledge, abs_sol.preferred_periods,
                                                           abs_sol.preferred_author, abs_sol.preferred_themes, abs_sol.time_coefficient, textual_feedback)

        results.append((abs_prob, abs_sol, spec_sol.visited_artworks_count, full_feedback))

    if gen_art_args.format == "json":
        serializable_results = []
        for abs_prob in results:
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

    elif gen_art_args.format == "sqlite":
        save_in_sqlite3(results)
    """
    cbr = CBR()
    print(ap.group_size, ap.group_type, ap.art_knowledge, ap.preferred_periods, ap.preferred_author, ap.preferred_themes, ap.time_coefficient)
    ap.cluster = 5
    print()
    retrieved_cases = cbr.retrieve_cases(ap)
    for case, similarity in retrieved_cases:
        print(similarity)
        print()
    cbr.calculate_redundancy()
    cbr.ensure_utility_column()
    """