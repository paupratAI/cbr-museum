import sqlite3
import numpy as np

class DatabaseHandler:
	def __init__(self, 
			db_path: str = "../data/database.db", 
			train_split: float = 0.8, 
			main_table: str = "abstract_problems",
			ratings_range: list = [0, 5],
			seed: int = 42
			):
		assert 0 <= train_split <= 1, "Train split should be between 0 and 1"

		self.train_split = train_split
		self.db_path = db_path
		self.main_table = main_table
		self.ratings_range = ratings_range

		self.conn = sqlite3.connect(db_path)
		self.cursor = self.conn.cursor()

		self.create_data_partitions(seed)

	def create_data_partitions(self, seed: int):
		"""
		Creates of the main table in the database.

		Args:
			seed (int): The seed to use for the random split.
		"""

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
		return self.cursor.fetchall()

	def evaluate_predictions(self, 
			predictions: np.ndarray, 
			improvement_error_funcs: list[str] = ['lin-lin'],
			) -> dict[str, tuple[float, np.ndarray]]:
		"""
		Evaluates the predictions using the improvement and error functions provided.

		Args:
			predictions (np.ndarray): The predictions to evaluate.
			improvement_error_funcs (list[str]): A list of strings containing the improvement and error functions to use. 
				Each string should be in the format 'improvement_func-error_func'w,
				here improvement_func and error_func are the functions to use (lin, log, exp).

		Returns:
			dict[tuple, tuple[float, list[float]]]: A dictionary containing the improvement metrics for each function pair. 
				The keys are the names of the function pairs, and the values are tuples containing the average metric and the individual metrics.
				Higher values are better.
		"""

		scores = {}

		for func_pair in improvement_error_funcs:
			improvement_func, error_func = func_pair.split('-')
			assert improvement_func in ['lin', 'log', 'exp'], "Improvement function should be one of 'lin', 'log', 'exp'"
			assert error_func in ['lin', 'log', 'exp'], "Error function should be one of 'lin', 'log', 'exp'"

			# Get the ratings of the test set
			test_ratings = np.array(self.get_test_ratings())
			
			if isinstance(predictions, list):
				predictions = np.array(predictions)

			# Calculate the metric
			average_metric, individual_metrics = self.calculate_metric(y_test=test_ratings, y_pred=predictions, improvement_func=improvement_func, error_func=error_func)

			scores[func_pair] = (average_metric, individual_metrics)

		return scores

	@staticmethod
	def calculate_metric(y_test, y_pred, improvement_func='log', error_func='lin') -> tuple[float, np.ndarray]:
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
		# Diferencias entre predicciones y valores reales
		diffs = y_pred - y_test

		absolute_errors = np.where(diffs >= 0, 0, -diffs)
		absolute_improvements = np.where(diffs >= 0, diffs, 0)
		
		# Improvement function
		def apply_improvement_func(absolute_improvements):
			if improvement_func == 'log':
				return np.log1p(absolute_improvements)  # log(1 + x)
			elif improvement_func == 'lin':
				return absolute_improvements  # Lineal
			elif improvement_func == 'exp':
				return np.expm1(absolute_improvements)  # exp(x) - 1
			else:
				raise ValueError(f"Improvement function '{improvement_func}' not recognized.")
		
		# Error function
		def apply_error_func(absolute_errors):
			if error_func == 'log':
				return np.log1p(-absolute_errors)  # log(1 - x)
			elif error_func == 'lin':
				return -absolute_errors  # Lineal
			elif error_func == 'exp':
				return np.expm1(-absolute_errors)  # exp(-x) - 1
			else:
				raise ValueError(f"Error function '{error_func}' not recognized.")
		
		# Apply the functions
		improvements = apply_improvement_func(absolute_improvements)
		errors = apply_error_func(absolute_errors)

		# Calculate the metric
		metrics = improvements - errors

		return np.mean(metrics), metrics

