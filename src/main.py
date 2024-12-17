from recommender import Recommender

def main():
	r = Recommender(cf_decay_factor=1, cf_alpha=1, cf_gamma=1, beta=1)
	r.evaluate(save=False)

if __name__ == '__main__':
	main()