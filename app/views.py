from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, login_required, logout_user, current_user
from app.models import User
from app.forms import RegistrationForm
from app.utils import (
    load_users, save_users, get_next_payer_based_on_least_spent,
    get_user_history, read_json, write_json, get_coffee_price, get_favorite_coffee_for_user
)
from datetime import datetime
from app import argon2

bp = Blueprint("main", __name__)

#Get spending total based on user_id
def get_spending_history(user_id):
    #Load in user history
    history = get_user_history(user_id)
    total_spent = 0

    for entry in history:
        timestamp = entry['timestamp']
        coffee_name = entry['coffee']
        user = entry['user']
        #Get price of coffee
        coffee_cost = get_coffee_price(coffee_name)
        total_spent += coffee_cost

    return total_spent

#Get spending totals
def get_user_spending_totals():
    #Load in history and coffee costs
    history = read_json("app/data/history.json", {})
    coffee_costs = read_json("app/data/coffee.json", {})
    #Load in users
    users = load_users()
    #Get user_spending for each user, otherwise default to 0.0
    user_spending = {user_id: 0.0 for user_id in users}
    
    #Iterate through history
    for user_id, purchases in history.items():
        #Iterate through entries
        for entry in purchases:
            coffee = entry["coffee"]
            #If user paid for round
            if coffee.lower() == "paid for round":
                #Get participants, if none, default to empty list
                participants = entry.get("participants", {})
                #Sum up the participants entries, otherwise default to 0.0
                round_total = sum(coffee_costs.get(fav, 0.0) for fav in participants.values())
                #Add in total to total user_spending
                user_spending[user_id] += round_total
            #If the user hasn't paid for round, add in coffee_costs to user_spending
            else:
                user_spending[user_id] += coffee_costs.get(coffee, 0.0)

    return user_spending

#Determine next buyer of coffee
def determine_next_payer():
    #Get totals
    user_spending = get_user_spending_totals()
    #Calculate the user that has spent the least and return that user
    return get_next_payer_based_on_least_spent(user_spending)

#Default route
@bp.route("/")
#Authentication required to access
@login_required
def index():
    #Read coffee costss
    coffee_costs = read_json("app/data/coffee.json", {})
    #Get current history based on currently logged in user
    user_history = get_user_history(current_user.id)
    #Get current spending based on current logged in user
    total_spent = get_spending_history(current_user.id)
    #Get user spending total
    user_spending = get_user_spending_totals()
    #Logic to determine next payer
    current_payer = determine_next_payer()
    #Load in users
    users = load_users()
    
    #Get participants
    participants = {
        #Get favorites
        user_id: data.get("favorite")
        #Get user_id and data from users
        for user_id, data in users.items()
        #Filter on users with only favorites
        if data.get("favorite")
    }
    #Sum up the cost of favorite coffees in participants
    round_cost = sum(get_coffee_price(fav) for fav in participants.values())
    
    #Render logic for index.html
    return render_template(
        "index.html",
        coffee_costs=coffee_costs,
        user_history=user_history,
        total_spent=total_spent,
        current_payer=current_payer,
        round_cost=round_cost,
        user_payments=user_spending,
        #Default to "least" spent
        payment_rule="least",
        current_user_favorite=get_favorite_coffee_for_user(current_user.id),
        users=users
    )

#Login page
@bp.route("/login", methods=["GET", "POST"])
def login():
    #If user authenticates, return to home
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    #If the user posts to the form
    if request.method == "POST":
        #Grab username and password
        username = request.form["username"]
        password = request.form["password"]
        #Load in users
        users = load_users()
        #Attempt to retrieve username for checking
        user = users.get(username)

        #If the user exists and password entered is the same as hashed password, attempt to login the user
        if user and argon2.check_password_hash(user["password"], password):
            #Get favorite and total_spentm otherwise default to 0.0
            login_user(User(username, user["password"], user.get("total_spent", 0.0), user.get("favorite")))
            return redirect(url_for("main.index"))
    
    #Otherwise, return to login page to attempt again
    return render_template("login.html")

#Registration page
@bp.route("/register", methods=["GET", "POST"])
def register():
    #Get coffee
    coffee_costs = read_json("app/data/coffee.json", {})
    #Load in registration form
    form = RegistrationForm()
    #List out available favoritese
    form.favorite.choices = [(coffee, f"{coffee} - ${price}") for coffee, price in coffee_costs.items()]

    #Validate form
    if form.validate_on_submit():
        #Get username, password, and favorite
        username = form.username.data
        password = form.password.data
        favorite = form.favorite.data
        #Load in users
        users = load_users()
        
        #If username is already taken, refresh the page for registration
        if username in users:
            return redirect(url_for("main.register"))

        #Otherwise, hash password for security
        hashed_password = argon2.generate_password_hash(password)
        
        #Load in new user with favorite, password, and total spend being 0.0
        users[username] = {
            "username": username,
            "password": hashed_password,
            "total_spent": 0.0,
            "favorite": favorite
        }
        #Save to users JSON
        save_users(users)
        #Login user with 0.0 total spend
        login_user(User(username, hashed_password, 0.0, favorite))
        return redirect(url_for("main.index"))

    #If form not valid, return to registration page
    return render_template("register.html", form=form)

#Logout page
@bp.route("/logout")
#Authentication required to access
@login_required
def logout():
    #Logout user
    logout_user()
    #Redirect to login page
    return redirect(url_for("main.login"))

#Route for round paid
@bp.route("/round_paid", methods=["POST"])
#Authentication required to access
@login_required
def round_paid():
    #Determine next payer
    current_payer = determine_next_payer()
    #Load in user
    users = load_users()
    #Get coffee costs and history
    coffee_costs = read_json("app/data/coffee.json", {})
    history = read_json("app/data/history.json", {})
    
    #Get participants
    participants = {
        #Get favorites
        user_id: data["favorite"]
        #Search for user_id and data in users
        for user_id, data in users.items()
        #If favorite found, get favorite
        if data.get("favorite")
    }
    
    #Total costs is summed up by favorites, otherwise default to 0.0
    total_cost = sum(coffee_costs.get(fav, 0.0) for fav in participants.values())
    
    #If current_payer is not history, init empty dict
    if current_payer not in history:
        history[current_payer] = []
        
    #Add in history for current_payer to keep track of costs
    history[current_payer].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "coffee": "paid for round",
        "user": current_payer,
        "participants": participants
    })

    #Add in total_costs to total_spent
    users[current_payer]["total_spent"] += total_cost
    #Write back to JSON
    write_json("app/data/history.json", history)
    #Save users
    save_users(users)

    #Return back home page
    return redirect(url_for("main.index"))
