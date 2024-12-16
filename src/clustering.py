import sqlite3
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import silhouette_score
import joblib
import os

class Clustering:
    def __init__(self, db_path='./data/database_2000.db', model_path='./models/kmeans_model.joblib'):
        self.db_path = db_path
        self.model_path = model_path
        self.conn = sqlite3.connect(self.db_path)
        self.scaler = StandardScaler()
        self.label_encoder_theme = LabelEncoder()
        self.label_encoder_author = LabelEncoder()
        self.kmeans = None
        self.data = None
        self.cluster_labels = None
        self.feature_names = []
        self.ids = None  # Initialize ids attribute

    def determine_optimal_clusters(self, X_scaled, min_clusters=3, max_clusters=10, minimum_examples_per_cluster=3):
        """
        Determine the optimal number of clusters using the silhouette score
        and ensure each cluster has at least minimum_examples_per_cluster examples.
        Update the KMeans model with the best result that satisfies the constraint.
        """
        best_score = -1
        best_k = None
        best_model = None  # Track the best model

        # Iterate over the range of clusters
        for k in range(min_clusters, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)
            score = silhouette_score(X_scaled, labels)
            print(f'Number of clusters: {k}, Silhouette Score: {score:.4f}')

            # Check if all clusters have at least minimum_examples_per_cluster examples
            unique, counts = pd.Series(labels).value_counts().sort_index().index, pd.Series(labels).value_counts().sort_index().values
            if all(count >= minimum_examples_per_cluster for count in counts):
                print(f'All clusters have at least {minimum_examples_per_cluster} examples.')
                # Update the best result if this score is the highest
                if score > best_score:
                    best_score = score
                    best_k = k
                    best_model = kmeans
            else:
                print(f'Cluster size below minimum for k={k}. Skipping this k.')

        if best_model is None:
            raise ValueError(f"No k between {min_clusters} and {max_clusters} satisfies the minimum examples per cluster constraint.")

        # Finalize the KMeans model with the best k
        self.kmeans = best_model
        self.cluster_labels = self.kmeans.predict(X_scaled)
        print(f'\nOptimal number of clusters determined: {best_k} with Silhouette Score: {best_score:.4f}')

        return best_k

    def fetch_data_from_cases(self):
        """Fetch data from the cases table for clustering."""
        query = """
        SELECT case_id, num_people, preferred_author_name, preferred_year, 
               preferred_main_theme, guided_visit, minors, num_experts, past_museum_visits
        FROM cases
        ORDER BY case_id
        """
        df = pd.read_sql_query(query, self.conn)
        df['guided_visit'] = df['guided_visit'].astype(int)
        df['minors'] = df['minors'].astype(int)
        df['preferred_main_theme_encoded'] = self.label_encoder_theme.fit_transform(df['preferred_main_theme'])
        df['preferred_author_name_encoded'] = self.label_encoder_author.fit_transform(df['preferred_author_name'])

        features = ['num_people', 'preferred_author_name_encoded', 'preferred_year', 
                    'guided_visit', 'minors', 'num_experts', 'past_museum_visits',
                    'preferred_main_theme_encoded']
        self.data = df[features]
        self.ids = df['case_id']
        return df

    def encode_and_scale_features(self):
        """Encode categorical features and scale numerical features for clustering."""
        if self.data is None:
            raise ValueError("No data available. Fetch data first.")
        X_scaled = self.scaler.fit_transform(self.data)
        self.feature_names = list(self.data.columns)
        return X_scaled

    def perform_clustering(self, X_scaled, min_k=3, max_k=10, minimum_examples_per_cluster=3):
        """
        Perform KMeans clustering using the determined optimal number of clusters.
        Ensures each cluster has at least minimum_examples_per_cluster examples.
        """
        if self.kmeans is None:
            print("Determining the optimal number of clusters...")
            self.determine_optimal_clusters(
                X_scaled, 
                min_clusters=min_k, 
                max_clusters=max_k, 
                minimum_examples_per_cluster=minimum_examples_per_cluster
            )
        else:
            # If KMeans is already initialized (e.g., from saved model), just predict
            self.cluster_labels = self.kmeans.predict(X_scaled)
        
        print("Cluster assignments completed.")
        return self.cluster_labels

    def ensure_cluster_column_in_cases(self):
        """Ensure the 'cluster' column exists in the cases table."""
        cursor = self.conn.execute("PRAGMA table_info(cases)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'cluster' not in columns:
            with self.conn:
                self.conn.execute("ALTER TABLE cases ADD COLUMN cluster INTEGER DEFAULT -1")
            print("Added 'cluster' column to cases table.")

    def save_clusters_to_cases(self):
        """Save cluster assignments to the cases table."""
        if self.cluster_labels is None:
            raise ValueError("No clustering results to save.")
        self.ensure_cluster_column_in_cases()
        with self.conn:
            for id_val, label in zip(self.ids, self.cluster_labels):
                self.conn.execute("UPDATE cases SET cluster = ? WHERE case_id = ?", (int(label), id_val))
        print("Clusters saved to cases table.")

    def save_model(self):
        """Save the model and preprocessing objects."""
        model_data = {
            'kmeans': self.kmeans,
            'scaler': self.scaler,
            'label_encoder_theme': self.label_encoder_theme,
            'label_encoder_author': self.label_encoder_author,
            'feature_names': self.feature_names
        }
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(model_data, self.model_path)
        print(f"Model saved to {self.model_path}")

    def load_model(self):
        """Load the model and preprocessing objects."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
        model_data = joblib.load(self.model_path)
        self.kmeans = model_data['kmeans']
        self.scaler = model_data['scaler']
        self.label_encoder_theme = model_data['label_encoder_theme']
        self.label_encoder_author = model_data['label_encoder_author']
        self.feature_names = model_data['feature_names']
        print(f"Model loaded from {self.model_path}")

    def print_cluster_statistics(self):
        """Print statistics for each cluster."""
        cluster_counts = pd.Series(self.cluster_labels).value_counts().sort_index()
        total = len(self.cluster_labels)
        cluster_percentages = (cluster_counts / total) * 100
        print("\nCluster Statistics:")
        for cluster_id in cluster_counts.index:
            print(f"Cluster {cluster_id}: {cluster_counts[cluster_id]} cases ({cluster_percentages[cluster_id]:.2f}%)")

    def print_centroids_readable(self):
        """
        Print the centroids in a readable format by inverse transforming the scaled features
        and decoding the encoded categorical features.
        """
        if self.kmeans is None:
            raise ValueError("K-Means model is not trained yet.")
        
        # Get the centroids from the K-Means model
        centroids_scaled = self.kmeans.cluster_centers_
        
        # Inverse scale the centroids
        centroids_original = self.scaler.inverse_transform(centroids_scaled)
        
        # Create a DataFrame for readability
        centroids_df = pd.DataFrame(centroids_original, columns=self.feature_names)
        
        # Decode 'preferred_main_theme_encoded' back to original labels
        centroids_df['preferred_main_theme'] = self.label_encoder_theme.inverse_transform(
            centroids_df['preferred_main_theme_encoded'].round().astype(int))
        
        # Decode 'preferred_author_name_encoded' back to original labels
        centroids_df['preferred_author_name'] = self.label_encoder_author.inverse_transform(
            centroids_df['preferred_author_name_encoded'].round().astype(int))
        
        # Drop the encoded columns
        centroids_df = centroids_df.drop(columns=['preferred_main_theme_encoded', 'preferred_author_name_encoded'])
        
        # Round 'guided_visit' and 'minors' to the nearest integer to reflect binary nature
        centroids_df['guided_visit'] = centroids_df['guided_visit'].round().astype(int)
        centroids_df['minors'] = centroids_df['minors'].round().astype(int)
        
        # Reorder columns for readability
        ordered_columns = ['num_people', 'preferred_author_name', 'preferred_year',
                           'guided_visit', 'minors', 'num_experts', 'past_museum_visits', 'preferred_main_theme']
        centroids_df = centroids_df[ordered_columns]
        
        print("\nCluster Centroids (Readable Format):")
        print(centroids_df)


    def classify_new_case(self, new_case):
        """Classify a new case into a cluster."""
        # Encode categorical features
        preferred_author_encoded = self.label_encoder_author.transform([new_case['preferred_author_name']])[0]
        preferred_theme_encoded = self.label_encoder_theme.transform([new_case['preferred_main_theme']])[0]

        # Create DataFrame for the new case
        df_new = pd.DataFrame([{
            'num_people': new_case['num_people'],
            'preferred_author_name_encoded': preferred_author_encoded,
            'preferred_year': new_case['preferred_year'],
            'guided_visit': new_case['guided_visit'],
            'minors': new_case['minors'],
            'num_experts': new_case['num_experts'],
            'past_museum_visits': new_case['past_museum_visits'],
            'preferred_main_theme_encoded': preferred_theme_encoded
        }])
        df_new = df_new[self.feature_names]
        X_scaled_new = self.scaler.transform(df_new)
        return int(self.kmeans.predict(X_scaled_new)[0])

    def close_connection(self):
        """Close the database connection."""
        self.conn.close()
        print("Database connection closed.")

# Usage Example
if __name__ == "__main__":
    # Initialize the clustering system
    clustering_system = Clustering(db_path='./data/database_2000.db', model_path='./models/kmeans_model.joblib')

    try:
        # Fetch data and perform clustering
        raw_data = clustering_system.fetch_data_from_cases()
        X_scaled = clustering_system.encode_and_scale_features()
        clustering_system.perform_clustering(X_scaled, min_k=20, max_k=50, minimum_examples_per_cluster=23)
        clustering_system.save_clusters_to_cases()
        clustering_system.print_cluster_statistics()
        clustering_system.print_centroids_readable()
        clustering_system.save_model()
    except ValueError as ve:
        print(f"Clustering Error: {ve}")
    finally:
        clustering_system.close_connection()

    # Classify a new case
    new_case = {
        'num_people': 3,
        'preferred_author_name': "Pablo Picasso",
        'preferred_year': 1890,
        'preferred_main_theme': "natural",
        'guided_visit': 1,
        'minors': 0,
        'num_experts': 2,
        'past_museum_visits': 5
    }

    # Initialize a new clustering system instance for classification
    classification_system = Clustering(db_path='./data/database_2000.db', model_path='./models/kmeans_model.joblib')

    try:
        classification_system.load_model()
        cluster_id = classification_system.classify_new_case(new_case)
        print(f"\nThe new case is assigned to cluster: {cluster_id}")
    except FileNotFoundError as fnfe:
        print(f"Model Loading Error: {fnfe}")
    finally:
        classification_system.close_connection()