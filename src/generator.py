from dataclasses import dataclass, field, asdict
import json
import random 
from flores.entities import Author, Period, Style, Artwork, AbstractProblem
from periods import periods
from themes import theme_instances

from preferences_generator import PreferencesGenerator
from utils import save_in_sqlite3, calculate_default_time
from flores.entities import AbstractSolution
from utils import save_in_sqlite3
from cbr import CBR

@dataclass
class GenArtArgs():

    data: list = field(default_factory=list)
    num_artworks: int = 10
    num_cases: int = 100
    format: str = "sqlite"

    def __post_init__(self):
        with open("data/filtered_artworks.json", "r", encoding="utf-8") as file:
            self.data = json.load(file)

if __name__ == "__main__":
    gen_art_args = GenArtArgs()
    artworks_data = gen_art_args.data[:gen_art_args.num_artworks]
    authors = set()
    artworks = []
    for artwork in artworks_data:
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
        # Seleccionar período válido en caso de que el año de la obra no esté en ninguno de los períodos, seleccionaremos uno aleatorio
        year = artwork["artwork_in_period"]
        random.shuffle(periods)
        period = next((p for p in periods if p.year_beginning <= year <= p.year_end), periods[0])

        # Tema y estilo
        theme = random.choice(period.themes)

        styles = []
        for style in artwork["style"]:
            style = Style(style_name=style)
            styles.append(style)

        # Otras características de la obra
        dimension = int(artwork["dimension"])
        relevance = True if artwork["relevance"] == "High" else False
        complexity = int(artwork["complexity"])

        # Calcular el tiempo predeterminado
        default_time = calculate_default_time(dimension, complexity, relevance)

        # Crear la instancia de Artwork
        artwork_instance = Artwork(
            artwork_id=artwork["artwork_id"],
            artwork_name=artwork["artwork_name"],
            artwork_in_room=None,
            created_by=author,
            artwork_in_period=period,
            artwork_theme=theme,
            artwork_style=styles,
            dimension=dimension,
            relevance=relevance,
            complexity=complexity,
            default_time=default_time
        )
        artworks.append(artwork_instance)
    
    # Create a preferences generator
    results = []
    preferences_generator = PreferencesGenerator(themes=theme_instances,authors=list(authors))
    for _ in range(gen_art_args.num_cases):
        sp = preferences_generator.sample()

        ap = AbstractProblem(
            specific_problem=sp,
            available_periods=periods,
            available_authors=list(authors),
            available_themes=theme_instances)
        
        # Crear AbstractSolution y computar matches
        asol = AbstractSolution(related_to_AbstractProblem=ap)
        asol.compute_matches(artworks=artworks)
        
        # Guardamos la tupla (ap, asol) en results para luego guardarlo en DB
        results.append((ap, asol))

    if gen_art_args.format == "json":
        serializable_results = []
        for ap in results:
            ap_dict = {
                "group_size": ap.group_size,
                "group_type": ap.group_type,
                "art_knowledge": ap.art_knowledge,
                "preferred_periods": [asdict(p) for p in ap.preferred_periods],
                "preferred_author": asdict(ap.preferred_author) if ap.preferred_author else None,
                "preferred_themes": ap.preferred_themes,
                "time_coefficient": ap.time_coefficient
            }
            serializable_results.append(ap_dict)

        with open("data/database.json", "w", encoding="utf-8") as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=4)

    elif gen_art_args.format == "sqlite":
        pass
        #save_in_sqlite3(results)
    
    '''cbr = CBR()
    print(ap.group_size, ap.group_type, ap.art_knowledge, ap.preferred_periods, ap.preferred_author, ap.preferred_themes, ap.time_coefficient)
    print()
    retrieved_cases = cbr.retrieve_cases(ap)
    for case, similarity in retrieved_cases:
        print(similarity)
        print()'''
        