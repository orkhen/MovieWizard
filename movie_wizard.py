from tmdbv3api import TMDb, Movie, Discover, Genre
from user import User
from db import DBHandler 

from datetime import date
import random

import json

from dotenv import load_dotenv
import os

class MovieWizard:
    def __init__(self) -> None:
        self.tmdb = None
        self.discover = None
        self.db = DBHandler()

        self.user_preferences = None
        self.discovered = None  # Stores IDs of discovered movies to avoid repetition

    def setup_wizard(self, user_id = None) -> None:
        load_dotenv()
        self.tmdb = TMDb()
        self.tmdb.api_key = os.getenv('TMDB_API_KEY')
        self.tmdb.language = 'en'
        self.discover = Discover()

        if user_id:
            self.set_user_preferences(user_id)
    
    def create_or_update_user(self, user: User) -> None:
        self.db.create_or_update_user(user)

        self.set_user_preferences(user.user_id)

    def set_user_preferences(self, user_id) -> None:
        self.user_preferences = self.db.get_user_by_id(user_id)
        self.discovered = self.user_preferences['discovered']
    
    def get_user_preferences(self, user_id) -> dict:
        self.set_user_preferences(user_id)

        with_genres = self.user_preferences['with_genres']
        translated_genres = self.translate_genres(with_genres, mode='name')

        self.user_preferences['with_genres'] = translated_genres

        return self.user_preferences

    def get_user_by_id(self, user_id) -> dict:
        return self.db.get_user_by_id(user_id)

    def translate_genres(self, genres, mode) -> list:
        all_genres = Genre().movie_list()
        translated_genres = []
        
        # Create a mapping of id to name and name to id for quick lookups
        id_to_name = {genre['id']: genre['name'] for genre in all_genres}
        name_to_id = {genre['name']: genre['id'] for genre in all_genres}

        if mode == "id":
            # Translate genre names to IDs
            for genre_name in genres:
                if genre_name in name_to_id:
                    translated_genres.append(name_to_id[genre_name])
                else:
                    raise ValueError(f"Genre name '{genre_name}' not found.")
        elif mode == "name":
            # Translate genre IDs to names
            for genre_id in genres:
                if genre_id in id_to_name:
                    translated_genres.append(id_to_name[genre_id])
                else:
                    raise ValueError(f"Genre ID '{genre_id}' not found.")
        else:
            raise ValueError("Invalid mode. Mode must be either 'id' or 'name'.")
        
        return translated_genres

    def translate_movies(self, movies, mode) -> list:
        translated_movies = []
        for movie in movies:
            translated_movies.append({
                'id': movie['id'],
                'title': movie['title'],
                'release_date': movie['release_date'],
                'vote_average': movie['vote_average'],
                'vote_count': movie['vote_count'],
                'popularity': movie['popularity']
            })
        return translated_movies
    def get_movie(self) -> str:
        filters = {
            'with_genres': ','.join(map(str, self.user_preferences['with_genres'])),
            # 'with_cast': ','.join(map(str, self.user_preferences.with_cast)),
            'primary_release_date.gte': self.user_preferences['release_date_gte'],
            'vote_average.gte': self.user_preferences['vote_gte'],
            'vote_count.gte': float(50),
            'with_runtime.gte': self.user_preferences['runtime_gte'],
            'with_runtime.lte': self.user_preferences['runtime_lte'],
            'include_adult': self.user_preferences['include_adult'],
            'language': self.user_preferences['language'],
            'region': self.user_preferences['region'],
            'sort_by': 'popularity.desc'
        }

        # Attempting up to 10 times to find a unique movie
        for _ in range(10):
            discovered_movie = random.choice(self.discover.discover_movies(filters))
            if discovered_movie.id not in self.discovered:
                # self.discovered.add(discovered_movie.id)
                movie_details = Movie().details(discovered_movie.id)
                # print(movie_details)
                movie_details_json = {
                    'title': movie_details.title,
                    'overview': movie_details.overview,
                    'release_date': movie_details.release_date.replace("-", "/"),
                    'vote_average': round(movie_details.vote_average, 1),
                    'genres': ', '.join([genre.name for genre in movie_details.genres]),
                    'cast': ', '.join([cast.name for cast in movie_details.casts.cast][:5]),
                    'runtime': movie_details.runtime,
                    'id': discovered_movie.id,
                    'poster_path': f'https://image.tmdb.org/t/p/original{discovered_movie.poster_path}'
                }
                
                self.db.update_user_discovered_list(self.user_preferences['user_id'], discovered_movie.id)

                return (self.format_response(movie_details_json), movie_details_json['poster_path'])
                
        return 'No movie found or no movies match the criteria. Please, try again later or update your preferences.'

    def update_user_discovered_list(self, user_id: int, movie_id: int) -> None:
        self.db.update_user_discovered_list(user_id, movie_id)

    def clear_user_discovered_list(self, user_id: int) -> None:
        self.db.clear_user_discovered_list(user_id)

    def get_user_discovered_list(self, user_id: int) -> list:
        return [Movie().details(movie_id).title for movie_id in self.db.get_user_discovered_list(user_id)]
    
    def format_response(self, movie_details_json) -> str:
        response = f"Title: {movie_details_json['title']}\n Overview: {movie_details_json['overview']}\n Release date: {movie_details_json['release_date']}\n Vote average: {movie_details_json['vote_average']}\n Genres: {movie_details_json['genres']}\n Cast: {movie_details_json['cast']}\n Runtime: {movie_details_json['runtime']} minutes\n"

        return response
    
m = MovieWizard()
print(m.get_user_preferences(1268370310))