# bankarstvo


app.py

Framework: Python
Type: General Script
Summary: Sets up and runs the Flask application using create_app from app_factory.py.
app_factory.py

Framework: Flask
Type: Class/Function Definitions
Summary: Defines create_app to set up the Flask app with configurations, routes, and extensions.
extensions.py

Framework: Flask
Type: Class/Function Definitions
Summary: Initializes Flask extensions like SQLAlchemy, Bcrypt, and LoginManager, and integrates them with the app.
models.py

Framework: Flask
Type: Class/Function Definitions
Summary: Defines data models using SQLAlchemy, including a User model with login functionality.
validation_utils.py

Framework: Python
Type: Class/Function Definitions
Summary: Contains functions for validating currencies against the database using custom queries.
Directories
DatabaseHandling

Contents: Modules for database interactions, including balance checking, connection management, login, and registration.
FiatHandling

Contents: Modules related to fiat currency operations like account details, statement, deposits, transfers, notifications, and withdrawals.
routes

Contents: Flask route modules for user, account, and transaction handling.
templates

Contents: HTML templates for various user interfaces like dashboard, deposit, login, account management, registration, transaction history, transfer, and withdrawal.