from DatabaseHandling.connection import connect_db
from core.models import Account, User


def get_user_balance(email):
    # Join Account and User, filter by User.email
    account = Account.query.join(User, Account.user_id == User.user_id).filter(User.email == email).first()
    return float(account.balance) if account else None


def check_balance(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    query = "SELECT balance FROM accounts WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()

    if result:
        return float(result[0])  # Return balance
    return None
