from sentence_transformers import SentenceTransformer
from math import exp

# Load the model
model = SentenceTransformer("thenlper/gte-small")
print("Model loaded successfully!")

# Sentence to compare
sentence_to_compare = "We are a group of young professionals who enjoy art and music."

# List of sentences describing different groups
sentences = [
    "We are a group of energetic retirees who love history and enjoy walking tours.",
    "A group of quiet middle-aged professionals who are passionate about art and culture.",
    "We are a family of four with two young children who are curious and playful.",
    "A team of physically fit young athletes who enjoy outdoor activities and challenges.",
    "A group of enthusiastic book club members who love discussing literature.",
    "We are a group of creative teenagers who enjoy photography and visual storytelling.",
    "A cheerful group of friends in their twenties who love exploring new places and meeting people.",
    "We are a group of food enthusiasts in our thirties who enjoy trying diverse cuisines.",
    "A group of science enthusiasts, mostly in their fifties, who enjoy learning about new discoveries.",
    "We are a close-knit family of grandparents and grandchildren who enjoy spending quality time together.",
    "A small group of elderly scholars who are meticulous and reflective.",
    "We are a lively band of teenagers who love music festivals and concerts.",
    "A family of three with a toddler, traveling with a stroller and lots of snacks.",
    "A small group of business executives in their forties visiting for a quick corporate retreat.",
    "We are a duo of adventure-seeking college roommates who love hiking and exploring.",
    "A group of middle-aged neighbors who enjoy gardening and bird-watching.",
    "We are a tightly-knit community of recent graduates exploring career opportunities.",
    "A retired couple who appreciate historical landmarks and quiet museums.",
    "We are a team of young tech enthusiasts, always on the lookout for innovation.",
    "A group of friends who are in their early thirties, coming for a weekend getaway.",
    "We are a set of cousins ranging from teens to adults, here to have a family reunion.",
    "A small tour group of professors and researchers attending a local conference.",
    "We are a group of best friends in our late twenties who enjoy craft beer and street art.",
    "A cluster of distant relatives meeting for the first time, eager to bond over a trip.",
    "We are a pair of newlyweds looking for romantic spots and scenic views.",
    "A group of quiet and introverted individuals who prefer tranquil spaces and minimal crowds.",
    "We are a band of young volunteers interested in environmental activism and community service.",
    "A handful of fashion-forward students who are keen on discovering trendy neighborhoods.",
    "We are a group of parents with young teenagers aiming to learn something new every day.",
    "A large extended family spanning three generations, excited to share experiences.",
    "We are two close friends in our fifties looking for culinary classes and workshops.",
    "A trio of digital nomads who balance work and leisure while traveling.",
    "We are a small group of language learners hoping to practice conversation skills.",
    "A circle of yoga enthusiasts who value relaxation, meditation, and serene environments.",
    "We are a sports team in our early twenties, eager to try new physical challenges.",
    "A group of grandparents who want to introduce their grandchildren to local history.",
    "We are a congregation of art students seeking inspiration from galleries and street murals.",
    "A class of high school seniors on a cultural exchange program, curious and open-minded.",
    "We are a circle of book lovers who relish quiet cafes and literary discussions.",
    "A group of working parents on a short vacation, hoping for family-friendly activities.",
    "We are three roommates in our early thirties exploring a new city to find hidden gems."
]

# Encode the sentences
embedding_to_compare = model.encode(sentence_to_compare)
embeddings = model.encode(sentences)

# Use the model's native similarity function
similarities = model.similarity(embedding_to_compare, embeddings)

# Convert similarities tensor to a list
similarities = similarities.squeeze().tolist()

# Print results
for i, sentence in enumerate(sentences):
    print(f"Similarity between '{sentence_to_compare}' and '{sentence}': {similarities[i]:.4f}")

def logistic_rescale(sim, threshold=0.84, temperature=0.03):
    # Apply a logistic function centered around 'threshold'
    return 1 / (1 + exp(-(sim - threshold) / temperature))

rescaled_sims = [logistic_rescale(s) for s in similarities]

for sent, orig, scaled in zip(sentences, similarities, rescaled_sims):
    print(f"Original: {orig:.4f} -> Scaled: {scaled:.4f} | '{sent}'")