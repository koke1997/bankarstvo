# DatabaseHandling/session_clearing.py
from flask import session

def clear_session():
    session.clear()