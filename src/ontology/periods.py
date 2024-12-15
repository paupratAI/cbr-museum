from entities import Period

# Periods remember we assign themes's labels to periods
periods_instances = [
    Period(1, 1000, 1150, ["Sadness", "Christianity", "Antiquity", "Magic"], "Romanesque"),
    Period(2, 1140, 1400, ["Christianity", "Battles and Wars", "Antiquity", "Monarchies", "Greek Mythology"], "Gothic"),
    Period(3, 1250, 1380, ["Islam", "Conquests", "Flora", "Landscapes", "Maritime Scenes"], "Islamic Golden Age"),
    Period(4, 1300, 1400, ["Astrology", "Alchemy", "Occult", "Mysticism", "Ancient Rituals"], "Proto-Renaissance"),
    Period(5, 1400, 1500, ["Joy", "Love", "Hope", "Christianity", "Landscapes"], "Early Renaissance"),
    Period(6, 1500, 1520, ["Christianity", "Greek Mythology", "Nostalgia", "Antiquity"], "High Renaissance"),
    Period(7, 1520, 1600, ["Love", "Despair", "Monarchies", "Christianity", "Mysticism"], "Mannerism"),
    Period(8, 1600, 1650, ["Christianity", "Monarchies", "Occult", "Astrology", "Mysticism"], "Early Baroque"),
    Period(9, 1650, 1720, ["Christianity", "Monarchies", "Landscapes", "Love"], "High Baroque"),
    Period(10, 1720, 1760, ["Nostalgia", "Joy", "Greek Mythology", "Fauna"], "Rococo"),
    Period(11, 1760, 1790, ["Revolutions", "Battles and Wars", "Hope", "Antiquity"], "Neoclassicism"),
    Period(12, 1790, 1850, ["Love", "Sadness", "Nostalgia", "Mysticism", "Landscapes"], "Romanticism"),
    Period(13, 1848, 1900, ["Sadness", "Battles and Wars", "Landscapes"], "Realism"),
    Period(14, 1860, 1880, ["Joy", "Landscapes", "Mysticism", "Christianity", "Love"], "Impressionism"),
    Period(15, 1880, 1910, ["Despair", "Nostalgia", "Mysticism", "Occult"], "Post-Impressionism"),
    Period(16, 1905, 1933, ["Mysticism", "Sadness", "Joy", "Astrology"], "Expressionism"),
    Period(17, 1907, 1930, ["Christianity", "Mysticism", "Greek Mythology", "Fauna"], "Cubism"),
    Period(18, 1920, 1950, ["Magic", "Mysticism", "Occult", "Alchemy"], "Surrealism"),
    Period(19, 1940, 1960, ["Revolutions", "Despair", "Mysticism", "Astrology"], "Abstract Expressionism"),
    Period(20, 1960, 1980, ["Sadness", "Joy", "Love", "Landscapes"], "Pop Art"),
    Period(21, 1980, 2000, ["Christianity", "Landscapes", "Joy", "Love"], "Contemporary Art")
]

periods = {p.period_id: p for p in periods_instances}