from dataclasses import dataclass, field, asdict
import json
import random 
from flores.entities import Author, Period  
from periods import periods
from themes import theme_instances

from preferences_generator import PreferencesGenerator
from utils import save_in_sqlite3

@dataclass
class GenArtArgs():

    data: list = field(default_factory=list)
    num_artworks: int = 10
    num_cases: int = 100
    format: str = "json"

    def __post_init__(self):
        with open("data/filtered_artworks.json", "r", encoding="utf-8") as file:
            self.data = json.load(file)

if __name__ == "__main__":
    gen_art_args = GenArtArgs()
    artworks = gen_art_args.data[:gen_art_args.num_artworks]
    authors = set()
    for artwork in artworks:
        author = Author(artwork["author_id"], artwork["created_by"])
        authors.add(author)

        num_periods = random.choices([1, 2, 3], weights=[70, 20, 10], k=1)[0]

        initial_period_index = random.randint(0, len(periods) - 1)
        main_periods = [periods[initial_period_index]]

        if num_periods > 1:
            if initial_period_index < len(periods) - 1: 
                main_periods.append(periods[initial_period_index + 1])

            if num_periods == 3 and initial_period_index > 0: 
                main_periods.append(periods[initial_period_index - 1])

        author.main_periods = main_periods
    
    # Create a preferences generator
    results = []
    preferences_generator = PreferencesGenerator(themes=theme_instances,authors=list(authors))
    for _ in range(gen_art_args.num_cases):
        sp = preferences_generator.sample()
        results.append(asdict(sp))

    if gen_art_args.format == "json":
        with open("data/database.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
    elif gen_art_args.format == "sqlite":
        save_in_sqlite3(results)