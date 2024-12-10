from cbr import CBR
from cf import CF

class Recommender:
	"""
	Main class for the recommender system that combines the collaborative filtering (CF) and case-based reasoning (CBR) systems.
	"""
	def __init__(self, db_path='../data/database.db'):
		self.db_path = db_path
		self.cbr: CBR = CBR(db_path)
		self.cf: CF = CF(db_path)
		pass
