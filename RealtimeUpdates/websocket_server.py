# websocket_server.py
import json
import pika
from flask import session
from flask_socketio import SocketIO, emit
from DatabaseHandling.connection import get_db_cursor

socketio = SocketIO()

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='transactions')

@socketio.on('connect')
def handle_connect():
    user_id = session['user_id']  # Get the user_id from the session
    cursor = get_db_cursor()
    cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (user_id,))
    balance = cursor.fetchone()[0]
    cursor.execute("SELECT transaction_id, amount FROM transactions WHERE from_account_id = %s ORDER BY transaction_id DESC", (user_id,))
    transactions = cursor.fetchall()
    data = {"balance": balance, "transactions": [{"id": id, "amount": amount} for id, amount in transactions]}
    emit('update', json.dumps(data))

def callback(ch, method, properties, body):
    user_id = session['user_id']  # Get the user_id from the session
    cursor = get_db_cursor()
    cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (user_id,))
    balance = cursor.fetchone()[0]
    cursor.execute("SELECT transaction_id, amount FROM transactions WHERE from_account_id = %s ORDER BY transaction_id DESC", (user_id,))
    transactions = cursor.fetchall()
    data = {"balance": balance, "transactions": [{"id": id, "amount": amount} for id, amount in transactions]}
    socketio.emit('update', json.dumps(data))

channel.basic_consume(queue='transactions', on_message_callback=callback, auto_ack=True)

def start_socketio_server(app):
    socketio.init_app(app)
    socketio.run(app)
