from cbr import CBR
from cf import CF

class Recommender:
	"""
	Main class for the recommender system that combines the collaborative filtering (CF) and case-based reasoning (CBR) systems.
	"""
	def __init__(self, 
			db_path='../data/database.db', 
			cf_alpha: float = 0.5, 
			cf_gamma: float = 0.25,
			cf_decay_factor: float = 0.9,
			cf_method: str = 'cosine',
			ratings_range: list = [0, 5],
			):

		self.db_path = db_path
		self.cbr: CBR = CBR(db_path)
		self.cf: CF = CF(
			db_path=db_path, 
			default_alpha=cf_alpha, 
			default_gamma=cf_gamma, 
			default_method=cf_method, 
			default_decay_factor=cf_decay_factor, 
			ratings_range=ratings_range
		)
		self.ratings_range = ratings_range
		pass
