from recommender import Recommender

def main():
	r = Recommender(cf_decay_factor=1, cf_alpha=1, cf_method='pearson', cf_gamma=1)
	r.evaluate(reload_cf=False, save=True)

if __name__ == '__main__':
	main()