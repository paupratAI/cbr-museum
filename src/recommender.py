from cbr import CBR
from cf import CF
import sqlite3
import json

from entities import AbstractProblem, SpecificProblem
from authors import authors
from ontology.themes import theme_instances
from ontology.periods import periods
from db_partitions_handler import DBPartitionsHandler
from clustering import Clustering

import pickle as pkl

class Recommender:
	"""
	Main class for the recommender system that combines the collaborative filtering (CF) and case-based reasoning (CBR) systems.
	"""
	def __init__(self, 
		db_path='data/database.db',
		main_table: str = 'cases',
		cf_alpha: float = 0.5, 
		cf_gamma: float = 1,
		cf_decay_factor: float = 1,
		cf_method: str = 'cosine',
		beta: float = 0.5,
		ratings_range: list = [0, 5],
		clustering: bool = False
		):
		"""
		Initializes the Recommender system.

		Args:
			beta (float): The weight of the CF system in the combination of the hybrid recommendation.
			- beta = 0 means only CBR recommendations are used.
			- beta = 1 means only CF recommendations are used.
			- 0 < beta < 1 means a combination of both recommendations is used.

			cf_alpha (float): The alpha parameter for the CF system.
			cf_gamma (float): The gamma parameter for the CF system.
			cf_decay_factor (float): The decay factor for the CF system.
			cf_method (str): The method to use for the CF system.
			db_path (str): The path to the SQLite database.
			main_table (str): The name of the main table in the database.
			ratings_range (list): The range of ratings to use in the feedback.
			clustering (bool): Whether to calculate the clusters or not.
		"""
		assert 0 <= beta <= 1, "Beta should be between 0 and 1."
		
		if clustering:
			self.clustering()

		self.main_table = main_table
		self.db_path = db_path
		self.beta = beta
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
		
		self.dbph = DBPartitionsHandler(db_path=self.db_path, train_split=0.975, main_table="cases", ratings_range=[0, 5], seed=42, overwrite=False)
	
	def clustering(self):

		# Initialize the clustering system
		clustering_system = Clustering(db_path='./data/database.db', model_path='./models/kmeans_model.joblib')

		try:
			# Fetch data and perform clustering
			raw_data = clustering_system.fetch_data_from_cases()
			X_scaled = clustering_system.encode_and_scale_features()
			clustering_system.perform_clustering(X_scaled, min_k=10, max_k=30, minimum_examples_per_cluster=10)
			clustering_system.save_clusters_to_cases()
			clustering_system.print_cluster_statistics()
			clustering_system.print_centroids_readable()
			clustering_system.save_model()
		except ValueError as ve:
			print(f"Clustering Error: {ve}")
		finally:
			print("Closing connection to the database.")
			clustering_system.close_connection()


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

	def add_rows_to_cf(self, table_name: str):
		"""
		Adds all the rows of the main table to the CF system.
		"""
		# Get the values from the database
		query = f"SELECT group_id, ordered_artworks, ordered_artworks_matches, visited_artworks_count, rating FROM {table_name}"
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
			available_authors=list(authors.values()),
			available_themes=theme_instances,
			available_periods=periods
		)

		return abstract_problem
	
	def store_case(self) -> None:
		pass

	def recommend(self, target_group_id: int, clean_response: list = [], ap: AbstractProblem = None, eval_mode: bool = False) -> dict[str, list]:
		"""
		Recommends items using the CF and CBR systems.

		The combination of the recommendations is done by averaging the positions of the items in the two lists and sorting them by the average position.

		Args:
			target_group_id (int): The group ID of the target group.
			clean_response (list): The list of data from the group.
			ap (AbstractProblem): The abstract problem to use for the CBR system.
			eval_mode (bool): Whether to use the evaluation mode or not. Eval mode does not add the resulting cases to CBR nor CF.

		Returns:
			dict(str, list): A dictionary with the CBR, CF and Hybrid recommendations.
		"""
		# Obtain abstract problem from clean_response
		if not ap:
			ap = self.convert_to_problems(clean_response)

		cf_result, cbr_result = [], []

		# Calculate the routes
		if self.beta > 0:
			cf_result, cf_probs = self.cf.recommend_items(target_group_id=target_group_id) # CF probs must be used to aproximate matches when storing the case in the CF databse
			cf_probs_dict = {item_id: prob for item_id, prob in zip(cf_result, cf_probs)}
		
		if self.beta < 1:
			cbr_result, cbr_probs = self.cbr.recommend_items(ap=ap)
			cbr_probs_dict = {item_id: prob for item_id, prob in zip(cbr_result, cbr_probs)}

		# Combine the recommendations from both systems
		all_items = cf_result if self.beta > 0 else cbr_result
		if 0 < self.beta < 1:
			averaged_probs_dict = {
				item_id: (cf_probs_dict[item_id] * self.beta + cbr_probs_dict[item_id] * (1 - self.beta)) for item_id in all_items
			}

		# Sort the items by the average position
		if self.beta == 0:
			combined_result = cbr_result
		elif self.beta == 1:
			combined_result = cf_result
		else:
			combined_result = list(sorted(averaged_probs_dict.keys(), key=lambda x: averaged_probs_dict[x]))

		recommendations = {
			"cf": cf_result,
			"cbr": cbr_result,
			"hybrid": combined_result
		}

		# if not eval_mode:
		# 	self.store_case()

		return recommendations

	def evaluate(self, reload_cf: bool = False, save: bool = False):
		"""
		Evaluates the Recommender Hybrid predictions in the test set.
		"""
		train_table_name = self.dbph.get_train_table_name()

		# Add the train rows to the CF system
		if reload_cf:
			self.add_rows_to_cf(table_name=train_table_name)

		# Get the predictions from the CF system
		test_rows = self.dbph.get_test_rows()
		predictions = []

		for i, row in enumerate(test_rows):
			group_id = row[1]

			print(f"Generating test prediction {(i+1)}/{len(test_rows)}", end='\r')

			predictions.append(self.recommend(target_group_id=group_id, clean_response=row, eval_mode=True)["hybrid"])

		# Evaluate the predictions
		scores = self.dbph.evaluate_predictions(predictions=predictions)

		print(scores)

		if save:
			return scores
			with open(f"scores/scores_cf_alpha{self.cf.default_alpha}_cfgamma{self.cf.default_gamma}_cfdecay{self.cf.default_decay_factor}_cfmethod{self.cf.default_method}.pkl", "wb") as f:
				pkl.dump(scores, f)

		return scores