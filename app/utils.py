import json
import os
from datetime import datetime

#File paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
COFFEE_FILE = os.path.join(DATA_DIR, "coffee.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

#JSON utilities
#Read given JSON
def read_json(path, default=None):
    #If file not found
    if not os.path.exists(path):
        return default
    #Otherwise load JSON
    with open(path, "r") as f:
        return json.load(f)

#Write to given JSON
def write_json(path, data):
    with open(path, "w") as f:
        #Pretty print
        json.dump(data, f, indent=2)

#User management
#Load in users
def load_users():
    return read_json(USERS_FILE, {})

#Save to users file
def save_users(users):
    write_json(USERS_FILE, users)

#Coffee & history utilities
#Get coffee prices by coffee_name
def get_coffee_price(coffee_name):
    coffee_prices = read_json(COFFEE_FILE, {})
    #Return coffee_price if found, otherwise return 0.0
    return coffee_prices.get(coffee_name, 0.0)

#Get user_history by user_id
def get_user_history(user_id):
    history = read_json(HISTORY_FILE, {})
    #Return history if found, otherwise return blank list
    return history.get(user_id, [])

#Get favorite coffee based on user_id
def get_favorite_coffee_for_user(user_id):
    #Load in users
    users = load_users()
    #Get the user based on user_id
    user = users.get(user_id)
    #Get favorite if found, otherwise return None
    return user.get("favorite") if user else None

#Set favorite coffee based on user_id
def set_favorite_coffee_for_user(user_id, favorite_coffee):
    #Load in users
    users = load_users()
    #If user_id is found in loaded users
    try:
        if user_id in users:
            #Grab favorite coffee
            users[user_id]["favorite"] = favorite_coffee
            #Save users again with favorite coffee
            save_users(users)
    except:
        print("An exception occurred")

#Round logic
#Get total spent by username
def get_user_total_spent(username):
    #Load in users
    users = load_users()
    #Get user by username
    user = users.get(username)
    #Get total spent if user is found, otherwise return 0.0
    return user.get("total_spent", 0.0) if user else 0.0

#Add entry to history
def add_history_entry(user_id, coffee):
    #Read history file
    history = read_json(HISTORY_FILE, {})
    #If user is not in history, init list
    if user_id not in history:
        history[user_id] = []

    #Add history based on user_id
    history[user_id].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "coffee": coffee,
        "user": user_id
    })
    #Write back to JSON
    write_json(HISTORY_FILE, history)

    #Load in users
    users = load_users()
    #If user_id is in users
    if user_id in users:
        #Get coffee price and add to total_spents
        users[user_id]["total_spent"] += get_coffee_price(coffee)
        #Save to users
        save_users(users)

#Payer selection logic
#Paid based on least amount spent
def get_next_payer_based_on_least_spent(user_spent):
    #If no user spent is found, return no data
    if not user_spent:
        return "No data"
    #Otherwise, find the minimum user_spent
    return min(user_spent, key=user_spent.get)

#Exportables
__all__ = [
    "load_users", "save_users", "read_json", "write_json",
    "get_user_total_spent", "get_coffee_price", "add_history_entry",
    "get_user_history", "get_next_payer_based_on_least_spent",
    "get_favorite_coffee_for_user",
    "set_favorite_coffee_for_user"
]
