from entities import Period, Author

@dataclass
class Case:
	case_id: int
	group_id: int
	group_size: int
	group_type: str
	art_knowledge: int
	preferred_periods: list[Period]
	preferred_author: Author
	preferred_themes: list[str]
	reduced_mobility: float
	time_coefficient: float
	group_description: str
	visited_artworks_count: int
	ordered_artworks: list[int]
	ordered_artworks_matches: list[float]
	rating: int
	textual_feedback: str
	only_elevator: int
	time_coefficient_correction: str
	artwork_to_remove: str
	route_score: float
	guided_visit: int
