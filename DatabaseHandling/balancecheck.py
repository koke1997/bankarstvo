from app_factory import db
from core.models import User


def get_user_balance(email):
    user = User.query.filter_by(email=email).first()
    return user.balance if user else None


def check_balance(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    query = "SELECT balance FROM Accounts WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()

    if result:
        return result[0]  # Return balance
    return None
