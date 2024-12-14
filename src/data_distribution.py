import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load data from JSON file
with open('data/sorted_artworks.json', 'r') as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

# Keep top 100
df = df.head(100)

# Descriptive statistics
print("Basic descriptive statistics:")
print(df.describe())

# Calculate mode manually (as Pandas does not compute mode for non-numeric columns)
print("\nMode of categorical attributes:")
for col in df.select_dtypes(include=['object']).columns:
    mode = df[col].mode().iloc[0]
    print(f"{col}: {mode}")

# Create histograms for numeric columns
num_cols = df.select_dtypes(include=[np.number]).columns

# If num cols are don't have id keep the
num_cols = [col for col in num_cols if 'id' not in col]

for col in num_cols:
    plt.figure()
    sns.histplot(df[col], kde=True, bins=30, color='blue')
    plt.title(f'Histogram of {col}')
    plt.xlabel(col)
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.show()

# Bar plot for styles
style_counts = df['style'].explode().value_counts()
plt.figure()
style_counts.plot(kind='bar', color='orange')
plt.title('Frequency of Art Styles')
plt.xlabel('Style')
plt.ylabel('Frequency')
plt.grid(axis='y')
plt.show()

# Bar plot for artists
artist_counts = df['created_by'].value_counts()
plt.figure()
artist_counts.plot(kind='bar', color='red')
plt.title('Frequency of Artists')
plt.xlabel('Artist')
plt.ylabel('Frequency')
plt.grid(axis='y')
plt.show()

# Scatter plot: Complexity vs. Dimension
plt.figure()
sns.scatterplot(data=df, x='dimension', y='complexity', hue='relevance', palette='viridis')
plt.title('Dimension vs Complexity')
plt.xlabel('Dimension')
plt.ylabel('Complexity')
plt.grid(True)
plt.show()

# Line plot: Artworks per year
artworks_per_year = df['artwork_in_period'].value_counts().sort_index()
plt.figure()
artworks_per_year.plot(kind='line', color='green')
plt.title('Number of Artworks per Year')
plt.xlabel('Year')
plt.ylabel('Number of Artworks')
plt.grid(True)
plt.show()

# Average complexity by author
avg_complexity_by_author = df.groupby('created_by')['complexity'].mean().sort_values(ascending=False)
plt.figure()
avg_complexity_by_author.plot(kind='bar', color='purple')
plt.title('Average Complexity by Author')
plt.xlabel('Author')
plt.ylabel('Average Complexity')
plt.grid(axis='y')
plt.show()