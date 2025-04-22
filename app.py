import os
from app import create_app

#Get absolute paths for template and static directories
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

#Create the Flask app with correct template/static directories
app = create_app(template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

if __name__ == "__main__":
    app.run(debug=True)
