import telebot
from telebot import types

from movie_wizard import MovieWizard
from user import User

from datetime import date
import re

from dotenv import load_dotenv
import os
import time

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN, parse_mode=None)

GENRES = [
    {'id': 28, 'name': 'Action'}, {'id': 12, 'name': 'Adventure'}, 
    {'id': 16, 'name': 'Animation'}, {'id': 35, 'name': 'Comedy'}, 
    {'id': 80, 'name': 'Crime'}, {'id': 99, 'name': 'Documentary'}, 
    {'id': 18, 'name': 'Drama'}, {'id': 10751, 'name': 'Family'}, 
    {'id': 14, 'name': 'Fantasy'}, {'id': 36, 'name': 'History'}, 
    {'id': 27, 'name': 'Horror'}, {'id': 10402, 'name': 'Music'}, 
    {'id': 9648, 'name': 'Mystery'}, {'id': 10749, 'name': 'Romance'}, 
    {'id': 878, 'name': 'Science Fiction'}, {'id': 10770, 'name': 'TV Movie'}, 
    {'id': 53, 'name': 'Thriller'}, {'id': 10752, 'name': 'War'}, 
    {'id': 37, 'name': 'Western'}
]

DURATIONS = {
    "<90 mins": (60, 90),
    "<120 mins": (60, 120),
    "<150 mins": (60, 150),
    "No limit": (60, 400)  # Use None to indicate no upper limit
}

RATINGS = [str(i) for i in range(5, 11)]  # Ratings from 5 to 10

ADULT_CONTENT = ["Yes", "No"]

user_preferences = {}

@bot.message_handler(commands=['start'])
def start_preferences(message):
    user_id = message.from_user.id
    user = MovieWizard().get_user_by_id(user_id)
    if user:
        bot.send_message(message.chat.id, f"Hello! You have already set your preferences. You can check or change them using /preferences command.")
    else:
        user_preferences[user_id] = {'with_genres': []}
        bot.send_message(message.chat.id, "Hello! I am Movie Wizard, who will be suggesting you movies to watch. To begin, please set your preference settings:")
        time.sleep(1)
        bot.send_message(message.chat.id, "Select your favorite genres (you can choose multiple, then press Done when finished):", reply_markup=generate_markup(GENRES, "genre", 4))

@bot.message_handler(commands=['help'])
def send_help(message):
    text = "Hi! I'm Movie Wizard, a bot that helps you find movies based on your preferences.\n\n"
    text += "Available commands:\n"
    text += "/start - set up your Movie Wizard\n"
    text += "/generate - generate a new movie based on your current preferences\n"
    text += "/preferences - check or change your preferences\n"
    text += "/clear - clear all the already discovered movies\n"
    text += "/help - display this message\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['preferences'])
def get_user_preferences(message):
    bot.send_message(message.chat.id, "This feature is being developed. Please, try again later.")
    # user_id = message.from_user.id
    # user = MovieWizard().get_user_by_id(user_id)
    # if user:
    #     text = f"Your current preferences:\n\n"
    #     text += "Genres: " + ", ".join([genre['name'] for genre in user['with_genres']]) + "\n"
    #     text += "Duration: " + DURATIONS.get((user['runtime_gte'], user['runtime_lte']), 'No limit')[0] + "\n"
    #     text += "Rating: " + str(user['vote_gte']) + "\n"
    #     text += "Release Date: " + str(user['release_date_gte']) + "\n"
    #     text += "Include Adult Content: " + user['include_adult'] + "\n\n"
    #     text += "Would you like to change your preferences?\n\n"
    #     text += "Yes / No"
    #     markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    #     markup.add(*[types.KeyboardButton(button) for button in ADULT_CONTENT])
    #     bot.send_message(message.chat.id, text, reply_markup=markup)
    # else:
    #     bot.send_message(message.chat.id, "You have not set your preferences yet. Start with /start command.")


@bot.message_handler(commands=['generate'])
def generate_movie(message):
    user_id = message.from_user.id

    if not MovieWizard().get_user_by_id(user_id):
        bot.send_message(message.chat.id, "You have not set your preferences yet. Start with /start command.")
        return

    movie_wizard = MovieWizard()
    movie_wizard.setup_wizard(user_id)

    movie_suggestion = movie_wizard.get_movie()

    if not movie_suggestion:
        bot.send_message(message.chat.id, "No movies found with your preferences. Please, adjust them.")
        return

    if isinstance(movie_suggestion, tuple):
        bot.send_photo(user_id, movie_suggestion[1], caption=movie_suggestion[0])
    else:
        bot.send_message(user_id, movie_suggestion)

@bot.message_handler(commands=['clear'])
def clear_discovered_movies(message):
    user_id = message.from_user.id
    MovieWizard().clear_user_discovered_list(user_id)
    bot.send_message(user_id, "Discovered movies list has been cleared.")

@bot.message_handler(commands=['discovered'])
def get_discovered_movies(message):
    user_id = message.from_user.id
    user = MovieWizard().get_user_discovered_list(user_id)
    if user:
        bot.send_message(user_id, "Discovered movies:\n" + "\n".join([movie['title'] for movie in user['discovered']]))
    else:
        bot.send_message(user_id, "You have not set your preferences yet. Start with /start command.")

def generate_markup(options, callback_prefix="", max_row_width=4):
    markup = types.InlineKeyboardMarkup()
    for i in range(0, len(options), max_row_width):
        row = [types.InlineKeyboardButton(text=option if isinstance(option, str) else option['name'],
                                          callback_data=f"{callback_prefix}:{option if isinstance(option, str) else option['id']}")
               for option in options[i:i+max_row_width]]
        markup.row(*row)
    if callback_prefix == "genre":
        markup.row(types.InlineKeyboardButton(text="Done", callback_data=f"{callback_prefix}:done"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith("genre:"))
def genre_selection(call):
    user_id = call.from_user.id
    data = call.data.split("genre:")[1]

    if data == "done":
        if not user_preferences[user_id]['with_genres']:
            bot.answer_callback_query(call.id, "Please select at least one genre before proceeding.")
            return
        bot.answer_callback_query(call.id, "Genre selection completed.")
        ask_duration_preference(call.message)
    else:
        # Add selected genre to user preferences
        selected_genre_id = int(data)
        if selected_genre_id not in user_preferences[user_id]['with_genres']:
            user_preferences[user_id]['with_genres'].append(selected_genre_id)
            bot.answer_callback_query(call.id, "Genre added to your preferences.")
        else:
            bot.answer_callback_query(call.id, "This genre was already selected.")

def ask_duration_preference(message):
    user_id = message.from_user.id
    duration_options = list(DURATIONS.keys())  # Convert the dictionary keys to a list for display
    markup = generate_markup(duration_options, "duration", 2)
    bot.send_message(message.chat.id, "How long do you prefer your movies to be?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("duration:"))
def duration_selection(call):
    user_id = call.from_user.id
    duration_key = call.data.split("duration:")[1]
    user_preferences[user_id]['preferred_duration'] = DURATIONS[duration_key]
    bot.answer_callback_query(call.id, f"Duration preference saved: {duration_key}")
    ask_rating_preference(call.message)  # Proceed to ask for rating preference

def ask_rating_preference(message):
    user_id = message.from_user.id
    markup = generate_markup(RATINGS, "rating", 3)
    bot.send_message(message.chat.id, "What is your preferred least rating?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("rating:"))
def rating_selection(call):
    user_id = call.from_user.id
    rating = call.data.split("rating:")[1]
    user_preferences[user_id]['preferred_rating'] = rating
    bot.answer_callback_query(call.id, f"Rating preference saved: {rating}")
    ask_adult_content_preference(call.message)

def ask_adult_content_preference(message):
    user_id = message.from_user.id
    markup = generate_markup(ADULT_CONTENT, "adult", 2)
    bot.send_message(message.chat.id, "Include adult content?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("adult:"))
def adult_content_selection(call):
    user_id = call.from_user.id
    adult_content = call.data.split("adult:")[1]
    user_preferences[user_id]['include_adult'] = adult_content == "Yes"
    bot.answer_callback_query(call.id, "Preference saved.")
    bot.send_message(call.message.chat.id, "Enter the earliest release date you are interested in (YYYY-mm-dd):")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def release_date_selection(message):
    user_id = message.from_user.id
    # Regex to match YYYY-mm-dd format
    if re.match(r'\d{4}-\d{2}-\d{2}', message.text):
        user_preferences[user_id]['earliest_release_date'] = message.text
        confirm_preferences(message)
    else:
        bot.send_message(message.chat.id, "Please enter the date in YYYY-mm-dd format.")

def confirm_preferences(message):
    user_id = message.from_user.id
    preferences_summary = "Your preferences:\n" + "\n".join([f"{key}: {value}" for key, value in user_preferences[user_id].items()])
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Confirm", callback_data="confirm"))
    markup.add(types.InlineKeyboardButton(text="Start Over", callback_data="start_over"))
    bot.send_message(message.chat.id, preferences_summary, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "confirm")
def preferences_confirmed(call):
    user_id = call.from_user.id
    prefs = user_preferences[user_id]
    
    # print(prefs['include_adult'])

    # Transform preferences into User object
    user = User(
        user_id=user_id,
        with_genres=prefs['with_genres'],
        with_cast=[],  # Assuming empty for simplicity, adjust as needed
        runtime_gte=prefs['preferred_duration'][0],
        runtime_lte=prefs['preferred_duration'][1],
        vote_gte=float(prefs['preferred_rating']),
        release_date_gte=date.fromisoformat(prefs['earliest_release_date']),
        language='en',  # Assuming 'en', adjust as needed
        include_adult=prefs['include_adult'] == "Yes",
        region=''  # Assuming empty for simplicity, adjust as needed
    )
    
    # Initialize MovieWizard and update user preferences in DB
    movie_wizard = MovieWizard()
    movie_wizard.setup_wizard()
    movie_wizard.create_or_update_user(user)

    bot.answer_callback_query(call.id, "Preferences confirmed. Your preferences have been saved.")
    
    # Now you can suggest a movie based on the preferences
    movie_suggestion = movie_wizard.get_movie()
    if isinstance(movie_suggestion, tuple):
        bot.send_photo(user_id, movie_suggestion[1], caption=movie_suggestion[0])
    else:
        bot.send_message(user_id, movie_suggestion)

@bot.callback_query_handler(func=lambda call: call.data == "start_over")
def start_over(call):
    start_preferences(call.message)

# Start polling
bot.infinity_polling()