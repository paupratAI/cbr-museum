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
    VALID_METHODS = ['cosine', 'pearson']

    def __init__(self, 
        ratings_range: list, db_path='../data/database.db', default_alpha: float = 0.5, default_gamma: float = 1, default_decay_factor: float = 1, default_method: str = 'cosine'
        ):
        """
        Initializes the collaborative filtering system by connecting to the database.

        Parameters
        ----------
        ratings_range : list
            The range of ratings that can be given (both inclusive).
        db_path : str
            Path to the SQLite database storing the ratings, default is '../data/database.db'.
        default_alpha : float
            Weight for combining user-based and item-based predictions, default is 0.5.
        default_gamma : float
            Weight for the sensitivity of individual item ratings to deviations in item matches when computing individual item ratings from a group's global rating, default is 1.
        default_decay_factor : float
            A factor controlling the decay of the old rating, default is 1 (no decay).
        default_method : str
            The similarity method to use for both group and item similarities, default is 'cosine'.
        """
        assert default_method in self.VALID_METHODS, f"Invalid method; use one of {self.VALID_METHODS}"
        assert 0 <= default_alpha <= 1, "Alpha must be between 0 and 1"
        assert 0 <= default_gamma <= 1, "Gamma must be between 0 and 1"
        assert 0 <= default_decay_factor <= 1, "Decay factor must be between 0 and 1"

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

        self.default_alpha = default_alpha
        self.default_gamma = default_gamma
        self.default_decay_factor = default_decay_factor
        self.default_method = default_method
        self.ratings_range = ratings_range

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

    def store_group_ratings(self, 
        group_id: int, 
        ordered_items: List[int], 
        ordered_items_matches: List[int], 
        visited_items_count: int, 
        global_rating: float,
        gamma: float | None = None,
        decay_factor: float | None = None
        ) -> None:
        """
        Stores the ratings of a group for a list of all items in the database.

        Parameters
        ----------
        group_id : int
            Unique identifier for the group.
        ordered_items : List[int]
            List of all items sorted by the number of matches (descending).
        ordered_items_matches : List[int]
            List of the number of matches for each item in ordered_items.
        visited_items_count : int
            Number of items visited by the group. Therefore, the first visited_items_count items from ordered_items are the visited items.
        global_rating : float
            The global rating given by the group for all items.
        gamma : float
            Controls how sensitive the individual item ratings are to deviations in item matches.
            - Lower values of gamma make the ratings more uniform (similar to the global rating).
            - Higher values of gamma make the ratings more sensitive to deviations, there fore more extreme compared to the global rating.
        """
        assert len(ordered_items) == len(ordered_items_matches), "Length of ordered_items and ordered_items_matches must match"
        assert visited_items_count <= len(ordered_items), "Visited items count must be less than or equal to the total number of items"
        assert (gamma is None) or (0 <= gamma <= 1), "Gamma must be between 0 and 1"
        assert (decay_factor is None) or (0 <= decay_factor <= 1), "Decay factor must be between 0 and 1"
        
        min_rating, max_rating = self.ratings_range
        assert min_rating <= global_rating <= max_rating, "Global rating must be within the specified ratings range"

        if gamma is None:
            gamma = self.default_gamma

        if decay_factor is None:
            decay_factor = self.default_decay_factor

        ordered_visited_items = ordered_items[:visited_items_count]
        ordered_visited_items_matches = ordered_items_matches[:visited_items_count]
        total_visited_matches = sum(ordered_visited_items_matches)

        for item_id, item_matches in zip(ordered_visited_items, ordered_visited_items_matches):
            item_ratio = item_matches / total_visited_matches if total_visited_matches > 0 else 0
            item_rating = global_rating + gamma * (item_ratio - 1/visited_items_count) #

            self.__store_rating(group_id=group_id, item_id=item_id, item_rating=item_rating, decay_factor=decay_factor)

    def __store_rating(self, group_id: int, item_id: int, item_rating: float, decay_factor: float | None = None) -> None:
        """
        Stores or updates a group's average rating and visit count for an item, 
        adjusting the weight of the old mean and giving slightly more importance 
        to the new rating.

        Parameters
        ----------
        group_id : int
            Unique identifier for the group.
        item_id : int
            Unique identifier for the item.
        item_rating : float
            The rating given to the item by the group on this visit.
        decay_factor : float
            A factor (0 <= decay_factor <= 1) controlling the decay of the old rating.
            - If decay_factor = 0, the old rating is completely replaced by the new rating.
            - If decay_factor = 1, the old rating is kept as it is to compute the new average rating, and the new added rating has no additional weight
            in the new average.
        """
        assert (decay_factor is None) or (0 <= decay_factor <= 1), "Decay factor must be between 0 and 1"

        if decay_factor is None:
            decay_factor = self.default_decay_factor

        # Check if there's an existing record
        existing = self.conn.execute('''
            SELECT rating, visit_count FROM ratings 
            WHERE group_id = ? AND item_id = ?
        ''', (group_id, item_id)).fetchone()

        if existing is None:
            # No existing record, insert a new one
            new_rating = item_rating
            new_visit_count = 1
        else:
            old_rating, old_visit_count = existing

            # Compute the new weighted average
            new_visit_count = old_visit_count + 1  # Keep the real visit count for record

            old_weight = (old_visit_count / new_visit_count) * decay_factor

            new_weight = 1 - old_weight
            
            new_rating = old_weight * old_rating + new_weight * item_rating

        # Update or insert the record in the database
        with self.conn:
            self.conn.execute('''
                INSERT INTO ratings (group_id, item_id, rating, visit_count)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(group_id, item_id) DO UPDATE SET 
                    rating=excluded.rating,
                    visit_count=excluded.visit_count;
            ''', (group_id, item_id, new_rating, new_visit_count))

    def clear_ratings(self) -> None:
        """
        Clears all ratings from the database.
        """
        with self.conn:
            self.conn.execute('DELETE FROM ratings')

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

    def group_similarity(self, group_id_a: int, group_id_b: int, method: str | None = None) -> float:
        """
        Computes the similarity between two groups based on their ratings of items.

        Parameters
        ----------
        group_id_a : int
            Identifier of the first group.
        group_id_b : int
            Identifier of the second group.
        method : str
            The similarity method to use.

        Returns
        -------
        float
            Similarity score between the groups based on their ratings.
        """
        assert method in self.VALID_METHODS, f"Invalid method; use one of {self.VALID_METHODS}"

        if method is None:
            method = self.default_method

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
            return (1 - cosine(ratings_a_vec, ratings_b_vec) + 1) / 2 # Cosine similarity scaled to [0, 1]
        elif method == 'pearson':
            # Pearson correlation
            if len(ratings_a_vec) < 2:  # Pearson requires at least 2 data points
                return 0
            return (pearsonr(ratings_a_vec, ratings_b_vec).correlation + 1) / 2  # Pearson correlation scaled to [0, 1]

    def item_similarity(self, item_id_a: int, item_id_b: int, method: str | None = None) -> float:
        """
        Computes the similarity between two items based on user ratings.

        Parameters
        ----------
        item_id_a : int
            Identifier of the first item.
        item_id_b : int
            Identifier of the second item.
        method : str
            The similarity method to use, default is 'cosine'.

        Returns
        -------
        float
            Similarity score between the items.
        """
        assert method in self.VALID_METHODS, f"Invalid method; use one of {self.VALID_METHODS}"

        if method is None:
            method = self.default_method

        ratings_a = self.get_item_ratings(item_id_a)
        ratings_b = self.get_item_ratings(item_id_b)

        common_groups = set(ratings_a.keys()) & set(ratings_b.keys())
        if not common_groups:
            return 0  # No groups in common

        ratings_a_vec = np.array([ratings_a[g][0] for g in common_groups])
        ratings_b_vec = np.array([ratings_b[g][0] for g in common_groups])

        if method == 'cosine':
            return (1 - cosine(ratings_a_vec, ratings_b_vec) + 1) / 2 # Cosine similarity scaled to [0, 1]
        elif method == 'pearson':
            return (pearsonr(ratings_a_vec, ratings_b_vec).correlation + 1) / 2  # Pearson correlation scaled to [0, 1]
    
    def recommend_items(
        self, target_group_id: int, method: str | None = None, alpha: float | None = None,
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
        method : str
            The similarity method to use for both group and item similarities.
        top_k_users : int, optional
            Number of most similar users to consider for user-based filtering. If None, all users are considered.
        top_k_items : int, optional
            Number of most similar items to consider for item-based filtering. If None, all items are considered.

        Returns
        -------
        List[int]
            Sorted list of item IDs by predicted relevance.
        """
        assert method in self.VALID_METHODS + [None], f"Invalid method; use one of {self.VALID_METHODS}"
        assert (alpha is None) or (0 <= alpha <= 1), "Alpha must be between 0 and 1"

        if method is None:
            method = self.default_method

        if alpha is None:
            alpha = self.default_alpha

        # Retrieve all items and the target group's ratings
        all_items = self.get_all_items()
        target_ratings = self.get_group_ratings(target_group_id)

        # Retrieve all groups except the target group
        all_groups = [g for g in self.get_all_groups() if g != target_group_id]

        user_based_predictions, item_based_predictions = {}, {}
        for item in all_items:
            # USER-BASED COLLABORATIVE FILTERING --------------------------------
            user_based_score = 0
            user_similarity_sum = 0

            group_similarities = sorted([
                (group, self.group_similarity(target_group_id, group, method=method))
                for group in all_groups
            ], key=lambda x: x[1], reverse=True)

            # Only consider the top-k most similar users
            if top_k_users is not None:
                group_similarities = group_similarities[:top_k_users]

            for similar_group, similar_item_similarity in group_similarities:
                group_ratings = self.get_group_ratings(similar_group)

                if item in group_ratings:
                    group_item_rating = group_ratings[item][0]

                    user_based_score += similar_item_similarity * group_item_rating
                    user_similarity_sum += similar_item_similarity

            user_based_prediction = (
                user_based_score / user_similarity_sum if user_similarity_sum > 0 else 0
            )

            user_based_predictions[item] = user_based_prediction

            # ITEM-BASED COLLABORATIVE FILTERING --------------------------------
            item_based_score = 0
            item_similarity_sum = 0

            item_similarities = sorted([
                (similar_item, self.item_similarity(item, similar_item, method=method))
                for similar_item in target_ratings.keys()
            ], key=lambda x: x[1], reverse=True)

            # Only consider the top-k most similar items
            if top_k_items is not None:
                item_similarities = item_similarities[:top_k_items]

            for similar_item, similar_item_similarity in item_similarities:
                target_rated_item_rating = target_ratings[similar_item][0]
                item_based_score += similar_item_similarity * target_rated_item_rating
                item_similarity_sum += similar_item_similarity

            item_based_prediction = (
                item_based_score / item_similarity_sum if item_similarity_sum > 0 else 0
            )

            item_based_predictions[item] = item_based_prediction

        # Scale to give the same importance to both predictions
        min_user_based_prediction, max_user_based_prediction = min(user_based_predictions.values()), max(user_based_predictions.values())
        scaled_user_based_predictions = {
            item: (user_based_predictions[item] - min_user_based_prediction) / (max_user_based_prediction - min_user_based_prediction)
            for item in all_items
        }

        min_item_based_prediction, max_item_based_prediction = min(item_based_predictions.values()), max(item_based_predictions.values())
        scaled_item_based_predictions = {
            item: (item_based_predictions[item] - min_item_based_prediction) / (max_item_based_prediction - min_item_based_prediction)
            for item in all_items
        }

        # Combine user-based and item-based predictions using alpha
        predicted_ratings = {
            item: alpha * scaled_user_based_predictions[item] + (1 - alpha) * scaled_item_based_predictions[item]
            for item in all_items
        }

        # Sort items by predicted ratings in descending order
        sorted_items = sorted(predicted_ratings.keys(), key=lambda x: predicted_ratings[x], reverse=True)

        print([round(float(predicted_ratings[item]), 4) for item in sorted_items])

        return sorted_items
