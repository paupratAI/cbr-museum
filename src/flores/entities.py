from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class Museum:
    museum_id: int
    museum_name: str
    rooms: List['Room'] = field(default_factory=list)
    auxiliary_rooms: List['Room'] = field(default_factory=list)

@dataclass
class Room:
    room_id: int
    room_in_museum: str
    is_entry: bool
    is_exit: bool
    is_stairs: bool
    is_elevator: bool
    room_name: Optional[str] = None
    adjacent_rooms: List['Room'] = field(default_factory=list)

    def __post_init__(self):
        assert not (self.is_entry and self.is_stairs), "The entry cannot be stairs."
        if self.room_name is None:
            self.room_name = f"room{self.room_id}"

@dataclass
class Author:
    author_id: int
    author_name: str
    main_periods: List['Period'] = field(default_factory=list)

@dataclass
class Theme:
    theme_name: str
    labels: List[str] = field(default_factory=list)

@dataclass
class Period:
    period_id: int
    year_beginning: int
    year_end: int
    themes: List[str] = field(default_factory=list)
    period_name: Optional[str] = None

    def __post_init__(self):
        if self.period_name is None:
            self.period_name = f"period{self.period_id}"

@dataclass
class Style:
    style_name: str

@dataclass
class Artwork:
    artwork_id: int
    artwork_name: str
    artwork_in_room: Optional[str]
    created_by: Author
    artwork_in_period: Period
    artwork_theme: str
    artwork_style: List[Style] = field(default_factory=list)
    dimension: float
    relevance: float
    complexity: float
    default_time: int

@dataclass
class SpecificProblem:
    num_people: int
    favorite_author: Optional[int]  # Author ID
    favorite_period: Optional[int]  # Year
    favorite_theme: Optional[str]
    guided_visit: bool
    minors: bool
    num_experts: int
    past_museum_visits: int

    def __post_init__(self):
        assert isinstance(self.num_people, int) and 1 <= self.num_people <= 50, "num_people must be between 1 and 50"
        assert isinstance(self.favorite_author, (int, type(None))), "favorite_author must be an integer or None"
        assert isinstance(self.favorite_period, (int, type(None))), "favorite_period must be an integer or None"
        assert isinstance(self.favorite_theme, (str, type(None))), "favorite_theme must be a string or None"
        assert isinstance(self.guided_visit, bool), "guided_visit must be a boolean"
        assert isinstance(self.minors, bool), "minors must be a boolean"
        assert isinstance(self.num_experts, int) and 0 <= self.num_experts <= self.num_people, "num_experts must be between 0 and num_people"
        assert isinstance(self.past_museum_visits, int) and 0 <= self.past_museum_visits <= 50, "past_museum_visits must be between 0 and 50"

class AbstractProblem:
    def __init__(
        self,
        specific_problem: 'SpecificProblem',
        available_periods: List['Period'],
        available_authors: List['Author'],
        available_themes: Dict[str, 'Theme']
    ):
        self.specific_problem = specific_problem
        self.available_periods = available_periods
        self.available_authors = available_authors
        self.available_themes = available_themes

        self.group_size = self.compute_group_size()
        self.group_type = self.compute_group_type()
        self.art_knowledge = self.compute_art_knowledge()
        self.preferred_periods = self.compute_preferred_periods()
        self.preferred_author = self.compute_preferred_author()
        self.preferred_themes = self.compute_preferred_themes()
        self.time_coefficient = self.compute_time_coefficient()

        # Assertions
        assert isinstance(self.preferred_periods, list) and all(isinstance(p, Period) for p in self.preferred_periods), \
            "preferred_periods must be a list of Period instances"
        assert isinstance(self.preferred_author, (Author, type(None))), \
            "preferred_author must be an Author instance or None"
        assert isinstance(self.art_knowledge, int) and 1 <= self.art_knowledge <= 4, \
            "art_knowledge must be between 1 and 4"
        assert isinstance(self.group_size, int) and 1 <= self.group_size <= 4, \
            "group_size must be between 1 and 4"
        assert self.group_type in {"casual", "family", "scholar"}, \
            "group_type must be 'casual', 'family', or 'scholar'"
        assert isinstance(self.preferred_themes, list) and all(isinstance(t, str) for t in self.preferred_themes), \
            "preferred_themes must be a list of strings"
        assert isinstance(self.time_coefficient, float) and self.time_coefficient > 0, \
            "time_coefficient must be a positive float"

    def compute_group_size(self) -> int:
        num_people = self.specific_problem.num_people
        if num_people < 1:
            return 1
        elif 1 <= num_people <= 5:
            return 2
        elif 6 <= num_people <= 15:
            return 3
        else:
            return 4
        
    def compute_group_type(self) -> str:
        if self.specific_problem.minors and self.group_size < 3:
            return "family"
        elif self.specific_problem.minors and self.group_size >= 3:
            return "scholar"
        else:
            return "casual"
        
    def compute_art_knowledge(self) -> int:
        num_people = self.specific_problem.num_people
        num_experts = self.specific_problem.num_experts
        past_visits = self.specific_problem.past_museum_visits
        expertise_percentage = (num_experts / num_people) * 100 if num_people > 0 else 0

        if past_visits < 10 or expertise_percentage < 25:
            return 1
        elif 10 <= past_visits <= 20 or (25 <= expertise_percentage < 50):
            return 2
        elif 20 < past_visits <= 30 or (50 <= expertise_percentage < 75):
            return 3
        else:
            return 4
        
    def compute_preferred_periods(self) -> List['Period']:
        favorite_year = self.specific_problem.favorite_period
        if favorite_year is None:
            return self.available_periods.copy()
        else:
            return [
                period for period in self.available_periods
                if period.year_beginning <= favorite_year <= period.year_end
            ]
        
    def compute_preferred_author(self) -> 'Author':
        favorite_author_id = self.specific_problem.favorite_author
        if favorite_author_id is not None:
            return next(
                (author for author in self.available_authors if author.author_id == favorite_author_id),
                None
            )
        else:
            return None  # Represents any author

    def compute_preferred_themes(self) -> List[str]:
        favorite_theme_choice = self.specific_problem.favorite_theme
        if favorite_theme_choice is None or favorite_theme_choice.lower() == "any":
            return list(self.available_themes.keys())
        else:
            theme = self.available_themes.get(favorite_theme_choice.lower())
            return theme.labels if theme else []

    def compute_time_coefficient(self) -> float:
        if self.specific_problem.guided_visit:
            return 1.5
        elif self.group_type == "scholar":
            return 2.0
        elif self.group_type == "family":
            return 1.75
        else:
            return 1.0 + (self.group_size * 0.25) + (self.art_knowledge * 0.25)
        
    # Getter Methods
    def get_preferred_periods(self) -> List['Period']:
        """Returns the list of preferred periods."""
        return self.preferred_periods

    def get_preferred_author(self) -> Optional['Author']:
        """Returns the preferred author or None if any author is acceptable."""
        return self.preferred_author

    def get_art_knowledge(self) -> int:
        """Returns the level of art knowledge (1-4)."""
        return self.art_knowledge

    def get_group_size(self) -> int:
        """Returns the size of the group (1-4)."""
        return self.group_size

    def get_group_type(self) -> str:
        """Returns the type of the group ('casual', 'family', 'scholar')."""
        return self.group_type

    def get_preferred_themes(self) -> List[str]:
        """Returns the list of preferred themes."""
        return self.preferred_themes

    def get_time_coefficient(self) -> float:
        """Returns the time coefficient for the visit."""
        return self.time_coefficient


@dataclass
class Match:
    artwork: Artwork
    match_type: int
    artwork_time: float

    def __post_init__(self):
        assert isinstance(self.artwork, Artwork), "artwork must be an Artwork instance"
        assert isinstance(self.match_type, int) and self.match_type >= 0, "match_type must be a non-negative integer"
        assert isinstance(self.artwork_time, (int, float)) and self.artwork_time > 0, "artwork_time must be a positive number"