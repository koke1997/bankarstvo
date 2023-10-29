from flask import Flask
from models import db
from routes import bcrypt, configure_routes

app = Flask(__name__)
app.secret_key = 'some_secret_key'  # Used for flashing messages

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Mikrovela1!@localhost/banking_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Bind the app with db and bcrypt
db.init_app(app)
bcrypt.init_app(app)

# Configure the routes
configure_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
