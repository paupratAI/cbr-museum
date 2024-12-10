import sqlite3
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import numpy as np

class ClusteringSystem:
    def __init__(self, db_path='./data/database.db', n_clusters=5):
        self.conn = sqlite3.connect(db_path)
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.kmeans = None
        self.data = None
        self.cluster_labels = None

    def fetch_data(self):
        """Fetch data from the database and prepare it for clustering."""
        query = """
        SELECT group_size, group_type, art_knowledge, time_coefficient, preferred_periods, 
            preferred_author, preferred_themes
        FROM abstract_problems
        """
        df = pd.read_sql_query(query, self.conn)
        
        # Preprocess data
        df['preferred_periods'] = df['preferred_periods'].apply(lambda x: len(eval(x)) if x else 0)
        df['preferred_themes'] = df['preferred_themes'].apply(lambda x: len(eval(x)) if x else 0)
        
        # Convert categorical variables to numeric
        df['group_type'] = pd.Categorical(df['group_type']).codes  # Label Encoding
        
        self.data = df
        return df


    def preprocess_data(self):
        """Standardize the data for clustering."""
        if self.data is None:
            raise ValueError("No data available. Fetch data first.")
        features = ['group_size', 'group_type', 'art_knowledge', 'time_coefficient', 
                    'preferred_periods', 'preferred_themes']
        scaled_data = self.scaler.fit_transform(self.data[features])
        return scaled_data

    def perform_clustering(self, scaled_data):
        """Perform K-Means clustering on the standardized data."""
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42)
        self.cluster_labels = self.kmeans.fit_predict(scaled_data)
        self.data['cluster'] = self.cluster_labels
        silhouette_avg = silhouette_score(scaled_data, self.cluster_labels)
        print(f"Silhouette Score: {silhouette_avg}")
        return self.data

    def ensure_cluster_column(self):
        """Ensure the 'cluster' column exists in the database."""
        with self.conn:
            self.conn.execute("""
                ALTER TABLE abstract_problems ADD COLUMN cluster INTEGER DEFAULT -1
            """)


    def save_clusters_to_db(self):
        """Save the cluster assignments back to the database."""
        if self.cluster_labels is None:
            raise ValueError("No clustering results to save. Perform clustering first.")
        with self.conn:
            for index, row in self.data.iterrows():
                self.conn.execute(
                    "UPDATE abstract_problems SET cluster = ? WHERE rowid = ?",
                    (row['cluster'], index + 1)
                )

    def recommend_from_cluster(self, input_case, top_k=3):
        """
        Recommend top-k cases from the same cluster as the input case.
        :param input_case: Dictionary with the input case attributes.
        :param top_k: Number of cases to recommend.
        """
        cluster_id = self.kmeans.predict(self.scaler.transform([[
            input_case['group_size'], input_case['group_type'], input_case['art_knowledge'],
            input_case['time_coefficient'], len(input_case['preferred_periods']),
            len(input_case['preferred_themes'])
        ]]))[0]

        similar_cases = self.data[self.data['cluster'] == cluster_id]
        return similar_cases.head(top_k).to_dict(orient='records')

# Usage
if __name__ == "__main__":
    clustering_system = ClusteringSystem(db_path='./data/database.db', n_clusters=5)
    
    # Fetch and preprocess data
    raw_data = clustering_system.fetch_data()
    processed_data = clustering_system.preprocess_data()
    
    # Perform clustering
    clustered_data = clustering_system.perform_clustering(processed_data)
    
    # Ensure 'cluster' column exists
    clustering_system.ensure_cluster_column()
    
    # Save cluster assignments to database
    clustering_system.save_clusters_to_db()
    
    # Recommend based on input case
    input_case = {
        'group_size': 4,
        'group_type': 2,
        'art_knowledge': 3,
        'time_coefficient': 0.8,
        'preferred_periods': [1, 2],
        'preferred_themes': [1]
    }
    recommendations = clustering_system.recommend_from_cluster(input_case, top_k=3)
    print("Recommendations:", recommendations)