# Bertram Coffee Application Documentation

---

## Overview

**Bertram Coffee Application** is a full-stack Flask web application designed to automate and fairly distribute the responsibility of paying for coffee rounds among a group of users. This is achieved using a rotation based on who has spent the least overall — a form of equitable contribution tracking. Users register with a favorite coffee, and each round includes everyone's preference. The designated payer is dynamically selected and logged.
---

## Assumptions
- Each user sets a favorite coffee during registration.
- Coffee rounds are paid by the user who has spent the least overall.
- Users must be registered to be included in a round.
- Initial test users may be pre-populated in `users.json` for demo purposes.

---

## Key Features

- **Secure User Authentication** — Users register and log in with hashed passwords using **Argon2**, a modern cryptographic algorithm recommended for secure password storage.
- **Session Hardening** — Application sessions are secured with cookie-based flags for secure, cross-site-safe usage.
- **Round-Robin Payer Rotation** — The system dynamically calculates and selects the user who has spent the least to pay for the next round.
- **Favorite Coffee Tracking** — Each user selects a favorite coffee upon registration, which is automatically used in the round cost calculation.
- **JSON-Based Storage** — Data is persisted using `users.json`, `history.json`, and `coffee.json`, removing the need for an external database.
- **Responsive Interface** — HTML templates are styled with modern and clean design principles to create a smooth user experience.

---

## Security Features

### Password Storage
- Utilizes **Flask-Argon2** to securely hash user passwords during registration.
- On login, hashes are validated against user input using secure comparison.

### Session Security
The following session security measures are configured:
- `SESSION_COOKIE_HTTPONLY=True`: Prevents JavaScript from accessing session cookies.
- `SESSION_COOKIE_SECURE=True`: Ensures cookies are only sent over HTTPS.
- `SESSION_COOKIE_SAMESITE='Lax'`: Prevents CSRF in many cases by restricting cross-site cookie usage.

### CSRF Protection
- Integrated with `Flask-WTF` forms to prevent cross-site request forgery via hidden CSRF tokens.

---

## Project Structure

```plaintext
BertramTakeHome/
├── app.py                  # Entry point of the application
├── app/
│   ├── __init__.py         # Application factory & config
│   ├── models.py           # User class with Flask-Login integration
│   ├── views.py            # All route definitions & logic
│   ├── utils.py            # Reusable helpers for file I/O and business logic
│   ├── forms.py            # WTForms for registration validation
│   └── data/
│       ├── coffee.json     # Available coffees and prices
│       ├── history.json    # Purchase and round history
│       └── users.json      # User account info & preferences
├── static/
│   └── styles.css          # Custom styles
├── templates/
│   ├── base.html           # Layout template
│   ├── index.html          # Home page with round payer & summary
│   ├── login.html          # Login form
│   └── register.html       # Registration form with validation
└── requirements.txt        # Python dependencies
```

## Setup Instructions

This section outlines how to install and run the Bertram Coffee Application locally.

### Requirements

- Python 3.9 or higher
- `pip` (Python package manager)

### Installation Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/tuesdayfig/Bertram-CoffeeApp.git
   cd Bertram-CoffeeApp
   ```

2. **Install required dependencies**

    ```pip install -r requirements.txt```

3. **Running the application**
    - To start the app locally in development mode:
    ```python app.py```
    - Once running, open your browser and navigate to:
    ```http://127.0.0.1:5000```
