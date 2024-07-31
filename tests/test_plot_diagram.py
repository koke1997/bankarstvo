import pytest
from core.plot_diagram import (
    plot_routes_diagram,
    extract_routes_from_file,
    extract_all_routes,
    plot_detailed_routes_diagram,
)


def test_extract_routes_from_file():
    # Create a temporary file with some routes
    with open("temp_routes.py", "w") as f:
        f.write(
            """
@account_routes.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    pass

@account_routes.route('/create_account', methods=['GET', 'POST'])
def create_account():
    pass
        """
        )

    routes = extract_routes_from_file("temp_routes.py")
    assert len(routes) == 2
    assert routes[0] == "@account_routes.route('/dashboard', methods=['GET', 'POST'])"
    assert routes[1] == "@account_routes.route('/create_account', methods=['GET', 'POST'])"


def test_extract_all_routes(monkeypatch):
    def mock_extract_routes_from_file(file_path):
        if file_path == "routes/account_routes.py":
            return [
                "@account_routes.route('/dashboard', methods=['GET', 'POST'])",
                "@account_routes.route('/create_account', methods=['GET', 'POST'])",
            ]
        return []

    monkeypatch.setattr("core.plot_diagram.extract_routes_from_file", mock_extract_routes_from_file)

    extracted_routes = extract_all_routes()
    assert len(extracted_routes) == 3
    assert len(extracted_routes["account_routes.py"]) == 2


def test_plot_routes_diagram():
    extracted_routes = {
        "account_routes.py": [
            "@account_routes.route('/dashboard', methods=['GET', 'POST'])",
            "@account_routes.route('/create_account', methods=['GET', 'POST'])",
        ]
    }
    plot_routes_diagram(extracted_routes)
    # No assertion needed, just ensure no exceptions are raised


def test_plot_detailed_routes_diagram():
    extracted_routes = {
        "account_routes.py": [
            "@account_routes.route('/dashboard', methods=['GET', 'POST'])",
            "@account_routes.route('/create_account', methods=['GET', 'POST'])",
        ]
    }
    plot_detailed_routes_diagram(extracted_routes)
    # No assertion needed, just ensure no exceptions are raised
    assert True  # Ensure the function runs without errors


def test_extract_routes_from_file_no_routes():
    # Create a temporary file with no routes
    with open("temp_no_routes.py", "w") as f:
        f.write(
            """
def no_routes():
    pass
        """
        )

    routes = extract_routes_from_file("temp_no_routes.py")
    assert len(routes) == 0


def test_extract_all_routes_empty(monkeypatch):
    def mock_extract_routes_from_file(file_path):
        return []

    monkeypatch.setattr("core.plot_diagram.extract_routes_from_file", mock_extract_routes_from_file)

    extracted_routes = extract_all_routes()
    assert len(extracted_routes) == 0


def test_plot_routes_diagram_empty():
    extracted_routes = {}
    plot_routes_diagram(extracted_routes)
    # No assertion needed, just ensure no exceptions are raised


def test_plot_detailed_routes_diagram_empty():
    extracted_routes = {}
    plot_detailed_routes_diagram(extracted_routes)
    # No assertion needed, just ensure no exceptions are raised
    assert True  # Ensure the function runs without errors


def test_extract_routes_from_file_no_routes():
    # Create a temporary file with no routes
    with open("temp_no_routes.py", "w") as f:
        f.write(
            """
def no_routes():
    pass
        """
        )

    routes = extract_routes_from_file("temp_no_routes.py")
    assert len(routes) == 0


def test_extract_all_routes_empty(monkeypatch):
    def mock_extract_routes_from_file(file_path):
        return []

    monkeypatch.setattr("core.plot_diagram.extract_routes_from_file", mock_extract_routes_from_file)

    extracted_routes = extract_all_routes()
    assert len(extracted_routes) == 0


def test_plot_routes_diagram_empty():
    extracted_routes = {}
    plot_routes_diagram(extracted_routes)
    # No assertion needed, just ensure no exceptions are raised


def test_plot_detailed_routes_diagram_empty():
    extracted_routes = {}
    plot_detailed_routes_diagram(extracted_routes)
    # No assertion needed, just ensure no exceptions are raised
    assert True  # Ensure the function runs without errors
