from dataclasses import dataclass, field
import json
import random 
from flores.entities import Author, Period  
from periods import periods


@dataclass
class GenArtArgs():

    data: list = field(default_factory=list)
    num_artworks: int = 10

    def __post_init__(self):
        with open("data/filtered_artworks.json", "r", encoding="utf-8") as file:
            self.data = json.load(file)

if __name__ == "__main__":
    gen_art_args = GenArtArgs()
    artworks = random.sample(gen_art_args.data, gen_art_args.num_artworks)
    authors = set()
    for artwork in artworks:
        # Crear las instancias a partir del JSON
        author = Author(artwork["author_id"], artwork["created_by"])
        authors.add(author)

        # Seleccionar si el autor tendrá uno o dos períodos principales (70% para uno, 30% para dos)
        num_periods = random.choices([1, 2, 3], weights=[70, 20, 10], k=1)[0]

        # Seleccionar un período aleatorio inicial para el autor
        initial_period_index = random.randint(0, len(periods) - 1)
        main_periods = [periods[initial_period_index]]

        # Agregar períodos adyacentes si el autor tiene más de un período principal
        if num_periods > 1:
            if initial_period_index < len(periods) - 1:  # Si no es el último, puede tener siguiente
                main_periods.append(periods[initial_period_index + 1])

            if num_periods == 3 and initial_period_index > 0:  # Si tiene 3 y no es el primero, puede tener anterior
                main_periods.append(periods[initial_period_index - 1])

        # Asignar los períodos principales al autor
        author.main_periods = main_periods
    
    print(authors)