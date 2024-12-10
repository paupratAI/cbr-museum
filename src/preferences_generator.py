# CLIPS QUESTIONS:

# How many people will join the visit (1-50)

# Are there children under 12? (yes/no):

# Would you like a guided visit? (yes/no): 

# How many experts are in the group? (Cannot exceed num_people_group):  (0 to num_people_group):

# How many museums have you visited before? (0 to 50):

# Enter the year of your favorite art period (or type -1 for any period) (1000 to 1900):

# Which of these themes do you prefer?
# 0. Any theme
# 1. Emotional
# 2. Historical
# 3. Religious
# 4. Natural
# 5. Mystical
# Enter the number of the theme? (0 to 5): 

# Top authors:
# 1. Fra Bartolommeo
# 2. Bartolomeo Manfredi
# 3. Iran, probably
# 4. Suzuki Harunobu
# 5. Edvard Munch
# Choose your favourite author between these (0 if you don't have any preferences) (0 to 5):

# How many days would you like to visit? (1 to 7):

# How many daily hours will you dedicate to the visit? (1 to 12):

# Is there someone with reduced mobility? (yes/no):

# ----------------------------

import random
from scipy.special import softmax
from scipy.stats import expon
from entities import SpecificProblem
import numpy as np
from scipy.stats import truncnorm

def generate_exponential_integer(low=1, high=50, scale=10):
	value = None
	while value is None:
		new_value = expon.rvs(scale=scale)
		rounded_value = int(round(new_value))

		if low <= rounded_value <= high:
			value = rounded_value
	
	return value

class PreferencesGenerator:
	def __init__(self, seed: int = 42, themes: list = [], authors: list = []):
		random.seed(seed)
		self.themes = themes
		self.authors = authors

	def sample(self) -> SpecificProblem:

		true_false = [True, False]

		# Num people must be an exponential distribution
		num_people = generate_exponential_integer()
		minors = random.choice(true_false)
		guided_visit = random.choice(true_false)
		num_experts = random.randint(0, num_people)
		past_museums_visits = random.randint(0, 50)
		favorite_period = random.randint(1000, 1900)
		favorite_theme = random.choice(self.themes).theme_name
		favorite_author = random.choice(self.authors).author_id

		sp = SpecificProblem(
			num_people=num_people,
			favorite_author=favorite_author,
			favorite_period=favorite_period,
			favorite_theme=favorite_theme,
			guided_visit=guided_visit,
			minors=minors,
			num_experts=num_experts,
			past_museum_visits=past_museums_visits
		)

		return sp
	
def create_sample_data(num_reference_samples: int, num_total_samples: int, random_seed: int = 42, themes: list = [], authors: list = []):
	"""
	Create a list of preferences for a given number of samples.

	Args:
		num_reference_samples (int): The number of random samples to generate and use as reference.
		num_total_samples (int): The total number of samples to generate (including the reference samples).
		random_seed (int): The random seed to use.
		themes (list): A list of themes to choose from.
		authors (list): A list of authors to choose from.
	Returns:
		list[dict]: A list of preferences for each sample.
	"""
	random.seed(random_seed)
	pg = PreferencesGenerator(random_seed, themes, authors)

	reference_samples = [pg.sample() for _ in range(num_reference_samples)]

	num_samples_to_generate = num_total_samples - num_reference_samples

	museum_visits = [sample.past_museum_visits for sample in reference_samples]
	museum_visits_prob = softmax(museum_visits)

	repeated_samples = random.choices(reference_samples, weights=museum_visits_prob, k=num_samples_to_generate)

	return reference_samples + repeated_samples

# #Visualize the exponential distribution function
# import matplotlib.pyplot as plt
# import seaborn as sns

# data = [generate_exponential_integer(scale=50) for _ in range(10000)]
# sns.histplot(data, kde=True)
# plt.show()
class TimeLimitGenerator:
    def __init__(self, low: int, high: int):
        """
        Initialize the generator with a range [low, high].
        We will use a truncated normal distribution centered around the mean (low + high) / 2.
        """
        assert low < high, "The value of 'low' must be smaller than 'high'."
        self.low = low
        self.high = high
        self.mean = (low + high) / 2
        
        # Choose a standard deviation relative to the range
        # For example, 1/6 of the range so that roughly 99.7% of values fall within [low, high]
        # This ensures a good concentration around the mean.
        self.sigma = (self.high - self.low) / 6
        
        # Calculate the normalized bounds for truncnorm
        # truncnorm expects bounds in terms of the standard normal distribution.
        self.a = (self.low - self.mean) / self.sigma
        self.b = (self.high - self.mean) / self.sigma

        # Create a truncnorm distribution object
        self.dist = truncnorm(self.a, self.b, loc=self.mean, scale=self.sigma)

    def generate(self) -> float:
        """
        Generate a random number within [low, high],
        using a truncated normal distribution centered around the mean.
        Most values will be concentrated near the mean.
        """
        return self.dist.rvs()