from pymongo import MongoClient

import os

from dotenv import load_dotenv
from datetime import date

from user import User

load_dotenv()

uri = os.getenv('MONGO_DB_CONNECTION_STRING')
client = MongoClient(uri)
db = client['movie_wizard']

class DBHandler:
    def __init__(self) -> None:
        self.user_collection = db['users']

    def create_or_update_user(self, user: User) -> None:
        """
        Create or update a User document in the MongoDB collection without
        overwriting the discovered list on updates.
        
        :param user: An instance of the User class.
        """
        user_data = {
            'user_id': user.user_id,
            'with_genres': user.with_genres,
            'with_cast': user.with_cast,
            'runtime_gte': user.runtime_gte,
            'runtime_lte': user.runtime_lte,
            'vote_gte': user.vote_gte,
            'release_date_gte': user.release_date_gte.strftime("%Y-%m-%d"),
            'language': user.language,
            'include_adult': user.include_adult,
            'region': user.region
            # Removed 'discovered' from here to avoid overwriting it during updates
        }
        
        if self.user_collection.find_one({'user_id': user.user_id}):
            # Update the user document except for the 'discovered' field
            update_data = {key: value for key, value in user_data.items() if key != 'discovered'}
            self.user_collection.update_one({'user_id': user.user_id}, {'$set': update_data})
        else:
            # Insert new user and initialize 'discovered' as an empty list
            user_data['discovered'] = []
            self.user_collection.insert_one(user_data)
            
    def get_user_by_id(self, user_id: int):
        """
        Retrieve a user document by user_id.
        
        :param user_id: The ID of the user to retrieve.
        :return: User document or None if not found.
        """
        return self.user_collection.find_one({'user_id': user_id})
    
    def update_user_discovered_list(self, user_id: int, movie_id: int) -> None:
        """
        Update the discovered list of a user by adding a new movie ID.
        
        :param user_id: The ID of the user to update.
        :param movie_id: The ID of the movie to add to the discovered list.
        """
        self.user_collection.update_one(
            {'user_id': user_id},
            {'$addToSet': {'discovered': movie_id}}  # Use $addToSet to avoid duplicates
        )

    def clear_user_discovered_list(self, user_id: int) -> None:
        """
        Empty the discovered list of a user.
        
        :param user_id: The ID of the user whose discovered list should be cleared.
        """
        self.user_collection.update_one(
            {'user_id': user_id},
            {'$set': {'discovered': []}}  # Set the discovered list to an empty list
        )
    
    def get_user_discovered_list(self, user_id: int) -> list:
        """
        Retrieve the discovered list of a user.
        
        :param user_id: The ID of the user whose discovered list should be retrieved.
        :return: The list of movie IDs in the discovered list.
        """
        user = self.user_collection.find_one({'user_id': user_id})
        if user:
            return user['discovered']
        else:
            return []

# Example usage:
# Load or create your User instance here
# user_instance = User(...)
# db_handler = DBHandler()
# db_handler.create_or_update_user(user_instance)
# ...