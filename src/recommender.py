from src.cbr import CBR
from src.cf import CF
import sqlite3
import json

from src.entities import AbstractProblem
from src.authors import authors
from src.ontology.themes import theme_instances
from src.ontology.periods import periods
from src.db_partitions_handler import DBPartitionsHandler

class Recommender:
	"""
	Main class for the recommender system that combines the collaborative filtering (CF) and case-based reasoning (CBR) systems.
	"""
	def __init__(self, 
			db_path='data/database.db',
			main_table: str = 'abstract_problems',
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

		self.cbr = CBR()
		
		# self.cbr: CBR = CBR(db_path)
		self.cf: CF = CF(
			db_path=db_path, 
			default_alpha=cf_alpha, 
			default_gamma=cf_gamma, 
			default_method=cf_method, 
			default_decay_factor=cf_decay_factor, 
			ratings_range=ratings_range
		)
		
		self.dbph = DBPartitionsHandler(db_path="data/database.db", train_split=0.8, main_table="abstract_problems", ratings_range=[0, 5], seed=42)


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

	def recommend(self, target_group_id: int):
		"""
		Recommends items using the CF and CBR systems.
		"""
		return self.cf.recommend_items(target_group_id=target_group_id)

if __name__ == '__main__':
	target_group_id = 1
	r = Recommender()
	r.cf.clear_ratings()
	r.add_rows_to_cf()
	print(r.recommend(target_group_id))
