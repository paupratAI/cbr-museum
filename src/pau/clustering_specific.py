import sqlite3
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import numpy as np

class Clustering:
    def __init__(self, db_path='./data/database.db'):
        self.conn = sqlite3.connect(db_path)
        self.n_clusters = None
        self.scaler = StandardScaler()
        self.kmeans = None
        self.data = None
        self.cluster_labels = None

    def determine_optimal_clusters(self, scaled_data, max_clusters=10):
        """Determine the optimal number of clusters using the silhouette score."""
        best_score = -1
        best_k = 2
        for k in range(2, max_clusters+1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(scaled_data)
            score = silhouette_score(scaled_data, labels)
            if score > best_score:
                best_score = score
                best_k = k
        self.n_clusters = best_k
        return best_k



    def fetch_data(self):
        """Fetch data from the database and prepare it for clustering."""
        query = """
        SELECT num_people, favorite_author, favorite_periods, favorite_theme, guided_visit,
            minors, num_experts, past_museum_visits
        FROM specific_problems
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
            """Perform K-Means clustering on the standardized data with an automatically determined number of clusters."""
            if self.n_clusters is None:
                self.determine_optimal_clusters(scaled_data)
            self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
            self.cluster_labels = self.kmeans.fit_predict(scaled_data)
            self.data['cluster'] = self.cluster_labels
            silhouette_avg = silhouette_score(scaled_data, self.cluster_labels)
            print(f"Chosen number of clusters: {self.n_clusters}")
            return self.data

    def ensure_cluster_column(self):
        """Ensure the 'cluster' column exists in the database."""
        # Check if the column already exists
        cursor = self.conn.execute("PRAGMA table_info(specific_problems)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'cluster' not in columns:
            with self.conn:
                self.conn.execute("ALTER TABLE specific_problems ADD COLUMN cluster INTEGER DEFAULT -1")



    def save_clusters_to_db(self):
        """Save the cluster assignments back to the database."""
        if self.cluster_labels is None:
            raise ValueError("No clustering results to save. Perform clustering first.")
        with self.conn:
            for index, row in self.data.iterrows():
                self.conn.execute(
                    "UPDATE specific_problems SET cluster = ? WHERE rowid = ?",
                    (row['cluster'], index + 1)
                )

    def recommend_from_cluster(self, input_case, top_k=3):
        """
        Recommend top-k cases from the same cluster as the input case.
        :param input_case: Dictionary with the input case attributes.
        :param top_k: Number of cases to recommend.
        """
        # Create a DataFrame with the same structure as the training data
        feature_names = ['group_size', 'group_type', 'art_knowledge', 'time_coefficient', 
                         'preferred_periods', 'preferred_themes']
        input_df = pd.DataFrame([[
            input_case['group_size'], 
            input_case['group_type'], 
            input_case['art_knowledge'],
            input_case['time_coefficient'], 
            len(input_case['preferred_periods']), 
            len(input_case['preferred_themes'])
        ]], columns=feature_names)

        # Scale using the scaler fitted on the training data
        scaled_input = self.scaler.transform(input_df)

        # Predict the cluster for the new case
        cluster_id = self.kmeans.predict(scaled_input)[0]

        # Retrieve similar cases from the same cluster
        similar_cases = self.data[self.data['cluster'] == cluster_id]
        return similar_cases.head(top_k).to_dict(orient='records')


# Usage
if __name__ == "__main__":
    clustering_system = Clustering(db_path='./data/database.db')
    
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
    print("length of recommendations:", len(recommendations))