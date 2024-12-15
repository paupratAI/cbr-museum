from dataclasses import dataclass

@dataclass
class Case:
	case_id: int
	group_id: int
	group_size: int
	group_type: str
	art_knowledge: int
	preferred_periods_ids: list[int]
	preferred_author_name: str
	preferred_themes: list[str]
	reduced_mobility: int
	time_coefficient: float
	group_description: str
	ordered_artworks: list[int]
	ordered_artworks_matches: list[float]
	visited_artworks_count: int
	rating: int
	textual_feedback: str
	only_elevator: int
	time_coefficient_correction: str
	artwork_to_remove: str
	guided_visit: int
	cluster_id: int
	redundancy: float
	usage_count: int
	utility: float
