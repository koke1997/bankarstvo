from DatabaseHandling.connection import connect_db


def get_account_details(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    details_query = "SELECT username, email, account_created, last_login FROM Users WHERE user_id = %s"
    cursor.execute(details_query, (user_id,))
    details = cursor.fetchone()

    cursor.close()
    connection.close()

    return details
