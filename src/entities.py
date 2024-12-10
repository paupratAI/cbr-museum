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
    author_name: str = None
    main_periods: List['Period'] = field(default_factory=list)

    def __hash__(self):
        return hash(self.author_id)

    def __eq__(self, other):
        if not isinstance(other, Author):
            return False
        return self.author_id == other.author_id

@dataclass
class Theme:
    theme_name: str
    labels: List[str] = field(default_factory=list)

@dataclass
class Period:
    period_id: int
    year_beginning: int = 1000
    year_end: int = 1900
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
    dimension: float
    relevance: float
    complexity: float
    default_time: int
    artwork_style: List[Style] = field(default_factory=list)

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
        available_themes: List['Theme']
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
        if not favorite_theme_choice or favorite_theme_choice.lower() == "any":
            return [t.theme_name for t in self.available_themes]
        
        theme = next(
            (t for t in self.available_themes if t.theme_name.lower() == favorite_theme_choice.lower()),
            None
        )
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


@dataclass
class AbstractSolution:
    related_to_AbstractProblem: AbstractProblem
    matches: List[Match] = field(default_factory=list)
    max_score: int = 0
    ordered_artworks: List[int] = field(default_factory=list)  # New attribute

    def compute_matches(self, artworks: List[Artwork]):
        ap = self.related_to_AbstractProblem
        preferred_author = ap.get_preferred_author()
        preferred_author_id = preferred_author.author_id if preferred_author else None
        preferred_themes = ap.get_preferred_themes()
        preferred_periods = ap.get_preferred_periods()

        for art in artworks:
            match_score = 0
            
            # Author
            if preferred_author is None or art.created_by.author_id == preferred_author_id:
                match_score += 1

            # Theme
            if len(preferred_themes) == 0 or art.artwork_theme.lower() in [t.lower() for t in preferred_themes]:
                match_score += 1

            # Period
            if (len(preferred_periods) == 0 or 
                any(p.year_beginning <= art.artwork_in_period.year_beginning <= p.year_end for p in preferred_periods)):
                match_score += 1

            time_coef = ap.get_time_coefficient()
            final_time = art.default_time * time_coef
            self.matches.append(Match(art, match_score, final_time))
            if match_score > self.max_score:
                self.max_score = match_score

        # Once all matches are calculated, sort and store the list of IDs
        sorted_matches = sorted(self.matches, key=lambda m: m.match_type, reverse=True)
        self.ordered_artworks = [m.artwork.artwork_id for m in sorted_matches]

@dataclass
class SpecificSolution:
    """Class that takes an AbstractSolution and a practical context (days, daily time, mobility),
    distributes the artworks across days, and calculates a "route" through the rooms, imitating Refinement in CLIPS."""
    related_to_AbstractSolution: AbstractSolution
    reduced_mobility: bool = False
    total_days: int = 1
    daily_minutes: int = 480  # Default 8 hours
    day_assignments: Dict[int, List[Artwork]] = field(default_factory=dict)

    def distribute_artworks(self):
        """Assigns the artworks obtained in AbstractSolution to several days, considering daily_minutes."""
        # Sort by match_type in descending order, similar to CLIPS
        ordered = sorted(self.related_to_AbstractSolution.matches, key=lambda x: x.match_type, reverse=True)

        # Initialize time per day
        day_time = {d: 0 for d in range(1, self.total_days+1)}

        for m in ordered:
            assigned = False
            for d in range(1, self.total_days+1):
                if day_time[d] + m.artwork_time <= self.daily_minutes:
                    day_time[d] += m.artwork_time
                    if d not in self.day_assignments:
                        self.day_assignments[d] = []
                    self.day_assignments[d].append(m.artwork)
                    assigned = True
                    break
            if not assigned:
                # Not enough time in available days
                # Depending on the logic, you could skip or try to adjust
                pass

    def find_entry_room(self, museum: Museum) -> Optional[Room]:
        for r in museum.rooms:
            if r.is_entry:
                return r
        return None

    def find_exit_room(self, museum: Museum) -> Optional[Room]:
        for r in museum.rooms:
            if r.is_exit:
                return r
        return None

    def find_route_for_day(self, day: int, museum: Museum) -> List[Room]:
        """Finds a simplified route: start at an entry room, visit the rooms of the artworks, and exit.
        A pathfinding algorithm (BFS, DFS, A*) could be implemented here, taking reduced mobility into account.
        For simplicity, we will do a trivial approximation.

        NOTE: This is a simplified implementation as an example.
        """
        entry = self.find_entry_room(museum)
        exit_room = self.find_exit_room(museum)
        if not entry or not exit_room:
            return []

        # Target rooms: rooms where the artworks for that day are located
        target_rooms_ids = set()
        for art in self.day_assignments.get(day, []):
            # art.artwork_in_room must be the name of the room; we will need to get the room instance
            room_obj = next((r for r in museum.rooms if r.room_name == art.artwork_in_room), None)
            if room_obj:
                target_rooms_ids.add(room_obj.room_id)

        # Assume a simple path: entry -> each target room -> exit
        # In a real case, a pathfinding algorithm would be implemented.
        # Here, for simplicity, we return a fictitious list assuming direct connection.
        path = [entry]
        for rid in target_rooms_ids:
            r = next((ro for ro in museum.rooms if ro.room_id == rid), None)
            if r:
                # If there is reduced mobility, avoid rooms with stairs
                # Here, we would need to check the path. For simplicity,
                # we assume the path is direct.
                if self.reduced_mobility and r.is_stairs:
                    # Find an alternative... (Omitted for simplicity)
                    pass
                path.append(r)

        path.append(exit_room)
        return path

    def find_all_routes(self, museum: Museum) -> Dict[int, List[Room]]:
        """Generates the routes for each day and returns them in a dictionary."""
        routes = {}
        for d in range(1, self.total_days+1):
            routes[d] = self.find_route_for_day(d, museum)
        return routes