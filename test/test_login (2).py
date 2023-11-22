import unittest
import sys
import os

# Adjust the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from DatabaseHandling.login import login_func
from app import create_app
from flask import Flask

class TestLogin(unittest.TestCase):
    def setUp(self):
        # Create a test app
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create a test client
        self.client = self.app.test_client()

    def tearDown(self):
        # Pop the application context
        self.app_context.pop()

    def test_successful_login(self):
        # Simulate a request using the test client
        with self.client:
            response = self.client.post('/login', data={'username': 'kokelej123456', 'password': '123'})
            self.assertTrue(login_func('kokelej123456', '123'))

        # You can also check the response here if needed

    def test_login_failure_incorrect_credentials(self):
        # Simulate a request using the test client
        with self.client:
            response = self.client.post('/login', data={'username': 'test_user', 'password': 'wrong_password'})
            self.assertFalse(login_func('test_user', 'wrong_password'))

    def test_login_nonexistent_user(self):
        # Simulate a request using the test client
        with self.client:
            response = self.client.post('/login', data={'username': 'nonexistent_user', 'password': 'any_password'})
            self.assertFalse(login_func('nonexistent_user', 'any_password'))

if __name__ == '__main__':
    unittest.main()
