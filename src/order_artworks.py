import json
from collections import Counter
from typing import List, Dict, Any


class ArtworksOrganizer:
    """
    A class to organize a list of artworks by their authors.

    This class provides functionality to:
    - Count how many artworks each author has produced (by author's name).
    - Sort the artworks so that those by the most represented authors appear first.
    - Write the sorted artworks to a JSON file.
    - Print the authors sorted by how many artworks they have, with the option to limit the number of authors shown.
    """

    def __init__(self, artworks: List[Dict[str, Any]]) -> None:
        """
        Initialize the ArtworksOrganizer with a list of artworks.

        Args:
            artworks (List[Dict[str, Any]]): A list of artworks, where each artwork is a dictionary
            containing keys like 'created_by'.
        """
        self.artworks = artworks
        self.author_count = Counter()

    def compute_author_frequency(self) -> None:
        """
        Compute the frequency of artworks per author (using the author name).

        This method fills the self.author_count attribute with the number of artworks per author_name.
        """
        if not self.author_count:
            for artwork in self.artworks:
                author_name = artwork.get("created_by")
                if author_name is not None:
                    self.author_count[author_name] += 1

    def sort_by_author_representation(self) -> List[Dict[str, Any]]:
        """
        Sort the artworks by the frequency of their authors (by name).

        Authors with more artworks appear first. If authors have the same frequency,
        their artworks retain their relative order (stable sort).

        Returns:
            List[Dict[str, Any]]: The sorted list of artworks.
        """
        # Ensure author_count is computed
        if not self.author_count:
            self.compute_author_frequency()

        sorted_artworks = sorted(
            self.artworks,
            key=lambda art: self.author_count[art["created_by"]],
            reverse=True
        )
        return sorted_artworks

    def write_sorted_artworks_to_file(self, output_file_path: str) -> None:
        """
        Write the sorted artworks to a JSON file.

        Args:
            output_file_path (str): The file path where the sorted artworks should be written.
        """
        sorted_artworks = self.sort_by_author_representation()
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(sorted_artworks, f, indent=4, ensure_ascii=False)

    def print_authors_by_frequency(self, top_n: int = None) -> None:
        """
        Print the authors sorted by their number of artworks.
        
        If top_n is provided, only print that many authors. Otherwise, print all.
        
        Args:
            top_n (int, optional): The number of top authors to print. If None, print all authors.
        """
        # Ensure author_count is computed
        if not self.author_count:
            self.compute_author_frequency()

        # Convert the Counter to a list of (author, count) sorted by count descending
        authors_sorted = self.author_count.most_common()  # already sorted by count descending

        # If top_n is given, slice the list
        if top_n is not None:
            authors_sorted = authors_sorted[:top_n]

        # Print the authors and their counts
        counter = 0
        for author, _ in authors_sorted:
            if counter == 0: # skip the first author bc its name is "Designed By"
                counter += 1
            else:
                print(f"{author}")
    
    def print_artworks_by_author_frequency(self, top_n: int = None) -> None:
        """
        Print artworks sorted by their author's frequency. Each line shows the artwork_id and artwork_name.
        
        If top_n is provided, only print that many artworks. Otherwise, print all.
        
        Args:
            top_n (int, optional): The number of top artworks to print. If None, print all artworks.
        """
        sorted_artworks = self.sort_by_author_representation()
        if top_n is not None:
            sorted_artworks = sorted_artworks[:top_n]

        for art in sorted_artworks:
            art_id = art.get("artwork_id")
            art_name = art.get("artwork_name")
            print(f"ID: {art_id}, Name: {art_name}")

if __name__ == "__main__":
    # Example artworks JSON data (shortened for illustration)
    with open("data/filtered_artworks.json", "r", encoding="utf-8") as file:
        artworks_data = json.load(file)

    organizer = ArtworksOrganizer(artworks_data)
    #organizer.write_sorted_artworks_to_file("data/sorted_artworks.json")
    #print("Sorted artworks have been written to sorted_artworks.json")

    organizer.print_authors_by_frequency(top_n=100)
    organizer.print_artworks_by_author_frequency(top_n=60)