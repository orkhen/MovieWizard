from datetime import date

class User:
    def __init__(self, user_id: int, with_genres: list, with_cast: list, runtime_gte: int, runtime_lte: int, vote_gte: float = 7, release_date_gte: date = date(1990,1,1), language: str = 'en', include_adult: bool = True, region: str = '') -> None:
        self.user_id = user_id
        self.with_genres = with_genres
        self.release_date_gte = release_date_gte
        self.language = language
        self.include_adult = include_adult
        self.region = region
        self.with_cast = with_cast
        self.runtime_gte = runtime_gte
        self.runtime_lte = runtime_lte
        self.vote_gte = vote_gte
