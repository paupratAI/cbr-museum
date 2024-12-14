from cbr import CBR
from cf import CF
import sqlite3

class Recommender:
	"""
	Main class for the recommender system that combines the collaborative filtering (CF) and case-based reasoning (CBR) systems.
	"""
	def __init__(self, 
			db_path='../data/database.db',
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
		
		# self.cbr: CBR = CBR(db_path)
		self.cf: CF = CF(
			db_path=db_path, 
			default_alpha=cf_alpha, 
			default_gamma=cf_gamma, 
			default_method=cf_method, 
			default_decay_factor=cf_decay_factor, 
			ratings_range=ratings_range
		)
		pass

	def add_rows_to_cf(self):
		"""
		Adds all the rows of the main table to the CF system.
		"""
		# Get the values from the database
		query = f"SELECT group_id, ordered_artworks, ordered_artworks_matches, visited_artworks_count, rating FROM {self.main_table}"
		rows = self.cursor.execute(query).fetchall()

		# Add the rows to the CF system
		for row in rows:
			group_id, ordered_artworks, ordered_artworks_matches, visited_artworks_count, rating = row

			self.cf.store_group_ratings(
				group_id=group_id, 
				ordered_items=ordered_artworks,
				ordered_items_matches=ordered_artworks_matches,
				visited_items_count=visited_artworks_count, 
				global_rating=rating
			)

	def recommend(self, target_group_id: int):
		"""
		Recommends items using the CF and CBR systems.
		"""
		self.cf.recommend_items(target_group_id=target_group_id)

if __name__ == '__main__':
	target_group_id = 1
	r = Recommender()
	r.add_rows_to_cf()
	print(r.recommend(target_group_id))
