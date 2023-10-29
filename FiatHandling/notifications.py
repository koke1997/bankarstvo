from DatabaseHandling.connection import get_db_connection

def check_notifications(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    notification_query = """SELECT transaction_type, transaction_date 
                            FROM Transactions WHERE from_account_id = %s 
                            AND transaction_date > NOW() - INTERVAL 1 DAY"""
    cursor.execute(notification_query, (user_id,))
    recent_transactions = cursor.fetchall()

    cursor.close()
    connection.close()

    notifications = []
    for transaction in recent_transactions:
        notifications.append(f"Recent {transaction[0]} on {transaction[1]}")

    return notifications
