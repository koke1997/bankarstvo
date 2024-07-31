from DatabaseHandling.connection import connect_db, get_db_cursor


def validate_currency(currency_code):
    """Validates that the given currency_code exists in the database."""
    db = connect_db()
    cursor = get_db_cursor(db)

    try:
        query = "SELECT COUNT(*) FROM currencies WHERE currency_code = %s"
        cursor.execute(query, (currency_code,))
        result = cursor.fetchone()

        return result[0] > 0
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()


def validate_account(account_id):
    """Validates that the given account_id exists in the database."""
    db = connect_db()
    cursor = get_db_cursor(db)

    try:
        query = "SELECT COUNT(*) FROM accounts WHERE account_id = %s"
        cursor.execute(query, (account_id,))
        result = cursor.fetchone()

        return result[0] > 0
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()
