import sqlite3
from entities import AbstractProblem, SpecificProblem, Author, Period, Theme, AbstractSolution
from typing import List, Dict, Tuple
import json
import ast
from dataclasses import asdict

from clustering import Clustering
from ontology.periods import periods
from ontology.themes import theme_instances
from ontology.art import artworks
from authors import authors
from group_description import compare_sentences, load_model

from typing import List, Tuple

class CBR:
	def __init__(self, db_path='./data/database.db', alpha=0.6, beta=0.3, gamma=0.1, top_k=3):
		self.conn = sqlite3.connect(db_path)
		self.conn.row_factory = sqlite3.Row 
		self.ensure_columns()
		self.create_indices()
		self.alpha = alpha
		self.beta = beta
		self.gamma = gamma
		self.top_k = top_k
		#self.model = load_model()

	def create_indices(self):
		"""Create indices for faster query performance."""
		with self.conn:
			self.conn.execute("CREATE INDEX IF NOT EXISTS idx_cluster ON train_cases(cluster);")
			self.conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_count ON train_cases(usage_count);")
			self.conn.execute("CREATE INDEX IF NOT EXISTS idx_utility ON train_cases(utility);")
			self.conn.execute("CREATE INDEX IF NOT EXISTS idx_redundancy ON train_cases(redundancy);")

	def ensure_columns(self):
		"""Ensure necessary columns (utility, usage_count, redundancy) exist in the table."""
		cursor = self.conn.execute("PRAGMA table_info(train_cases)")
		columns = [col[1] for col in cursor.fetchall()]

		if 'usage_count' not in columns:
			self.conn.execute("ALTER TABLE train_cases ADD COLUMN usage_count INTEGER DEFAULT 0")
		if 'redundancy' not in columns:
			self.conn.execute("ALTER TABLE train_cases ADD COLUMN redundancy REAL DEFAULT 0.0")
		if 'utility' not in columns:
			self.conn.execute("ALTER TABLE train_cases ADD COLUMN utility REAL DEFAULT 0.0")
		self.conn.commit()

	def calculate_similarity(
		self, 
		problem_group_size: int = None,
		problem_group_type: str = None,
		problem_art_knowledge: int = None,
		problem_preferred_periods: List[Period] = None,
		problem_preferred_author: Author = None,
		problem_preferred_themes: List[str] = None,
		problem_time_coefficient: float = None,
		stored_group_size: int = None, 
		stored_group_type: str = None, 
		stored_art_knowledge: int = None, 
		stored_preferred_periods_id: List[int] = None,
		stored_author_name: str = None,
		stored_preferred_themes: List[str] = None,
		stored_time_coefficient: float = None,
		problem_group_description: str = None,
		stored_group_description: str = None
	) -> float:
		"""
		Calculates the similarity between the provided parameters of a problem
		and those of a stored case directly, without needing an AbstractProblem object.
		"""
		if problem_group_description:
			weights = {
				"group_size": 0.05,
				"group_type": 0.1,
				"art_knowledge": 0.2,
				"preferred_periods": 0.2,
				"preferred_author": 0.2,
				"preferred_themes": 0.2,
				"time_coefficient": 0.05
			}
		else:
			weights = {
				"group_size": 0.05,
				"group_type": 0.05,
				"art_knowledge": 0.1,
				"preferred_periods": 0.2,
				"preferred_author": 0.2,
				"preferred_themes": 0.2,
				"time_coefficient": 0.05,
				"group_description": 0.15
			}

		similarity = 0.0

		# Group size
		diff_group_size = abs(problem_group_size - stored_group_size)
		if diff_group_size == 0:
			similarity += weights["group_size"]
		elif diff_group_size == 1:
			similarity += weights["group_size"] * 0.5
		elif diff_group_size == 2:
			similarity += weights["group_size"] * 0.1

		# Group type
		if problem_group_type == stored_group_type:
			similarity += weights["group_type"]

		# Art knowledge
		diff_art_knowledge = abs(problem_art_knowledge - stored_art_knowledge)
		if diff_art_knowledge == 0:
			similarity += weights["art_knowledge"]
		elif diff_art_knowledge == 1:
			similarity += weights["art_knowledge"] * 0.5
		elif diff_art_knowledge == 2:
			similarity += weights["art_knowledge"] * 0.1

		# Preferred periods
		matched_periods = 0
		for period_id in stored_preferred_periods_id:
			for p in problem_preferred_periods:
				if period_id == p.period_id:
					matched_periods += 1
		if matched_periods > 0:
			similarity += weights["preferred_periods"] * (1 - abs(len(stored_preferred_periods_id) - matched_periods))
	
		# Preferred author
		if problem_preferred_author and stored_author_name:
			problem_author_name = problem_preferred_author.author_name
			if problem_author_name == stored_author_name:
				similarity += weights["preferred_author"]
			else:
				# Get the Author instances from the 'authors' dictionary
				stored_author = authors.get(stored_author_name)
				problem_author = authors.get(problem_author_name)

				if stored_author and problem_author:
					# Get the IDs of the main periods
					stored_period_ids = {period.period_id for period in stored_author.main_periods}
					problem_period_ids = {period.period_id for period in problem_author.main_periods}

					# Calculate the intersection of periods
					common_periods = stored_period_ids.intersection(problem_period_ids)
					total_periods = len(problem_period_ids)

					if total_periods > 0:
						period_overlap_ratio = len(common_periods) / total_periods
						similarity += weights["preferred_author"] * 0.5 * period_overlap_ratio

					# Consider similar authors
					similar_authors = stored_author.similar_authors
					if problem_author_name in similar_authors:
						similarity += weights["preferred_author"] * 0.8  

		# Preferred themes
		if problem_preferred_themes and stored_preferred_themes:
			common_themes = set(problem_preferred_themes).intersection(stored_preferred_themes)
			if common_themes:
				similarity += weights["preferred_themes"]
		
		# Time coefficient
		diff_time_coefficient = abs(problem_time_coefficient - stored_time_coefficient)
		if diff_time_coefficient == 0:
			similarity += weights["time_coefficient"]
		elif diff_time_coefficient == 0.25:
			similarity += weights["time_coefficient"] * 0.5
		elif diff_time_coefficient == 0.5:
			similarity += weights["time_coefficient"] * 0.1

		# Group description
		if problem_group_description and stored_group_description:
			sims = compare_sentences(problem_group_description, stored_group_description, self.model)
			description_similarity = sims[0]
			similarity += weights["group_description"] * description_similarity

		return round(similarity, 2)

	def increment_usage_count(self, case_id):
		"""Increments usage_count each time a case is retrieved."""
		cursor = self.conn.execute("SELECT usage_count FROM train_cases WHERE case_id = ?", (case_id,))
		result = cursor.fetchone()
		if result is not None and result[0] is not None:
			usage_count = result[0]
		else:
			usage_count = 0

		usage_count += 1
		self.conn.execute("UPDATE train_cases SET usage_count = ? WHERE case_id = ?", (usage_count, case_id))
		self.conn.commit()

	def get_feedback_list(self, ordered_artworks_matches_str: str, rating: float) -> List[float]:
		"""
		Given the ordered_artworks_matches (a string representation of matches) and a single rating value,
		produce a feedback list where each element corresponds to one artwork.
		
		The logic:
		- Parse ordered_artworks_matches to get a list of numeric match values.
		- Find the maximum match value.
		- For each match value, the feedback is scaled based on (match / max_match) * rating,
		but we also enforce a minimum threshold so that feedback values remain closer to the original rating.
		
		If ordered_artworks_matches_str is empty or rating is 0, returns an empty list.
		"""

		if not ordered_artworks_matches_str or rating is None or rating == 0:
			return []

		try:
			matches = list(map(float, ordered_artworks_matches_str.strip('[]').split(',')))
		except ValueError:
			# If parsing fails or empty string
			return []

		if not matches:
			return []

		max_match = max(matches)
		if max_match == 0:
			# Avoid division by zero
			return [rating for _ in matches]

		# Define a minimum fraction of the rating that no feedback should fall below (70% of the rating)
		min_fraction = 0.7
		min_feedback = rating * min_fraction

		feedback_list = []
		for m in matches:
			scaled_value = (m / max_match) * rating
			# Enforce the minimum feedback threshold
			if scaled_value < min_feedback:
				scaled_value = min_feedback
			feedback_list.append(scaled_value)

		return feedback_list
	
	def calculate_redundancy(self):
		"""
		Calculate redundancy for each case.
		Redundancy is defined as the fraction of other cases that are very similar (>0.9) to this one.
		"""
		cursor = self.conn.execute("SELECT * FROM train_cases")
		all_cases = cursor.fetchall()

		cases = []
		for row in all_cases:
			stored_author = row['preferred_author_name']
			problem_author = authors.get(row['preferred_author_name'])

			stored_periods_id = json.loads(row['preferred_periods_ids'])
			problem_period = [period for period in periods if period.period_id in stored_periods_id]
			themes = ast.literal_eval(row['preferred_themes']) 

			case_params = {
				"group_size": row['group_size'],
				"group_type": row['group_type'],
				"art_knowledge": row['art_knowledge'],
				"preferred_periods": stored_periods_id,
				"preferred_author": stored_author,
				"preferred_themes": themes,
				"time_coefficient": row['time_coefficient'],
			}
			cases.append((row['case_id'], case_params))

		total_cases = len(cases)
		for i, (case_id, case_params) in enumerate(cases):
			if total_cases <= 1:
				redundancy = 0
			else:
				total_similarity = 0
				for j, (_, other_params) in enumerate(cases):
					if i == j:
						continue
					sim = self.calculate_similarity(
						problem_group_size=case_params["group_size"],
						problem_group_type=case_params["group_type"],
						problem_art_knowledge=case_params["art_knowledge"],
						problem_preferred_periods=problem_period,
						problem_preferred_author=problem_author,
						problem_preferred_themes=case_params["preferred_themes"],
						problem_time_coefficient=case_params["time_coefficient"],
						stored_group_size=other_params["group_size"],
						stored_group_type=other_params["group_type"],
						stored_art_knowledge=other_params["art_knowledge"],
						stored_preferred_periods_id=[other_params["preferred_periods"]],
						stored_author_name=other_params["preferred_author"],
						stored_preferred_themes=other_params["preferred_themes"],
						stored_time_coefficient=other_params["time_coefficient"]
					)

					total_similarity += sim
				redundancy = total_similarity / (total_cases - 1)
				redundancy = round(redundancy, 2)

			self.conn.execute("UPDATE train_cases SET redundancy = ? WHERE case_id = ?", (redundancy, case_id))
		self.conn.commit()

	def calculate_utility(self):
		"""
		Recalculate utility considering the rating, usage_count, and redundancy.
		
		Steps:
		- Compute a feedback list from ordered_artworks_matches and rating using get_feedback_list().
		- normalized_feedback = average(feedback_list)/5.0 (if rating is given on scale 1-5)
		- normalized_usage = usage_count / max_usage_count
		- non_redundancy_factor = (1 - redundancy)
		- utility = 0.5 * normalized_feedback + 0.3 * normalized_usage + 0.2 * non_redundancy_factor
		"""
		self.ensure_columns()
		self.calculate_redundancy()

		cursor = self.conn.execute("SELECT MAX(usage_count) FROM train_cases")
		max_usage = cursor.fetchone()[0]
		if max_usage is None or max_usage == 0:
			max_usage = 1

		# Retrieve required data for all cases
		cursor = self.conn.execute("SELECT case_id, ordered_artworks_matches, rating, usage_count, redundancy FROM train_cases")
		rows = cursor.fetchall()

		for case_id, ordered_artworks_matches_str, rating, usage_count, redundancy in rows:
			feedback_list = self.get_feedback_list(ordered_artworks_matches_str, rating)
			if feedback_list:
				avg_feedback = sum(feedback_list) / len(feedback_list)
			else:
				avg_feedback = 0.0

			normalized_feedback = avg_feedback / 5.0
			normalized_usage = usage_count / max_usage
			non_redundancy_factor = 1 - redundancy
			if non_redundancy_factor < 0:
				non_redundancy_factor = 0

			if max_usage == 0:
				# Exclude usage_count from utility calculation
				utility = (0.7 * normalized_feedback) + (0.3 * non_redundancy_factor)
			else:
				# Include normalized_usage when max_usage is greater than 0
				normalized_usage = usage_count / max_usage
				utility = (0.5 * normalized_feedback) + (0.3 * normalized_usage) + (0.2 * non_redundancy_factor)
        
			utility = round(utility, 2)
			self.conn.execute("UPDATE train_cases SET utility = ? WHERE case_id = ?", (utility, case_id))

		self.conn.commit()

	def retrieve(self, problem: AbstractProblem, top_k=50) -> List:
		"""
		Retrieves the most similar cases to the given problem and updates their usage_count.
		"""
		query = """
			SELECT * 
			FROM train_cases 
			WHERE cluster = ? 
		"""
		params = (problem.cluster,)
		rows = self.conn.execute(query, params).fetchall()
		cases_with_similarity = []
		for row in rows:
			stored_periods_id = json.loads(row['preferred_periods_ids'])

			stored_author_name = row['preferred_author_name']

			preferred_themes = ast.literal_eval(row['preferred_themes']) 

			similarity = self.calculate_similarity(
				problem_group_size=problem.group_size,
				problem_group_type=problem.group_type,
				problem_art_knowledge=problem.art_knowledge,
				problem_preferred_periods=problem.preferred_periods,
				problem_preferred_author=problem.preferred_author,
				problem_preferred_themes=problem.preferred_themes,
				problem_time_coefficient=problem.time_coefficient,
				stored_group_size=row['group_size'],
				stored_group_type=row['group_type'],
				stored_art_knowledge=row['art_knowledge'],
				stored_preferred_periods_id=stored_periods_id,
				stored_author_name=stored_author_name,
				stored_preferred_themes=preferred_themes,
				stored_time_coefficient=row['time_coefficient']
			)

			feedback = row['rating']
			distance = similarity * feedback

			cases_with_similarity.append((row, distance))

		# Sort by distance and return top_k
		ranked_cases = sorted(cases_with_similarity, key=lambda x: x[1], reverse=True)
		selected_cases = ranked_cases[:top_k]

		# Actualizar el contador de uso
		for case, dist in selected_cases:
			self.increment_usage_count(case['case_id']) 

		return selected_cases

	def reuse(self, base_problem: AbstractProblem) -> Tuple[List[int], List[float]]:
			"""
			Adapts a solution for the base problem by combining and reordering artworks
			from the top k most similar cases to create a personalized route of desired_artwork_count artworks.
			
			:param base_problem: The AbstractProblem instance representing the new problem.
			:param top_k: Number of top similar cases to consider.
			:param alpha: Weight for normalized frequency.
			:param beta: Weight for normalized match_type.
			:param gamma: Weight for normalized inverse average position.
			:param desired_artwork_count: Total number of artworks desired in the final route.
			:return: A tuple containing:
					- A list of adapted artwork IDs ordered according to the combined scores.
					- A corresponding list of their total scores.
			"""
			top_k = self.top_k
			alpha = self.alpha
			beta = self.beta
			gamma = self.gamma
			desired_artwork_count = 50

			# Step 1: Retrieve the top k most similar cases
			retrieved_cases = self.retrieve(base_problem, top_k=top_k)

			# Step 2: Initialize dictionaries to store frequencies and positions
			artwork_frequency = {}
			artwork_positions = {}

			for case_tuple in retrieved_cases:
				case, similarity = case_tuple
				case_dict = row_to_dict(case)
				
				# Extract 'ordered_artworks' and 'visited_artworks_count' from the case
				ordered_artworks_str = case_dict.get('ordered_artworks', '[]')
				visited_artworks_count = case_dict.get('visited_artworks_count', 0)
				
				# Convert the JSON string of artworks to a list of integers
				try:
					ordered_artworks = json.loads(ordered_artworks_str)
				except json.JSONDecodeError:
					ordered_artworks = []
				
				# Get the artworks actually visited
				visited_artworks = ordered_artworks[:visited_artworks_count]
				
				# Update frequency and position data
				for position, artwork_id in enumerate(visited_artworks):
					# Update frequency count
					artwork_frequency[artwork_id] = artwork_frequency.get(artwork_id, 0) + 1
					
					# Update positions list
					if artwork_id not in artwork_positions:
						artwork_positions[artwork_id] = []
					artwork_positions[artwork_id].append(position + 1)  # Positions start at 1

			# Step 3: Calculate average position for each artwork
			artwork_avg_positions = {
				artwork_id: sum(positions) / len(positions)
				for artwork_id, positions in artwork_positions.items()
			}

			# Step 4: Prepare comprehensive artwork list
			all_artwork_ids = list(artworks.keys())
			
			# Initialize frequency and average position for all artworks
			comprehensive_artwork_frequency = {aid: 0 for aid in all_artwork_ids}
			comprehensive_artwork_avg_positions = {aid: 0.0 for aid in all_artwork_ids}

			# Update with actual frequencies and average positions from retrieved cases
			for aid in artwork_frequency:
				comprehensive_artwork_frequency[aid] = artwork_frequency[aid]
			for aid in artwork_avg_positions:
				comprehensive_artwork_avg_positions[aid] = artwork_avg_positions[aid]

			# Step 5: Compute match scores for all artworks
			# Prepare Artwork instances
			all_artworks_instances = [artworks[aid] for aid in all_artwork_ids if aid in artworks]
			
			# Create an AbstractSolution instance
			abs_sol = AbstractSolution(related_to_AbstractProblem=base_problem)
			
			# Compute matches for all artworks
			abs_sol.compute_matches(artworks=all_artworks_instances)
			
			# Extract match_type scores
			match_type_dict = {match.artwork.artwork_id: match.match_type for match in abs_sol.matches if match.artwork.artwork_id in artworks}

			# Step 6: Normalize frequencies, match scores, and inverse average positions

			# Normalize frequency
			freq_values = list(comprehensive_artwork_frequency.values())
			max_freq = max(freq_values) if freq_values else 1
			min_freq = min(freq_values) if freq_values else 0
			freq_range = max_freq - min_freq if max_freq != min_freq else 1
			normalized_frequency = {aid: (count - min_freq) / freq_range for aid, count in comprehensive_artwork_frequency.items()}

			# Normalize match_type scores
			match_scores = list(match_type_dict.values())
			max_match = max(match_scores) if match_scores else 1
			min_match = min(match_scores) if match_scores else 0
			match_range = max_match - min_match if max_match != min_match else 1
			normalized_match = {aid: (score - min_match) / match_range for aid, score in match_type_dict.items()}

			# Normalize inverse average position
			# For artworks not in any retrieved case, average position is 0, so inverse is 0
			normalized_inv_avg_pos = {}
			# First, compute inverse average position where applicable
			for aid in all_artwork_ids:
				avg_pos = comprehensive_artwork_avg_positions.get(aid, 0.0)
				if avg_pos > 0:
					inv_avg = 1.0 / avg_pos
				else:
					inv_avg = 0.0
				normalized_inv_avg_pos[aid] = inv_avg

			# Now, normalize the inverse average positions
			inv_avg_values = list(normalized_inv_avg_pos.values())
			max_inv_avg = max(inv_avg_values) if inv_avg_values else 1
			min_inv_avg = min(inv_avg_values) if inv_avg_values else 0
			inv_avg_range = max_inv_avg - min_inv_avg if max_inv_avg != min_inv_avg else 1
			normalized_inv_avg_pos = {aid: (inv_pos - min_inv_avg) / inv_avg_range for aid, inv_pos in normalized_inv_avg_pos.items()}

			# Step 7: Calculate total scores and order artworks
			total_scores = {}
			for aid in all_artwork_ids:
				freq_norm = normalized_frequency.get(aid, 0)
				match_norm = normalized_match.get(aid, 0)
				inv_pos_norm = normalized_inv_avg_pos.get(aid, 0)
				total_score = alpha * freq_norm + beta * match_norm + gamma * inv_pos_norm
				total_scores[aid] = total_score

			# Sort artworks by total_score descending
			sorted_artworks = sorted(total_scores.items(), key=lambda x: x[1], reverse=True)
			ordered_artwork_ids = [aid for aid, score in sorted_artworks]
			ordered_artworks_scores = [score for aid, score in sorted_artworks]

			# Step 8: Truncate to desired_artwork_count
			final_ordered_artwork_ids = ordered_artwork_ids[:desired_artwork_count]
			final_ordered_artworks_scores = ordered_artworks_scores[:desired_artwork_count]

			return final_ordered_artwork_ids, final_ordered_artworks_scores
	
	def revise(self, artworks: List[int], artwork_to_remove_name: str) -> List[int]:
		"""
		Revises the solution by moving an artwork to the end of the list if it is present.

		:param artworks: The list of artworks to revise (list of artwork IDs).
		:param artwork_to_remove_name: The name of the artwork to move to the end of the list.
		:return: A list of adapted artworks ordered according to the ontology.
		"""
		# Obtain the ID of the artwork to remove
		artwork_to_remove_id = authors.get(artwork_to_remove_name).author_id

		# If the ID is in the list, move it to the end
		if artwork_to_remove_id in artworks:
			artworks.remove(artwork_to_remove_id)
			artworks.append(artwork_to_remove_id)
		
		return artworks

	def retain(self, specific_problem: SpecificProblem, abstract_problem: AbstractProblem, user_feedback: int, visited_artworks_count: int,  ordered_artworks: List[int], ordered_artworks_matches: List[int], time_limit: int,  rating: int, textual_feedback: str, cluster: int):
		"""
		Stores a SpecificProblem and its corresponding AbstractProblem in the database.

		:param specific_problem: SpecificProblem instance containing user-defined details.
		:param user_feedback: User feedback on the recommended route (1-5).
		:param visited_artworks_count: Number of artworks visited in the recommended route.
		:param clustering: An instance of the Clustering class used for assigning clusters.
		"""
		cursor = self.conn.cursor()

		# Prepare JSON-serialized fields for AbstractProblem
		preferred_periods_json = json.dumps(
			[asdict(p) for p in abstract_problem.preferred_periods],
			ensure_ascii=False
		)
		preferred_author_json = json.dumps(
			asdict(abstract_problem.preferred_author),
			ensure_ascii=False
		) if abstract_problem.preferred_author else None
		preferred_themes_json = json.dumps(abstract_problem.preferred_themes, ensure_ascii=False)

		# Insert AbstractProblem into the cases table
		cursor.execute("""
			INSERT INTO train_cases
			(group_id, group_size, num_people, num_experts, minors, past_museum_visits, preferred_main_theme, guided_visit, preferred_year, group_type, art_knowledge, preferred_periods_ids, preferred_author_name, preferred_themes, reduced_mobility, time_coefficient, time_limit, group_description, ordered_artworks, ordered_artworks_matches, visited_artworks_count, rating, textual_feedback, only_elevator, time_coefficient_correction, artwork_to_remove, guided_visit_feedback, usage_count, redundancy, utility, cluster)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		""", (
			abstract_problem.group_id,
			abstract_problem.group_size,
			specific_problem.num_people,
			specific_problem.num_experts,
			specific_problem.minors,
			specific_problem.past_museum_visits,
			specific_problem.favorite_theme,
			specific_problem.guided_visit,
			specific_problem.favorite_period,
			abstract_problem.group_type,
			abstract_problem.art_knowledge,
			preferred_periods_json,
			preferred_author_json,
			preferred_themes_json,
			abstract_problem.time_coefficient,
			time_limit,
			specific_problem.group_description, 
			json.dumps(ordered_artworks, ensure_ascii=False), 
			json.dumps(ordered_artworks_matches, ensure_ascii=False),
			visited_artworks_count,
			rating,
			user_feedback,
			textual_feedback,
			0,
			"Equal",
			"None",
			0,
			0,
			0,
			0,
			cluster
		))
		self.conn.commit()
	
	def forget_cases(self, threshold=0.2):
		"""Removes cases with low utility from the database."""
		with self.conn:
			self.conn.execute("DELETE FROM train_cases WHERE utility <= ?", (threshold,))

	def recommend_items(self, ap: AbstractProblem, top_k: int = 3) -> Tuple[List[int], List[float]]:
		"""
		Recommends items based on the utility values of the stored cases.

		Args:
			ap (AbstractProblem): The abstract problem representing the current user query.
			top_k (int): The number of top recommendations to return.

		Returns:
			Tuple[List[int], List[float]]: A tuple containing the recommended item IDs and their corresponding vales (criterion of order).
		"""
		recommended_artworks, recommended_probs = self.reuse(ap)
		if not recommended_artworks:
			return [], []
		return recommended_artworks, recommended_probs

	
def row_to_dict(row):
	return {k: row[k] for k in row.keys()}

"""if __name__ == '__main__':
	conn = sqlite3.connect('./data/database.db')
	cursor = conn.cursor()
	
	cursor.execute("PRAGMA table_info(train_cases)")
	columns = [column[1] for column in cursor.fetchall()]
	
	if 'cluster' not in columns:
		cursor.execute("ALTER TABLE train_cases ADD COLUMN cluster INTEGER DEFAULT 1")
		cursor.execute("UPDATE train_cases SET cluster = 1")
	
	conn.commit()
	conn.close()
	
	cbr = CBR()
	sp = SpecificProblem(group_id=1, num_people=2, favorite_author='Pablo Picasso', favorite_period=1900, favorite_theme='historical', guided_visit=True, minors=False, num_experts=1, past_museum_visits=3, group_description='A group of friends visiting the museum.')
	ap = AbstractProblem(sp, periods, list(authors.values()), theme_instances)
	ap.cluster = 1
	
	cases = cbr.retrieve(ap)
	for case, similarity in cases:
		case_dict = row_to_dict(case)
		print(f"Case: {case_dict['case_id']}, Similarity: {similarity}")
	print(ap.preferred_themes)
	
	route = cbr.reuse(ap, top_k=3)
	print(route), print(len(route))
	"""