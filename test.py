from datetime import date
from user import User  # Import the User class
from db import DBHandler  # Import the DBHandler class you've implemented

def main():
    # Create a DBHandler instance to interact with the database
    db_handler = DBHandler()

    # Example users to insert/update
    users = [
        User(
            user_id=1,
            with_genres=["action", "comedy"],
            with_cast=["actor_id_1", "actor_id_2"],
            runtime_gte=90,
            runtime_lte=120,
            vote_gte=7.0,
            release_date_gte=date(1990, 1, 1),
            language='en',
            include_adult=True,
            region='US'
        ),
        User(
            user_id=2,
            with_genres=["drama", "thriller"],
            with_cast=["actor_id_3", "actor_id_4"],
            runtime_gte=100,
            runtime_lte=150,
            vote_gte=8.0,
            release_date_gte=date(1985, 1, 1),
            language='en',
            include_adult=False,
            region='CA'
        )
    ]

    # Insert/update users in the database
    # for user in users:
    #     db_handler.create_or_update_user(user)
    #     print(f"User {user.user_id} inserted/updated.")
    
    print(db_handler.get_user_by_id(1))

if __name__ == "__main__":
    main()
