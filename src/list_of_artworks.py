import json
from authors import authors
from ontology.periods import periods
import random
from ontology.art_theme_pairs import art_theme_pairs
from entities import Style, Artwork
from utils import calculate_default_time
import pandas as pd

with open("data/sorted_artworks.json", "r", encoding="utf-8") as file:
    data = json.load(file)

artworks_data = data[:50]
artworks = []
for artwork in artworks_data:
    author_name = artwork["created_by"]
    author = authors[author_name]

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
    artworks.append(artwork_instance)
artworks_dict = {art.artwork_id: art.__repr__() for art in artworks}  # Evitar comillas innecesarias
print(artworks_dict)

for artwork_id, artwork_repr in artworks_dict.items():
    print(f"{artwork_id}: {artwork_repr},")