from cbr import CBR
from cf import CF
import sqlite3
import json

from entities import AbstractProblem, SpecificProblem
from authors import authors
from ontology.themes import theme_instances
from ontology.periods import periods
from db_partitions_handler import DBPartitionsHandler

class Recommender:
	"""
	Main class for the recommender system that combines the collaborative filtering (CF) and case-based reasoning (CBR) systems.
	"""
	def __init__(self, 
			db_path='data/database.db',
			main_table: str = 'cases',
			cf_alpha: float = 0.5, 
			cf_gamma: float = 1,
			cf_decay_factor: float = 0.9,
			cf_method: str = 'cosine',
			ratings_range: list = [0, 5],
			):

		self.db_path = db_path
		self.main_table = main_table
		self.conn = sqlite3.connect(db_path)
		self.cursor = self.conn.cursor()

		self.ratings_range = ratings_range

		self.cbr: CBR = CBR(db_path)
		
		self.cf: CF = CF(
			db_path=db_path, 
			default_alpha=cf_alpha, 
			default_gamma=cf_gamma, 
			default_method=cf_method, 
			default_decay_factor=cf_decay_factor, 
			ratings_range=ratings_range
		)
		
		self.dbph = DBPartitionsHandler(db_path="data/database.db", train_split=0.8, main_table="cases", ratings_range=[0, 5], seed=42)


	def retrieve_data(self, clean_response):
		"""
		Retrieves data from the database.
		"""
		sp = clean_response
		ap = AbstractProblem(specific_problem=sp, available_authors=self.get_authors(), available_themes=theme_instances, available_periods=periods)
		self.cbr.retrieve_cases(problem=ap)
	
	def get_authors(self):
		"""
		Returns the authors from the CBR system.
		"""
		# Pick the first 50 in the dictionary
		aut = list(authors.values())[:50]
		return aut

	def add_rows_to_cf(self):
		"""
		Adds all the rows of the main table to the CF system.
		"""
		# Get the values from the database
		query = f"SELECT group_id, ordered_artworks, ordered_artworks_matches, visited_artworks_count, rating FROM {self.main_table}"
		self.cursor.execute(query)
		rows = self.cursor.fetchall()

		total_rows = len(rows)
		# Add the rows to the CF system
		for i, row in enumerate(rows):
			print(f"Adding row {i+1}/{total_rows} to the CF system.", end='\r')
			group_id, ordered_artworks, ordered_artworks_matches, visited_artworks_count, rating = row

			# Decode JSON fields to Python lists
			ordered_artworks_list = json.loads(ordered_artworks) if ordered_artworks else []
			ordered_artworks_matches_list = json.loads(ordered_artworks_matches) if ordered_artworks_matches else []

			self.cf.store_group_ratings(
				group_id=group_id, 
				ordered_items=ordered_artworks_list,
				ordered_items_matches=ordered_artworks_matches_list,
				visited_items_count=visited_artworks_count, 
				global_rating=rating
			)

		print("All rows added to the CF system.")

	def convert_to_problems(clean_response: list) -> AbstractProblem:
		"""
			Converts a `clean_response` data list into a SpecificProblem object and then into an AbstractProblem.

			Args:
				clean_response (list): List with the necessary data to build a SpecificProblem.
				authors (list): List of available authors.
				themes (dict): Dictionary of available themes.
				periods (list): List of available periods.

			Returns:
				AbstractProblem: The abstract problem created from clean_response.
		"""
		specific_problem = SpecificProblem(
			group_id=clean_response[0],
			num_people=clean_response[1],
			favorite_author=clean_response[2],
			favorite_period=clean_response[3],
			favorite_theme=clean_response[4],
			guided_visit=clean_response[5],
			minors=clean_response[6],
			num_experts=clean_response[7],
			past_museum_visits=clean_response[8],
			group_description=clean_response[9]
		)

		abstract_problem = AbstractProblem(
			specific_problem=specific_problem,
			available_authors=authors,
			available_themes=theme_instances,
			available_periods=periods
		)

		return abstract_problem

	def recommend(self, target_group_id: int, clean_response: list):
		"""
		Recommends items using the CF and CBR systems.

		The combination of the recommendations is done by averaging the positions of the items in the two lists and sorting them by the average position.
		"""
		# Cridar a la funció que calgui per obtenir abs_prob des de clean_response
		ap = self.convert_to_problems(clean_response)

		# Calculate the routes
		cf_result = self.cf.recommend_items(target_group_id=target_group_id)
		cbr_result = self.cbr.recommend_items(abs_prob=ap)

		# Combine the recommendations from both systems
		average_position = {
			item_id: (cf_result.index(item_id) + cbr_result.index(item_id)) / 2
			for item_id in cf_result
		}

		# Sort the items by the average position
		combined_result = sorted(cf_result, key=lambda x: average_position[x])

		return combined_result
