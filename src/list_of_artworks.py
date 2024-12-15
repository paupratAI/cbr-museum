import json
from ontology.authors import authors
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
artworks_dict = {art.artwork_id: repr(art) for art in artworks}
print(artworks_dict)