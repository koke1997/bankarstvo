import unittest
import sys
import os
import jwt
from unittest.mock import patch
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy

# Adjust the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from DatabaseHandling.authentication import login_func
from app_factory import create_app


class TestLogin(unittest.TestCase):
    def setUp(self):
        # Create a test app
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create a test client
        self.client = self.app.test_client()

        # Set up the database
        self.db = SQLAlchemy()
        self.db.init_app(self.app)
        with self.app.app_context():
            self.db.create_all()

    def tearDown(self):
        # Tear down the database
        with self.app.app_context():
            self.db.session.remove()
            self.db.drop_all()

        # Pop the application context
        self.app_context.pop()

    def test_successful_login(self):
        # Simulate a request using the test client
        with self.client:
            response = self.client.post(
                "/login", data={"username": "kokelej123456", "password": "123"}
            )
            self.assertTrue(login_func("kokelej123456", "123"))
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Logged in successfully!", response.data)

    def test_login_failure_incorrect_credentials(self):
        # Simulate a request using the test client
        with self.client:
            response = self.client.post(
                "/login", data={"username": "test_user", "password": "wrong_password"}
            )
            self.assertFalse(login_func("test_user", "wrong_password"))

    def test_login_nonexistent_user(self):
        # Simulate a request using the test client
        with self.client:
            response = self.client.post(
                "/login", data={"username": "nonexistent_user", "password": "any_password"}
            )
            self.assertFalse(login_func("nonexistent_user", "any_password"))


class TestOIDCIntegration:
    def setup_method(self):
        self.app = create_app()
        self.client = self.app.test_client()

    @patch("utils.extensions.requests.get")
    def test_token_validation_success(self, mock_get):
        # Mock Keycloak public key response
        mock_get.return_value.json.return_value = {
            "keys": [
                {"x5c": ["mocked-public-key"]}
            ]
        }

        # Mock a valid JWT token
        valid_token = jwt.encode(
            {"aud": os.getenv("KEYCLOAK_RESOURCE"), "iss": f"{os.getenv('KEYCLOAK_AUTH_SERVER_URL')}/realms/{os.getenv('KEYCLOAK_REALM')}"},
            "mocked-public-key",
            algorithm="RS256"
        )

        headers = {"Authorization": f"Bearer {valid_token}"}
        response = self.client.get(url_for("user_routes.register"), headers=headers)
        assert response.status_code == 200

    def test_logout_flow(self):
        # Simulate a logout request
        response = self.client.get(url_for("user_routes.logout"))
        assert response.status_code == 302  # Redirect to login
        assert url_for("user_routes.login") in response.location


if __name__ == "__main__":
    unittest.main()
