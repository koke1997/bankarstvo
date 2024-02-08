# websocket_server.py
import asyncio
import websockets
import json
import pika
from flask import session
from DatabaseHandling.connection import get_db_cursor

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='transactions')

def callback(ch, method, properties, body):
    user_id = session['user_id']  # Get the user_id from the session
    cursor = get_db_cursor()
    cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (user_id,))
    balance = cursor.fetchone()[0]
    cursor.execute("SELECT transaction_id, amount FROM transactions WHERE from_account_id = %s ORDER BY transaction_id DESC", (user_id,))
    transactions = cursor.fetchall()
    data = {"balance": balance, "transactions": [{"id": id, "amount": amount} for id, amount in transactions]}
    await websocket.send(json.dumps(data))

channel.basic_consume(queue='transactions', on_message_callback=callback, auto_ack=True)

async def send_updates(websocket, path):
    channel.start_consuming()

start_server = websockets.serve(send_updates, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()