import sqlite3
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import silhouette_score
import joblib
import os

class Clustering:
    def __init__(self, db_path='./data/database.db', model_path='./models/kmeans_model.joblib'):
        self.db_path = db_path
        self.model_path = model_path
        self.conn = sqlite3.connect(self.db_path)
        self.scaler = StandardScaler()
        self.label_encoder_theme = LabelEncoder()
        self.label_encoder_author = LabelEncoder()  # New LabelEncoder for favorite_author
        self.kmeans = None
        self.data = None
        self.cluster_labels = None
        self.feature_names = []
    
    def determine_optimal_clusters(self, X_scaled, min_clusters=3, max_clusters=10):
        """Determine the optimal number of clusters using the silhouette score."""
        best_score = -1
        best_k = 2
        for k in range(min_clusters, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)
            score = silhouette_score(X_scaled, labels)
            print(f'Number of clusters: {k}, Silhouette Score: {score:.4f}')
            if score > best_score:
                best_score = score
                best_k = k
        self.kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        self.kmeans.fit(X_scaled)
        self.cluster_labels = self.kmeans.predict(X_scaled)
        silhouette_avg = silhouette_score(X_scaled, self.cluster_labels)
        print(f'\nOptimal number of clusters determined: {best_k} with Silhouette Score: {silhouette_avg:.4f}')
        return best_k

    def fetch_data_from_specific_problems(self):
        """
        Fetch data from the specific_problems table for clustering.
        """
        query = """
        SELECT id, num_people, favorite_author, favorite_period, favorite_theme, 
               guided_visit, minors, num_experts, past_museum_visits
        FROM specific_problems
        ORDER BY id
        """
        df = pd.read_sql_query(query, self.conn)
        
        # Cast 'guided_visit' and 'minors' to integer
        df['guided_visit'] = df['guided_visit'].astype(int)
        df['minors'] = df['minors'].astype(int)
        
        # Encode favorite_theme using LabelEncoder
        df['favorite_theme_encoded'] = self.label_encoder_theme.fit_transform(df['favorite_theme'])
        
        # Encode favorite_author using LabelEncoder
        df['favorite_author_encoded'] = self.label_encoder_author.fit_transform(df['favorite_author'])
        
        # Select relevant features for clustering in the specified order
        features = ['num_people', 'favorite_author_encoded', 'favorite_period', 
                   'guided_visit', 'minors', 'num_experts', 'past_museum_visits',
                   'favorite_theme_encoded']
        
        self.data = df[features]
        self.ids = df['id']
        return df

    def encode_and_scale_features(self):
        """
        Encode categorical features and scale numerical features for clustering.
        """
        if self.data is None:
            raise ValueError("No data available. Fetch data first.")
        
        # Scale the features
        X_scaled = self.scaler.fit_transform(self.data)
        self.feature_names = list(self.data.columns)
        return X_scaled

    def perform_clustering(self, X_scaled):
        """Perform K-Means clustering on the standardized data."""
        if self.kmeans is None:
            self.determine_optimal_clusters(X_scaled)
        else:
            # If kmeans already exists, just predict
            self.cluster_labels = self.kmeans.predict(X_scaled)
        print("\nCluster assignments completed.")
        return self.cluster_labels

    def ensure_cluster_column_in_abstract_problems(self):
        """
        Ensure the 'cluster' column exists in the abstract_problems table.
        """
        cursor = self.conn.execute("PRAGMA table_info(abstract_problems)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'cluster' not in columns:
            with self.conn:
                self.conn.execute("ALTER TABLE abstract_problems ADD COLUMN cluster INTEGER DEFAULT -1")
            print("Added 'cluster' column to abstract_problems table.")
        else:
            print("'cluster' column already exists in abstract_problems table.")

    def save_clusters_to_abstract_problems(self):
        """
        Save the cluster assignments to the abstract_problems table based on id.
        """
        if self.cluster_labels is None:
            raise ValueError("No clustering results to save. Perform clustering first.")
        
        # Ensure 'cluster' column exists
        self.ensure_cluster_column_in_abstract_problems()
        
        # Fetch all IDs from specific_problems ordered by id
        cursor = self.conn.execute("SELECT id FROM specific_problems ORDER BY id")
        ids = [row[0] for row in cursor.fetchall()]
        
        if len(ids) != len(self.cluster_labels):
            raise ValueError(f"Number of cluster labels ({len(self.cluster_labels)}) does not match number of specific_problems records ({len(ids)}).")
        
        # Update abstract_problems table with cluster labels based on id
        with self.conn:
            for id_val, label in zip(ids, self.cluster_labels):
                self.conn.execute(
                    "UPDATE abstract_problems SET cluster = ? WHERE id = ?",
                    (int(label), id_val)
                )
        print("Cluster assignments have been saved to abstract_problems table based on 'id'.")

    def print_cluster_statistics(self):
        """
        Print the number of cases in each cluster along with their percentages.
        """
        if self.cluster_labels is None:
            raise ValueError("No clustering results available. Perform clustering first.")
        
        cluster_counts = pd.Series(self.cluster_labels).value_counts().sort_index()
        total = len(self.cluster_labels)
        cluster_percentages = (cluster_counts / total) * 100
        
        print("\nCluster Statistics:")
        for cluster_id in cluster_counts.index:
            count = cluster_counts[cluster_id]
            percentage = cluster_percentages[cluster_id]
            print(f"Cluster {cluster_id}: {count} cases ({percentage:.2f}%)")

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
        
        # Decode the 'favorite_theme_encoded' back to original labels
        centroids_df['favorite_theme'] = self.label_encoder_theme.inverse_transform(centroids_df['favorite_theme_encoded'].round().astype(int))
        
        # Decode the 'favorite_author_encoded' back to original labels
        centroids_df['favorite_author'] = self.label_encoder_author.inverse_transform(centroids_df['favorite_author_encoded'].round().astype(int))
        
        # Drop the encoded columns
        centroids_df = centroids_df.drop(columns=['favorite_theme_encoded', 'favorite_author_encoded'])
        
        # Round 'guided_visit' and 'minors' to nearest integer to reflect binary nature
        centroids_df['guided_visit'] = centroids_df['guided_visit'].round().astype(int)
        centroids_df['minors'] = centroids_df['minors'].round().astype(int)
        
        # Reorder columns as specified
        ordered_columns = ['num_people', 'favorite_author', 'favorite_period', 
                           'guided_visit', 'minors', 'num_experts', 'past_museum_visits', 'favorite_theme']
        centroids_df = centroids_df[ordered_columns]
        
        print("\nCluster Centroids (Readable Format):")
        print(centroids_df)

    def save_model(self):
        """
        Save the trained K-Means model, scaler, and label encoders to a file using joblib.
        """
        model_data = {
            'kmeans': self.kmeans,
            'scaler': self.scaler,
            'label_encoder_theme': self.label_encoder_theme,
            'label_encoder_author': self.label_encoder_author,  # Save the author encoder
            'feature_names': self.feature_names
        }
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(model_data, self.model_path)
        print(f"K-Means model and preprocessing objects saved to {self.model_path}")

    def load_model(self):
        """
        Load the trained K-Means model, scaler, and label encoders from a file using joblib.
        """
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
        model_data = joblib.load(self.model_path)
        self.kmeans = model_data['kmeans']
        self.scaler = model_data['scaler']
        self.label_encoder_theme = model_data['label_encoder_theme']
        self.label_encoder_author = model_data['label_encoder_author']  # Load the author encoder
        self.feature_names = model_data['feature_names']
        print(f"K-Means model and preprocessing objects loaded from {self.model_path}")

    def classify_new_case(self, new_case):
        """
        Classify a new case by assigning it to an existing cluster.
        
        :param new_case: Dictionary with the new case attributes.
        :return: Cluster number.
        """
        # Handle unseen favorite_theme
        if new_case['favorite_theme'] not in self.label_encoder_theme.classes_:
            raise ValueError(f"Unknown favorite_theme: {new_case['favorite_theme']}. Please retrain the model with this new category.")
        
        # Handle unseen favorite_author
        if new_case['favorite_author'] not in self.label_encoder_author.classes_:
            raise ValueError(f"Unknown favorite_author: {new_case['favorite_author']}. Please retrain the model with this new category.")
        
        # Encode favorite_theme and favorite_author
        favorite_theme_encoded = self.label_encoder_theme.transform([new_case['favorite_theme']])[0]
        favorite_author_encoded = self.label_encoder_author.transform([new_case['favorite_author']])[0]
        
        # Create a DataFrame from the new case in the specified order
        df_new = pd.DataFrame([{
            'num_people': new_case['num_people'],
            'favorite_author_encoded': favorite_author_encoded,
            'favorite_period': new_case['favorite_period'],
            'guided_visit': new_case['guided_visit'],
            'minors': new_case['minors'],
            'num_experts': new_case['num_experts'],
            'past_museum_visits': new_case['past_museum_visits'],
            'favorite_theme_encoded': favorite_theme_encoded
        }])
        
        # Ensure feature order
        df_new = df_new[self.feature_names]
        
        # Scale the features
        X_scaled_new = self.scaler.transform(df_new)
        
        # Predict the cluster
        cluster_id = self.kmeans.predict(X_scaled_new)[0]
        return int(cluster_id)
    
    def recommend_from_cluster(self, input_case):
        """
        Recommend similar cases from the same cluster as the input case.
        This function has been modified to remove top_k=3 retrieval.
        Instead, it only assigns the input case to a cluster.
        
        :param input_case: Dictionary with the input case attributes.
        :return: Cluster number.
        """
        # Classify the input case to find its cluster
        cluster_id = self.classify_new_case(input_case)
        print(f"Input case assigned to cluster: {cluster_id}")
        return cluster_id

    def close_connection(self):
        """
        Close the SQLite database connection.
        """
        self.conn.close()
        print("Database connection closed.")

# Usage Example
"""if __name__ == "__main__":
    # Initialize the clustering system
    clustering_system = Clustering(db_path='./data/database.db', model_path='./models/kmeans_model.joblib')
    
    # Step 1: Fetch and preprocess data from specific_problems
    raw_data = clustering_system.fetch_data_from_specific_problems()
    print("Fetched data from specific_problems:")
    print(raw_data.head())
    
    # Step 2: Encode and scale features
    X_scaled = clustering_system.encode_and_scale_features()
    print("\nEncoded and scaled features:")
    print(X_scaled[:5])
    
    # Step 3: Determine optimal number of clusters and perform clustering
    clustering_system.determine_optimal_clusters(X_scaled, min_clusters=3, max_clusters=10)
    
    # Step 4: Assign clusters
    clustering_system.perform_clustering(X_scaled)
    
    # Step 5: Save cluster assignments to abstract_problems table
    clustering_system.save_clusters_to_abstract_problems()
    
    # Step 6: Print cluster statistics
    clustering_system.print_cluster_statistics()
    
    # Step 7: Print readable centroids
    clustering_system.print_centroids_readable()
    
    # Step 8: Save the trained model for future use
    clustering_system.save_model()
    
    # Step 9: Close the database connection
    clustering_system.close_connection()
    
    # ----- Assigning a New Case -----
    
    # Example of classifying a new case without retrieving recommendations
    new_case = {
        'num_people': 4,
        'favorite_author': "James McNeill",  # Must match existing categories
        'favorite_period': 1995,
        'favorite_theme': 'religious',    # Must match existing categories
        'guided_visit': 1,
        'minors': 0,
        'num_experts': 1,
        'past_museum_visits': 3
    }
    
    # Initialize the clustering system again for classification
    clustering_system = Clustering(db_path='./data/database.db', model_path='./models/kmeans_model.joblib')
    
    # Load the saved model
    clustering_system.load_model()
    
    # Classify the new case
    try:
        cluster_id = clustering_system.classify_new_case(new_case)
        print(f"\nThe new case is assigned to cluster: {cluster_id}")
    except ValueError as e:
        print(f"\nError: {e}")
    
    # Close the connection
    clustering_system.close_connection()"""