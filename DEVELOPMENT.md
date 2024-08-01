# Development Process Documentation

This document provides a comprehensive guide to the development process for the Banking Application project. It includes instructions for setting up the development environment, coding standards, and testing procedures.

## Setting Up the Development Environment

1. **Clone the Repository**
   ```sh
   git clone https://github.com/koke1997/bankarstvo
   ```

2. **Navigate to the Project Directory**
   ```sh
   cd bankarstvo
   ```

3. **Create and Activate Virtual Environment**
   This is strongly advised for further development, because dependencies can be easily added to the project.
   ```sh
   python -m virtualenv .
   ```

   - **For Windows (using Command Prompt):**
     ```sh
     .\Scripts\activate
     ```
   - **For Windows (using PowerShell):**
     ```sh
     .\Scripts\Activate.ps1
     ```
   - **For Unix or MacOS (using Bash):**
     ```sh
     source bin/activate
     ```

4. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

5. **Install Node.js Dependencies**
   ```sh
   npm install
   ```

6. **Build the Project**
   ```sh
   npm run build
   ```

7. **Set up MySQL Database**
   ```sh
   # Install MySQL Server
   sudo apt-get update
   sudo apt-get install mysql-server

   # Secure MySQL Installation
   sudo mysql_secure_installation

   # Log in to MySQL
   sudo mysql -u root -p

   # Create a new database
   CREATE DATABASE banking_app;

   # Create a new user and grant privileges
   CREATE USER 'ikokalovic'@'localhost' IDENTIFIED BY 'Mikrovela1!';
   GRANT ALL PRIVILEGES ON banking_app.* TO 'ikokalovic'@'localhost';
   FLUSH PRIVILEGES;
   ```

8. **Configure Environment Variables**
   ```sh
   # Create a .env file in the project root directory and add the following environment variables
   DATABASE_USER=ikokalovic
   DATABASE_PASSWORD=Mikrovela1!
   DATABASE_HOST=localhost
   DATABASE_PORT=3306
   DATABASE_NAME=banking_app
   ```

## Coding Standards

1. **Follow PEP 8**: Ensure that your Python code adheres to the PEP 8 style guide.
2. **Use Meaningful Names**: Use clear and descriptive names for variables, functions, and classes.
3. **Write Docstrings**: Include docstrings for all modules, classes, and functions to provide clear documentation.
4. **Keep Functions Small**: Break down large functions into smaller, more manageable pieces.
5. **Use Comments Wisely**: Add comments to explain complex logic, but avoid redundant comments.
6. **Consistent Indentation**: Use 4 spaces for indentation in Python code.
7. **Avoid Magic Numbers**: Use named constants instead of hardcoding numbers in your code.
8. **Handle Exceptions**: Use try-except blocks to handle exceptions and provide meaningful error messages.

## Testing Procedures

1. **Write Unit Tests**: Ensure that all new features and bug fixes are covered by unit tests.
2. **Use pytest**: Use the pytest framework for writing and running tests.
3. **Run Tests Locally**: Run tests locally before pushing your changes to the repository.
   ```sh
   pytest
   ```
4. **Continuous Integration**: The project includes GitHub Actions workflows for continuous integration. Ensure that your changes pass all CI checks.
5. **Test Coverage**: Aim for high test coverage to ensure the reliability of the codebase.
6. **Mock External Dependencies**: Use mocking to isolate the code being tested from external dependencies.

## Additional Guidelines

1. **Use Git Branches**: Create a new branch for each feature or bug fix.
2. **Write Clear Commit Messages**: Use clear and descriptive commit messages to explain the changes made.
3. **Submit Pull Requests**: Submit pull requests for code review and ensure that all checks pass before merging.
4. **Follow the Contribution Guidelines**: Refer to the CONTRIBUTING.md file for detailed steps on contributing to the project.

By following these guidelines, we can ensure a smooth and efficient development process for the Banking Application project.
