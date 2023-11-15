import mysql.connector
from datetime import datetime
from DatabaseHandling.connection import connect_db

def connect_db():
    config = {
        'host': 'localhost',
        'user': 'banking_user',
        'password': 'secure_password_here',
        'database': 'banking_app'
    }
    connection = mysql.connector.connect(**config)
    return connection

def add_recurring_payment(from_user_id, to_account_id, amount, start_date, end_date, frequency):
    connection = connect_db()
    cursor = connection.cursor()

    insert_query = """INSERT INTO RecurringPayments (from_user_id, to_account_id, amount, start_date, end_date, frequency, status)
                     VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVE')"""
    cursor.execute(insert_query, (from_user_id, to_account_id, amount, start_date, end_date, frequency))

    connection.commit()
    cursor.close()
    connection.close()

def execute_recurring_payments():
    connection = connect_db()
    cursor = connection.cursor()

    # Get all active recurring payments that need execution
    today = datetime.today().date()
    select_query = """SELECT payment_id, from_user_id, to_account_id, amount, frequency, last_executed 
                     FROM RecurringPayments WHERE status = 'ACTIVE' AND start_date <= %s AND (end_date IS NULL OR end_date >= %s)"""
    cursor.execute(select_query, (today, today))
    payments = cursor.fetchall()

    for payment in payments:
        payment_id, from_user_id, to_account_id, amount, frequency, last_executed = payment
        should_execute = False

        if frequency == 'DAILY':
            should_execute = True
        elif frequency == 'WEEKLY' and (today - last_executed).days >= 7:
            should_execute = True
        elif frequency == 'MONTHLY' and today.month != last_executed.month:
            should_execute = True
        elif frequency == 'YEARLY' and today.year != last_executed.year:
            should_execute = True

        if should_execute:
            # Transfer the amount
            transfer_funds(from_user_id, to_account_id, amount)
            # Update last_executed
            update_query = "UPDATE RecurringPayments SET last_executed = %s WHERE payment_id = %s"
            cursor.execute(update_query, (today, payment_id))

    connection.commit()
    cursor.close()
    connection.close()
