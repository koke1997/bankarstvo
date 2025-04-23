import pytest
from app_factory import create_app
from core.models import db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()
