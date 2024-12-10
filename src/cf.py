import sqlite3
from typing import Dict, List
from scipy.stats import pearsonr
from scipy.spatial.distance import cosine
import numpy as np

class CF:
    """
    This class implements a Collaborative Filtering (CF) system based on group information 
    and their ratings of various items. Ratings are stored along with the number of times 
    each group has visited an item, which are used to compute average ratings.

    The system uses both user-based and item-based collaborative filtering to recommend items.
    """

    def __init__(self, db_path='../data/database.db'):
        """
        Initializes the collaborative filtering system by connecting to the database.

        Parameters
        ----------
        db_path : str, optional
            Path to the SQLite database storing the ratings, default is '../data/database.db'.
        """
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        """
        Creates the necessary table to store group ratings and visit counts for items.
        Each entry corresponds to a (group_id, item_id) pair, storing the average rating 
        and the total number of visits that led to that rating.
        """
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS ratings (
                    group_id INTEGER,
                    item_id INTEGER,
                    rating REAL,
                    visit_count INTEGER DEFAULT 0,
                    PRIMARY KEY (group_id, item_id)
                );
            ''')

    def store_rating(self, group_id: int, item_id: int, rating: float):
        """
        Stores or updates a group's average rating and visit count for an item.

        If the group has already visited the item, the stored rating is updated 
        as a weighted average using the new rating. The visit_count is incremented 
        by one. If it's the first time the group rates the item, a new record is inserted.

        Parameters
        ----------
        group_id : int
            Unique identifier for the group.
        item_id : int
            Unique identifier for the item.
        rating : float
            The rating given to the item by the group on this visit.
        """
        # Check if there's an existing record
        existing = self.conn.execute('''
            SELECT rating, visit_count FROM ratings 
            WHERE group_id = ? AND item_id = ?
        ''', (group_id, item_id)).fetchone()

        if existing is None:
            # No existing record, insert a new one
            new_rating = rating
            new_visit_count = 1
        else:
            old_rating, old_visit_count = existing
            # Compute the new average rating
            total_score = old_rating * old_visit_count + rating
            new_visit_count = old_visit_count + 1
            new_rating = total_score / new_visit_count

        with self.conn:
            self.conn.execute('''
                INSERT INTO ratings (group_id, item_id, rating, visit_count)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(group_id, item_id) DO UPDATE SET 
                    rating=excluded.rating,
                    visit_count=excluded.visit_count;
            ''', (group_id, item_id, new_rating, new_visit_count))

    def get_group_ratings(self, group_id: int) -> Dict[int, tuple[float, int]]:
        """
        Retrieves all averaged ratings from a specific group.

        Parameters
        ----------
        group_id : int
            Unique identifier for the group.

        Returns
        -------
        Dict[int, tuple[float, int]]
            Dictionary mapping item identifiers to a tuple of (rating, visit_count).
        """
        query = "SELECT item_id, rating, visit_count FROM ratings WHERE group_id = ?"
        rows = self.conn.execute(query, (group_id,)).fetchall()
        return {r[0]: (r[1], r[2]) for r in rows}
    
    def get_item_ratings(self, item_id: int) -> Dict[int, tuple[float, int]]:
        """
        Retrieves all averaged ratings for a specific item.

        Parameters
        ----------
        item_id : int
            Unique identifier for the item.

        Returns
        -------
        Dict[int, tuple[float, int]]
            Dictionary mapping group identifiers to a tuple of (rating, visit_count).
        """
        query = "SELECT group_id, rating, visit_count FROM ratings WHERE item_id = ?"
        rows = self.conn.execute(query, (item_id,)).fetchall()
        return {r[0]: (r[1], r[2]) for r in rows}

    def get_all_groups(self) -> List[int]:
        """
        Retrieves the list of all groups that have provided at least one rating.

        Returns
        -------
        List[int]
            List of group identifiers.
        """
        query = "SELECT DISTINCT group_id FROM ratings"
        rows = self.conn.execute(query).fetchall()
        return [r[0] for r in rows]

    def get_all_items(self) -> List[int]:
        """
        Retrieves the list of all items that have been rated by any group.

        Returns
        -------
        List[int]
            List of item identifiers.
        """
        query = "SELECT DISTINCT item_id FROM ratings"
        rows = self.conn.execute(query).fetchall()
        return [r[0] for r in rows]

    def group_ratings_similarity(self, group_id_a: int, group_id_b: int, method: str = 'cosine') -> float:
        """
        Computes the similarity between two groups based on their ratings of items.

        Parameters
        ----------
        group_id_a : int
            Identifier of the first group.
        group_id_b : int
            Identifier of the second group.
        method : str, optional
            The similarity method to use ('cosine' or 'pearson'), default is 'cosine'.

        Returns
        -------
        float
            Similarity score between the groups based on their ratings.
        """
        assert method in ['cosine', 'pearson'], "Invalid method; use 'cosine' or 'pearson'"

        ratings_a = self.get_group_ratings(group_id_a)
        ratings_b = self.get_group_ratings(group_id_b)

        # Find common items
        common_items = set(ratings_a.keys()) & set(ratings_b.keys())
        if not common_items:
            return 0  # No items in common

        ratings_a_vec = np.array([ratings_a[i][0] for i in common_items])
        ratings_b_vec = np.array([ratings_b[i][0] for i in common_items])

        if method == 'cosine':
            # Cosine similarity
            return 1 - cosine(ratings_a_vec, ratings_b_vec)
        elif method == 'pearson':
            # Pearson correlation
            if len(ratings_a_vec) < 2:  # Pearson requires at least 2 data points
                return 0
            return pearsonr(ratings_a_vec, ratings_b_vec).correlation

    def item_similarity(self, item_id_a: int, item_id_b: int, method: str = 'cosine') -> float:
        """
        Computes the similarity between two items based on user ratings.

        Parameters
        ----------
        item_id_a : int
            Identifier of the first item.
        item_id_b : int
            Identifier of the second item.
        method : str, optional
            The similarity method to use, default is 'cosine'.

        Returns
        -------
        float
            Similarity score between the items.
        """
        ratings_a = self.get_item_ratings(item_id_a)
        ratings_b = self.get_item_ratings(item_id_b)

        common_groups = set(ratings_a.keys()) & set(ratings_b.keys())
        if not common_groups:
            return 0  # No groups in common

        ratings_a_vec = np.array([ratings_a[g] for g in common_groups])
        ratings_b_vec = np.array([ratings_b[g] for g in common_groups])

        if method == 'cosine':
            return 1 - cosine(ratings_a_vec, ratings_b_vec)
        elif method == 'pearson':
            return pearsonr(ratings_a_vec, ratings_b_vec).correlation
        else:
            raise ValueError("Invalid method; use 'cosine' or 'pearson'")
    
    def recommend_items(
        self, target_group_id: int, alpha: float, similarity: str = 'cosine',
        top_k_users: int | None = None, top_k_items: int | None = None
    ) -> List[int]:
        """
        Recommends a sorted list of items for a target group.

        Parameters
        ----------
        target_group_id : int
            Identifier of the target group.
        alpha : float
            Weight for combining user-based and item-based predictions.
        similarity : str
            The similarity method to use for both group and item similarities ('cosine', 'pearson').
        top_k_users : int, optional
            Number of most similar users to consider for user-based filtering. If None, all users are considered.
        top_k_items : int, optional
            Number of most similar items to consider for item-based filtering. If None, all items are considered.

        Returns
        -------
        List[int]
            Sorted list of item IDs by predicted relevance.
        """
        assert 0 <= alpha <= 1, "Alpha must be between 0 and 1"
        assert similarity in ['cosine', 'pearson'], "Invalid similarity method; use 'cosine', 'pearson'"

        # Retrieve all items and the target group's ratings
        all_items = self.get_all_items()
        target_ratings = self.get_group_ratings(target_group_id)

        # Retrieve all groups except the target group
        all_groups = [g for g in self.get_all_groups() if g != target_group_id]

        predicted_ratings = {}

        for item in all_items:
            # Skip items already rated by the target group
            if item in target_ratings:
                continue

            # USER-BASED COLLABORATIVE FILTERING
            user_based_score = 0
            user_similarity_sum = 0
            if top_k_users is not None:
                # Compute similarities and take top-k
                similarities = [
                    (group, self.group_ratings_similarity(target_group_id, group, method=similarity))
                    for group in all_groups
                ]
                top_k_user_groups = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k_users]
            else:
                # Use all groups
                top_k_user_groups = [
                    (group, self.group_ratings_similarity(target_group_id, group, method=similarity))
                    for group in all_groups
                ]

            for group, similarity_value in top_k_user_groups:
                group_ratings = self.get_group_ratings(group)
                if item in group_ratings:
                    user_based_score += similarity_value * group_ratings[item][0]
                    user_similarity_sum += similarity_value

            user_based_prediction = (
                user_based_score / user_similarity_sum if user_similarity_sum > 0 else 0
            )

            # ITEM-BASED COLLABORATIVE FILTERING
            item_based_score = 0
            item_similarity_sum = 0
            if top_k_items is not None:
                # Compute similarities and take top-k
                similarities = [
                    (rated_item, self.item_similarity(item, rated_item, method=similarity))
                    for rated_item in target_ratings.keys()
                ]
                top_k_similar_items = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k_items]
            else:
                # Use all rated items
                top_k_similar_items = [
                    (rated_item, self.item_similarity(item, rated_item, method=similarity))
                    for rated_item in target_ratings.keys()
                ]

            for rated_item, similarity_value in top_k_similar_items:
                rating = target_ratings[rated_item][0]
                item_based_score += similarity_value * rating
                item_similarity_sum += similarity_value

            item_based_prediction = (
                item_based_score / item_similarity_sum if item_similarity_sum > 0 else 0
            )

            # Combine user-based and item-based predictions
            predicted_rating = (
                alpha * user_based_prediction + (1 - alpha) * item_based_prediction
            )
            predicted_ratings[item] = predicted_rating

        # Sort items by predicted ratings in descending order
        sorted_items = sorted(predicted_ratings.keys(), key=lambda x: predicted_ratings[x], reverse=True)

        return sorted_items
