from sentence_transformers import SentenceTransformer

# Load the model
model = SentenceTransformer("thenlper/gte-small")
print("Model loaded successfully!")

# Sentence to compare
sentence_to_compare = "We are a group of young students, excited and curious about science."

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
    "We are a close-knit family of grandparents and grandchildren who enjoy spending quality time together."
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