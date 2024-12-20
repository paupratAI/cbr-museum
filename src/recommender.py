from cbr import CBR
from cf import CF
import sqlite3
import json
import os
import numpy as np
import time
import matplotlib.pyplot as plt

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
		cbr_alpha: float = 0.6,
		cbr_beta: float = 0.3,
		cbr_gamma: float = 0.1,
		cbr_top_k: int = 3,
		ratings_range: list = [0, 5],
		clustering: bool = True
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
			cbr_alpha (float): The alpha parameter for the CBR system.
			cbr_beta (float): The beta parameter for the CBR system.
			cbr_gamma (float): The gamma parameter for the CBR system.
			cbr_top_k (int): The number of top cases to consider in the CBR system.
			db_path (str): The path to the SQLite database.
			main_table (str): The name of the main table in the database.
			ratings_range (list): The range of ratings to use in the feedback.
			clustering (bool): Whether to calculate the clusters or not.
		"""
		assert 0 <= beta <= 1, "Beta should be between 0 and 1."
		
		if clustering:
			self.clustering_system = self.clustering()

		self.cf_alpha = cf_alpha
		self.cf_gamma = cf_gamma
		self.cf_decay_factor = cf_decay_factor
		self.cf_method = cf_method
		self.cbr_alpha = cbr_alpha
		self.cbr_beta = cbr_beta
		self.cbr_gamma = cbr_gamma
		self.cbr_top_k = cbr_top_k
		self.main_table = main_table
		self.db_path = db_path
		self.beta = beta
		self.conn = sqlite3.connect(db_path, check_same_thread=False)
		self.cursor = self.conn.cursor()

		self.ratings_range = ratings_range

		self.cbr: CBR = CBR(db_path, alpha=cbr_alpha, beta=cbr_beta, gamma=cbr_gamma, top_k=cbr_top_k)
		
		self.cf: CF = CF(
			db_path=db_path, 
			default_alpha=cf_alpha, 
			default_gamma=cf_gamma, 
			default_method=cf_method, 
			default_decay_factor=cf_decay_factor, 
			ratings_range=ratings_range
		)
		
		self.dbph = DBPartitionsHandler(db_path=self.db_path, train_split=0.9875, main_table="cases", ratings_range=[0, 5], seed=42, overwrite=False)
	
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
		return clustering_system


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

	def convert_to_problems(self, clean_response: list = None) -> AbstractProblem:
		"""
		Converts a `clean_response` data list into a SpecificProblem object and then into an AbstractProblem.
		"""
		specific_problem = SpecificProblem(
			group_id=int(clean_response[0]),
			num_people=int(clean_response[1]),
			favorite_author=clean_response[2],
			favorite_period=int(clean_response[3]),
			favorite_theme=clean_response[4],
			guided_visit=bool(int(clean_response[5])),
			minors=bool(int(clean_response[6])),
			num_experts=int(clean_response[7]),
			past_museum_visits=int(clean_response[8]),
			group_description=clean_response[9]
		)

		abstract_problem = AbstractProblem(
			specific_problem=specific_problem,
			available_authors=list(authors.values())[:50],
			available_themes=theme_instances,
			available_periods=periods
		)

		return specific_problem, abstract_problem
	
	def store_case(self, clean_response,  visited_artworks_count, ordered_artworks, ordered_artworks_matches, rating, textual_feedback, cluster, time_limit) -> None:
		print('.......................................................................................................................')
		sp, ap = self.convert_to_problems(clean_response)
		self.cf.store_group_ratings(group_id=ap.group_id, ordered_items=ordered_artworks, ordered_items_matches=ordered_artworks_matches, visited_items_count=visited_artworks_count, global_rating=rating)
		self.cbr.retain(specific_problem=sp, abstract_problem=ap, user_feedback=rating, visited_artworks_count=visited_artworks_count, ordered_artworks=ordered_artworks, ordered_artworks_matches=ordered_artworks_matches, time_limit=time_limit, rating=rating, textual_feedback=textual_feedback, cluster=cluster)

	def recommend(self, target_group_id: int, clean_response: list = [], ap: AbstractProblem = None, eval_mode: bool = False, cluster_id: int = 0) -> dict[str, tuple[list[int], list[float]]]:
		"""
		Recommends items using the CF and CBR systems.

		The combination of the recommendations is done by averaging the positions of the items in the two lists and sorting them by the average position.

		Args:
			target_group_id (int): The group ID of the target group.
			clean_response (list): The list of data from the group.
			ap (AbstractProblem): The abstract problem to use for the CBR system.
			eval_mode (bool): Whether to use the evaluation mode or not. Eval mode does not add the resulting cases to CBR nor CF.

		Returns:
			dict(str, tuple): A dictionary with the CBR, CF and Hybrid recommendations and their probabilities.
		"""
		# Obtain abstract problem from clean_response
		if not ap:
			sp, ap = self.convert_to_problems(clean_response)

		ap.cluster = cluster_id
		cf_result, cbr_result = [], []
		cf_probs, cbr_probs = [], []
		combined_result, combined_probs = [], []

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
			combined_probs = [averaged_probs_dict[item_id] for item_id in combined_result]

		recommendations = {
			"cf": (cf_result, cf_probs),
			"cbr": (cbr_result, cbr_probs),
			"hybrid": (combined_result, combined_probs)
		}

		return recommendations

	def evaluate(self, results_file_name: str, reload_cf: bool = False, save: bool = False, plot_time = False):
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

		self.clustering_system.load_model()

		execution_times = [] 

		start_time = time.time()
		for i, row in enumerate(test_rows):
			iter_start_time = time.time()  

			if (i + 1) % 50 == 0:
				self.clustering_system = self.clustering()			
				self.clustering_system.load_model() 

			print(f"Generating test prediction {(i+1)}/{len(test_rows)}", end='\r')

			_, group_id, _, num_people, num_experts, minors, past_museum_visits, preferred_main_theme, guided_visit, preferred_year, _, _, _, preferred_author_name, _, _, _, _, group_description, _, _, _, _, _, _, _, _, _, _, _, _, _ = row

			clean_response = [group_id, num_people, preferred_author_name, preferred_year, preferred_main_theme, guided_visit, minors, num_experts, past_museum_visits, group_description]

			new_case = {
				'num_people': int(num_people),
				'preferred_author_name': preferred_author_name,
				'preferred_year': int(preferred_year),
				'preferred_main_theme': preferred_main_theme,
				'guided_visit': int(guided_visit),
				'minors': int(minors),
				'num_experts': int(num_experts),
				'past_museum_visits': int(past_museum_visits)
			}

			cluster_id = self.clustering_system.classify_new_case(new_case)

			predictions.append(self.recommend(target_group_id=group_id, clean_response=clean_response, eval_mode=True, cluster_id=cluster_id)["hybrid"][0])

			iter_time = time.time() - iter_start_time
			execution_times.append(iter_time)

		# Evaluate the predictions
		scores = self.dbph.evaluate_predictions(predictions=predictions, improvement_error_funcs=['lin-lin'])
	
		if plot_time:
			final_time = time.time() - start_time
			print("-" * 50)
			print(f"\nTime taken: {final_time} seconds.\n")

			plots_dir = "plots"
			if not os.path.exists(plots_dir):
				os.makedirs(plots_dir)

			plt.figure(figsize=(10, 6))
			plt.plot(range(1, len(execution_times) + 1), execution_times, marker='o', linestyle='-')
			plt.xlabel("Iteration")
			plt.ylabel("Execution Time (seconds)")
			plt.title("Execution Time per Iteration")
			plt.grid(True)

			plot_path = os.path.join(plots_dir, "exec_time_plot_no_gd.png")
			plt.savefig(plot_path)
			plt.close()

		if save:
			# Check if the file exists. If it does, change the name
			parameters_str = f"{self.cf_alpha=}, {self.cf_gamma=}, {self.cf_decay_factor=}, {self.cf_method=}, {self.beta=}, {self.cbr_alpha=}, {self.cbr_beta=}, {self.cbr_gamma=}, {self.cbr_top_k=}"
			results_file_name = os.path.join('scores', results_file_name)

			scores['parameters'] = parameters_str

			if not results_file_name.endswith('.json'):
				results_file_name += '.json'

			if os.path.exists(results_file_name):
				results_file_name = results_file_name.replace('.json', '_new.json')

			# Save the results to a file
			with open(results_file_name, 'w') as f:
				json.dump(scores, f)

		return scores
	
if __name__ == '__main__':
	r = Recommender(cf_decay_factor=1, cf_alpha=0, cf_gamma=1, beta=0)
	r.evaluate(results_file_name='cf-alpha0', save=True, reload_cf=False)
	