import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MultiLabelBinarizer, StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import joblib

# Define file paths
DATABASE_FILE = 'baiges/database.db'
CENTROIDS_FILE = 'baiges/centroids.joblib'  # Using .joblib for better serialization
PREPROCESSING_FILE = 'baiges/preprocessing.joblib'  # To store encoders and scalers

def load_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def preprocess_data(data, model):
    """
    Flatten and preprocess the JSON data into a pandas DataFrame suitable for clustering.
    Includes embedding textual descriptions.
    """
    records = []
    descriptions = []
    for case in data:
        record = {}
        # Numerical features
        record['group_size'] = case.get('group_size', 0)
        record['art_knowledge'] = case.get('art_knowledge', 0)
        record['time_coefficient'] = case.get('time_coefficient', 0.0)
        
        # Categorical features
        record['group_type'] = case.get('group_type', 'unknown')
        preferred_author = case.get('preferred_author', {})
        record['preferred_author_name'] = preferred_author.get('author_name', 'unknown')
        
        # Preferred periods - collect period names
        periods = case.get('preferred_periods', [])
        period_names = [period.get('period_name', 'unknown') for period in periods]
        record['preferred_period_names'] = period_names
        
        # Preferred author main periods
        main_periods = preferred_author.get('main_periods', [])
        main_period_names = [period.get('period_name', 'unknown') for period in main_periods]
        record['preferred_author_main_period_names'] = main_period_names
        
        # Preferred themes
        themes = case.get('preferred_themes', [])
        record['preferred_themes'] = themes
        
        # Textual description (assuming it's under 'description')
        description = case.get('description', '')
        descriptions.append(description)
        
        records.append(record)
    
    df = pd.DataFrame(records)
    
    # Embed textual descriptions
    if descriptions:
        embeddings = model.encode(descriptions, convert_to_numpy=True, show_progress_bar=True)
        # Add embeddings as separate columns
        for i in range(embeddings.shape[1]):
            df[f'desc_emb_{i}'] = embeddings[:, i]
    
    return df

def encode_features(df):
    """
    Encode categorical and list-based features using OneHotEncoder and MultiLabelBinarizer.
    Apply PCA to reduce embedding dimensionality.
    Returns the feature matrix and the fitted encoders and scaler.
    """
    # Define feature categories
    numerical_features = ['group_size', 'art_knowledge', 'time_coefficient']
    categorical_features = ['group_type', 'preferred_author_name']
    list_features = ['preferred_period_names', 'preferred_author_main_period_names', 'preferred_themes']
    embedding_features = [col for col in df.columns if col.startswith('desc_emb_')]
    
    # Initialize encoders
    ohe = OneHotEncoder(handle_unknown='ignore', sparse=False)
    mlb_period = MultiLabelBinarizer()
    mlb_author_period = MultiLabelBinarizer()
    mlb_themes = MultiLabelBinarizer()
    
    # Fit encoders on the data
    ohe.fit(df[categorical_features])
    mlb_period.fit(df['preferred_period_names'])
    mlb_author_period.fit(df['preferred_author_main_period_names'])
    mlb_themes.fit(df['preferred_themes'])
    
    # Transform features
    ohe_features = ohe.transform(df[categorical_features])
    period_features = mlb_period.transform(df['preferred_period_names'])
    author_period_features = mlb_author_period.transform(df['preferred_author_main_period_names'])
    themes_features = mlb_themes.transform(df['preferred_themes'])
    embedding_features_data = df[embedding_features].values
    
    # Apply PCA to reduce embedding dimensions
    pca = PCA(n_components=50, random_state=42)  # Adjust n_components as needed
    embedding_reduced = pca.fit_transform(embedding_features_data)
    
    # Standardize numerical and PCA-reduced embedding features
    scaler = StandardScaler()
    numerical_scaled = scaler.fit_transform(df[numerical_features])
    embedding_scaled = scaler.fit_transform(embedding_reduced)
    
    # Combine all features
    X = np.hstack([
        numerical_scaled,
        ohe_features,
        period_features,
        author_period_features,
        themes_features,
        embedding_scaled
    ])
    
    # Feature names for reference (optional)
    feature_names = numerical_features + \
                    list(ohe.get_feature_names_out(categorical_features)) + \
                    list(mlb_period.classes_) + \
                    list(mlb_author_period.classes_) + \
                    list(mlb_themes.classes_) + \
                    [f'pca_emb_{i}' for i in range(embedding_reduced.shape[1])]
    
    return X, ohe, mlb_period, mlb_author_period, mlb_themes, pca, scaler, feature_names

def find_optimal_clusters(X, min_k=2, max_k=10):
    """
    Determine the optimal number of clusters using silhouette score.
    """
    best_k = min_k
    best_score = -1
    for k in range(min_k, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        score = silhouette_score(X, labels, metric='euclidean')
        print(f'Number of clusters: {k}, Silhouette Score: {score:.4f}')
        if score > best_score:
            best_k = k
            best_score = score
    print(f'Optimal number of clusters: {best_k} with Silhouette Score: {best_score:.4f}')
    return best_k

def cluster_data(X, n_clusters):
    """
    Apply K-Means clustering to the data.
    """
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)
    centroids = kmeans.cluster_centers_
    return labels, centroids, kmeans

def save_centroids(centroids, file_path):
    """
    Save the centroids to a file for future use.
    """
    joblib.dump({
        'centroids': centroids
    }, file_path)
    print(f'Centroids saved to {file_path}')
    return centroids

def load_centroids(file_path):
    """
    Load the centroids from a file.
    """
    data = joblib.load(file_path)
    return data['centroids']

def save_preprocessing(ohe, mlb_period, mlb_author_period, mlb_themes, pca, scaler, feature_names, file_path):
    """
    Save the preprocessing objects to a file for future use.
    """
    joblib.dump({
        'ohe': ohe,
        'mlb_period': mlb_period,
        'mlb_author_period': mlb_author_period,
        'mlb_themes': mlb_themes,
        'pca': pca,
        'scaler': scaler,
        'feature_names': feature_names
    }, file_path)
    print(f'Preprocessing objects saved to {file_path}')

def load_preprocessing(file_path):
    """
    Load the preprocessing objects from a file.
    """
    data = joblib.load(file_path)
    return data

def assign_cluster(new_case, centroids, ohe, mlb_period, mlb_author_period, mlb_themes, pca, scaler, model):
    """
    Assign a new case to the nearest cluster based on Euclidean distance to centroids.
    """
    # Preprocess the new case
    record = {}
    # Numerical features
    record['group_size'] = new_case.get('group_size', 0)
    record['art_knowledge'] = new_case.get('art_knowledge', 0)
    record['time_coefficient'] = new_case.get('time_coefficient', 0.0)
    
    # Categorical features
    record['group_type'] = new_case.get('group_type', 'unknown')
    preferred_author = new_case.get('preferred_author', {})
    record['preferred_author_name'] = preferred_author.get('author_name', 'unknown')
    
    # Preferred periods
    periods = new_case.get('preferred_periods', [])
    period_names = [period.get('period_name', 'unknown') for period in periods]
    record['preferred_period_names'] = period_names
    
    # Preferred author main periods
    main_periods = preferred_author.get('main_periods', [])
    main_period_names = [period.get('period_name', 'unknown') for period in main_periods]
    record['preferred_author_main_period_names'] = main_period_names
    
    # Preferred themes
    themes = new_case.get('preferred_themes', [])
    record['preferred_themes'] = themes
    
    # Textual description
    description = new_case.get('description', '')
    
    # Create DataFrame
    df_new = pd.DataFrame([record])
    
    # Embed textual description
    if description:
        embedding = model.encode([description], convert_to_numpy=True)
        # Apply PCA
        embedding_reduced = pca.transform(embedding)
    else:
        # If no description, fill with zeros
        embedding_reduced = np.zeros((1, pca.n_components_))
    
    # One-hot encode categorical features
    ohe_features = ohe.transform(df_new[['group_type', 'preferred_author_name']])
    period_features = mlb_period.transform(df_new['preferred_period_names'])
    author_period_features = mlb_author_period.transform(df_new['preferred_author_main_period_names'])
    themes_features = mlb_themes.transform(df_new['preferred_themes'])
    
    # Standardize numerical and PCA-reduced embedding features
    numerical_scaled = scaler.transform(df_new[['group_size', 'art_knowledge', 'time_coefficient']])
    embedding_scaled = scaler.transform(embedding_reduced)
    
    # Combine all features
    X_new = np.hstack([
        numerical_scaled,
        ohe_features,
        period_features,
        author_period_features,
        themes_features,
        embedding_scaled
    ])
    
    # Assign to nearest centroid based on Euclidean distance
    distances = np.linalg.norm(centroids - X_new, axis=1)
    assigned_cluster = np.argmin(distances)
    return assigned_cluster

def main():
    # Initialize the sentence transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')  # Efficient and effective model
    
    # Step 1: Load data
    data = load_data(DATABASE_FILE)
    
    # Step 2: Preprocess data
    df = preprocess_data(data, model)
    
    # Step 3: Encode features
    X, ohe, mlb_period, mlb_author_period, mlb_themes, pca, scaler, feature_names = encode_features(df)
    
    # Step 4: Find optimal number of clusters
    optimal_k = find_optimal_clusters(X, min_k=2, max_k=10)
    
    # Step 5: Cluster data
    labels, centroids, kmeans = cluster_data(X, optimal_k)
    
    # Step 6: Assign cluster labels to data
    for idx, case in enumerate(data):
        case['cluster'] = int(labels[idx])
    
    # Save updated data back to database.db
    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    print(f'Cluster labels assigned and saved to {DATABASE_FILE}')
    
    # Step 7: Save centroids and preprocessing objects
    save_centroids(centroids, CENTROIDS_FILE)
    save_preprocessing(ohe, mlb_period, mlb_author_period, mlb_themes, pca, scaler, feature_names, PREPROCESSING_FILE)
    
    # Example of assigning a new case
    new_case = {
        "group_size": 4,
        "group_type": "scholar",
        "art_knowledge": 2,
        "preferred_periods": [
            {
                "period_id": 2,
                "year_beginning": 1140,
                "year_end": 1400,
                "themes": [
                    "Christianity",
                    "Battles and Wars",
                    "Antiquity",
                    "Monarchies",
                    "Greek Mythology"
                ],
                "period_name": "Gothic"
            }
        ],
        "preferred_author": {
            "author_id": 1,
            "author_name": "Stuart Davis",
            "main_periods": [
                {
                    "period_id": 15,
                    "year_beginning": 1880,
                    "year_end": 1910,
                    "themes": [
                        "Despair",
                        "Nostalgia",
                        "Mysticism",
                        "Occult"
                    ],
                    "period_name": "Post-Impressionism"
                }
            ]
        },
        "preferred_themes": [
            "Battles and Wars",
            "Conquests",
            "Revolutions",
            "Antiquity",
            "Monarchies",
            "Colonizations"
        ],
        "time_coefficient": 1.5,
        "description": "A group deeply interested in Gothic art and its influence on modern aesthetics."
    }
    
    # Load centroids and preprocessing objects
    centroids_loaded = load_centroids(CENTROIDS_FILE)
    preprocessing = load_preprocessing(PREPROCESSING_FILE)
    
    # Assign cluster to the new case
    assigned_cluster = assign_cluster(
        new_case,
        centroids_loaded,
        preprocessing['ohe'],
        preprocessing['mlb_period'],
        preprocessing['mlb_author_period'],
        preprocessing['mlb_themes'],
        preprocessing['pca'],
        preprocessing['scaler'],
        model
    )
    
    print(f'The new case is assigned to cluster: {assigned_cluster}')

if __name__ == "__main__":
    main()
