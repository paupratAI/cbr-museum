import sqlite3
import numpy as np
from feedback import generate_and_parse_museum_feedback
import random
from ontology.periods import periods_dict
from authors import authors
from ontology.art import artworks

class DBPartitionsHandler:
	def __init__(self, 
			db_path: str = "../data/database.db", 
			train_split: float = 0.975, # 50 cases for testing
			main_table: str = "cases",
			ratings_range: list = [0, 5],
			seed: int = 42,
			overwrite: bool = False
			):
		assert 0 <= train_split <= 1, "Train split should be between 0 and 1"

		self.train_split = train_split
		self.db_path = db_path
		self.main_table = main_table
		self.ratings_range = ratings_range

		self.conn = sqlite3.connect(db_path)
		self.cursor = self.conn.cursor()

		if overwrite:
			self.create_data_partitions(seed)

	def create_data_partitions(self, seed: int):
		"""
		Creates of the main table in the database.

		Args:
			seed (int): The seed to use for the random split.
		"""
		# Check if the train and test tables are already created with the same split proportion
		# Count the length of the train and test tables to check the proportion if they exist
		# Set the seed
		np.random.seed(seed)

		# Delete the train and test tables if they exist
		self.cursor.execute(f"DROP TABLE IF EXISTS train_{self.main_table}")
		self.cursor.execute(f"DROP TABLE IF EXISTS test_{self.main_table}")

		# Get the length of the main table
		self.cursor.execute(f"SELECT COUNT(*) FROM {self.main_table}")
		total_rows = self.cursor.fetchone()[0]

		# Split the data into train and test
		train_rows = int(self.train_split * total_rows)

		# Get the row ids (from 1 to total_rows)
		row_ids = np.arange(1, total_rows + 1)

		# Shuffle the row ids
		row_ids = np.random.permutation(row_ids)

		# Get the train and test row ids
		train_row_ids = np.random.choice(row_ids, train_rows, replace=False)
		test_row_ids = np.array([row_id for row_id in row_ids if row_id not in train_row_ids])

		# Create the train and test tables
		self.cursor.execute(f"CREATE TABLE train_{self.main_table} AS SELECT * FROM {self.main_table} WHERE rowid IN ({','.join(map(str, train_row_ids))})")
		self.cursor.execute(f"CREATE TABLE test_{self.main_table} AS SELECT * FROM {self.main_table} WHERE rowid IN ({','.join(map(str, test_row_ids))})")

		self.conn.commit()
	
	def get_train_table_name(self):
		"""
		Returns the name of the train table in the given database.
		"""
		return f"train_{self.main_table}"
	
	def get_test_table_name(self):
		"""
		Returns the name of the test table in the fiven database.
		"""
		return f"test_{self.main_table}"

	def get_test_ratings(self):
		"""
		Returns the ratings of the test set.
		"""

		self.cursor.execute(f"SELECT rating FROM test_{self.main_table}")
		test_ratings = self.cursor.fetchall()
		test_ratings = [float(rating[0]) for rating in test_ratings]
		return test_ratings
	
	def get_test_rows(self):
		"""
		Returns the rows of the test set.
		"""

		self.cursor.execute(f"SELECT * FROM test_{self.main_table}")
		return self.cursor.fetchall()
	
	def get_predictions_ratings(self, predictions: list[list[int]]):
		"""
		Returns the ratings of the test set using the same expert LLM that rated the test set.
		"""
		# Get the test rows
		query = f"SELECT group_size, group_type, group_description, art_knowledge, preferred_periods_ids, preferred_author_name, preferred_themes, time_coefficient FROM test_{self.main_table}"
		self.cursor.execute(query)
		test_rows = self.cursor.fetchall()

		predictions_ratings = []

		for i, (test_row, prediction) in enumerate(zip(test_rows, predictions)):
			print(f"Evaluating prediction {i+1}/{len(test_rows)}", end='\r')

			textual_feedback = random.choice(["full", "short", "None"])

			prediction = [artworks[artwork_id] for artwork_id in prediction]

			group_size, group_type, group_description, art_knowledge, preferred_periods, preferred_author, preferred_themes, time_coefficient = test_row

			preferred_periods = preferred_periods.replace("[", "").replace("]", "").replace("'", "").replace(" ", "").split(",") if preferred_periods else []
			preferred_periods = [int(period.strip()) for period in preferred_periods]
			preferred_periods = [periods_dict[period_id] for period_id in preferred_periods]

			preferred_author = preferred_author.strip()
			preferred_author = authors[preferred_author]

			# Generate the feedback
			feedback = generate_and_parse_museum_feedback(
				group_size=group_size,
				group_type=group_type,
				group_description=group_description,
				reduced_mobility='Unknown',
				art_knowledge_level=art_knowledge,
				preferred_periods=preferred_periods,
				preferred_authors=preferred_author,
				preferred_themes=preferred_themes,
				time_coefficient=time_coefficient,
				proposed_paintings=prediction,
				route_score='Unknown',
				perfect_route_score=10,
				textual_feedback=textual_feedback
			)

			predictions_ratings.append(feedback['evaluation'])

		return predictions_ratings

	def evaluate_predictions(self, 
			predictions: list[list[int]], 
			improvement_error_funcs: list[str] = ['exp-exp', 'exp-lin', 'exp-log', 'lin-exp', 'lin-lin', 'lin-log', 'log-exp', 'log-lin', 'log-log']
			) -> dict[str, tuple[float, list]]:
		"""
		Evaluates the predictions in the test set using the improvement and error functions provided.

		Args:
			predictions (list[list[int]]): A list of lists containing the predictions for each test row.
			improvement_error_funcs (list[str]): A list of strings containing the improvement and error functions to use. 
				Each string should be in the format 'improvement_func-error_func', where improvement_func and error_func are the functions to use (lin, log, exp).

		Returns:
			dict[tuple, tuple[float, list[float]]]: A dictionary containing the improvement metrics for each function pair. 
				The keys are the names of the function pairs, and the values are tuples containing the average metric and the individual metrics for each test row.
				Higher values are better.
		"""
		# Get the ratings of the test set
		predictions_ratings = self.get_predictions_ratings(predictions)
		test_ratings = self.get_test_ratings()

		scores = {}
		for func_pair in improvement_error_funcs:
			improvement_func, error_func = func_pair.split('-')
			assert improvement_func in ['lin', 'log', 'exp'], "Improvement function should be one of 'lin', 'log', 'exp'"
			assert error_func in ['lin', 'log', 'exp'], "Error function should be one of 'lin', 'log', 'exp'"

			# Calculate the metric
			average_metric, individual_metrics = self.calculate_metric(y_test=test_ratings, y_pred=predictions_ratings, improvement_func=improvement_func, error_func=error_func)

			scores[func_pair] = (average_metric, individual_metrics)

		scores['test_ratings'] = test_ratings
		scores['predictions_ratings'] = predictions_ratings

		return scores

	@staticmethod
	def calculate_metric(y_test, y_pred, improvement_func='log', error_func='lin') -> tuple[float, list[float]]:
		"""
		Calculates a flexible metric based on improvements and errors, with customizable functions.
		
		Args:
			y_test (array-like): Actual values.
			y_pred (array-like): Predicted values.
			improvement_func (str): Function for improvements ('log', 'lin', 'exp').
			error_func (str): Function for errors ('log', 'lin', 'exp').
		
		Returns:
			tuple[float, np.ndarray]: The average metric and the individual metrics.
		"""
		assert len(y_test) == len(y_pred), "The lengths of y_test and y_pred should be the same."

		diffs = [p - t for p, t in zip(y_pred, y_test)]

		from math import log, exp

		if improvement_func == 'lin':
			new_diffs = diffs
		elif improvement_func == 'log':
			new_diffs = []
			for diff in diffs:
				if diff > 0:
					new_diffs.append(log(abs(diff) + 1))
				else:
					new_diffs.append(diff)
		elif improvement_func == 'exp':
			new_diffs = []
			for diff in diffs:
				if diff > 0:
					new_diffs.append(exp(abs(diff)) - 1)
				else:
					new_diffs.append(diff)

		diffs = new_diffs

		if error_func == 'lin':
			new_diffs = diffs
		elif error_func == 'log':
			new_diffs = []
			for diff in diffs:
				if diff < 0:
					new_diffs.append(-log(abs(diff) + 1))
				else:
					new_diffs.append(diff)
		elif error_func == 'exp':
			new_diffs = []
			for diff in diffs:
				if diff < 0:
					new_diffs.append(-exp(abs(diff)) + 1)
				else:
					new_diffs.append(diff)

		diffs = new_diffs

		return sum(diffs) / len(diffs) , diffs

