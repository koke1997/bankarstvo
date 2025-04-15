# **Banking Application**

## **Description**

This project is a comprehensive banking application built in Python. It features modules for user registration, login, balance checking, and more, offering a robust framework for banking operations. The main idea is to create more smaller banks instead of having a few big banks in a country. The current challenge is the technology which should enable only real persons to use the banking system.

## **Features**

- **User Registration**: Allows new users to register for the banking service.
- **User Login**: Secure login functionality for existing users.
- **Balance Checking**: Users can check their account balance.
- **Database Connectivity**: Manages secure connections to the database.
- **Data Validation**: Ensures integrity and correctness of user input.
- **Real-Time Notifications**: Users receive real-time notifications for transactions and account alerts, enhancing user engagement.
- **Multi-Factor Authentication**: Enhances security for user accounts by supporting multi-factor authentication.
- **Document Signing and Management**: Expanded features allow users to handle official documents more efficiently.
- **Wider Currency Support**: The app now supports a wider range of currencies for financial transactions, catering to a global audience.
- **User Feedback and Support System**: A new system introduced to improve user satisfaction and app usability.
- **Enhanced Logging System**: The logging system is enhanced for better audit trails and debugging, facilitating maintenance and support.
- **Crypto & Stock Trading**: Users can engage in crypto and stock trading via popular free-to-use APIs. This feature is configurable to allow the application to become SaaS in the future.
- **Digital Marketplace**: Users can sell items in an internal digital marketplace, similar to eBay. This feature is also configurable.
- **Bootstrap Integration**: Improved design and responsiveness using Bootstrap CSS and components.
- **Vue.js Integration**: Dynamic content rendering using Vue.js framework.
- **SASS/SCSS Styling**: Enhanced styling with SASS/SCSS, converting existing CSS to SASS/SCSS and organizing styles into reusable components.
- **Data Visualization**: Integration of Charts.js for financial data visualization.
- **Node.js/Express Server**: Backend routes for API requests and database interactions.
- **Secure Database Setup**: Configuration of MySQL securely using environment variables for sensitive data.
- **CI/CD Pipeline**: Automated deployment to GitHub Pages using GitHub Actions.
- **Improved Navigation**: Implementation of a navigation bar for easy access to different sections.
- **User Interactions**: Inclusion of forms for user inputs (e.g., login, transactions) and implementation of JWT for secure authentication.
- **SEO and Accessibility**: Optimization for search engines with meta tags and descriptive titles, ensuring compliance with WCAG for accessibility.

## **Installation**

**Step-by-step setup:**

1. **Clone the Repository**
   <pre><code>git clone https://github.com/koke1997/bankarstvo</code></pre>

2. **Navigate to the Project Directory**
   <pre><code>cd bankarstvo</code></pre>
 
 3.  **Create and Activate Virtual Environment**
  This is strongly advised for further development, because dependencies can be easily added to the project.
	 <pre><code>python -m virtualenv . </code></pre>
	 
	 3.1. **For Windows (using Command Prompt):**
	  -  <pre><code>.\Scripts\activate</code></pre>
	  3.2 **For Windows (using PowerShell):**
	  -  <pre><code>.\Scripts\Activate.ps1</code></pre>
	  3.3 **For Unix or MacOS (using Bash):**
	  -  <pre><code>source bin/activate</code></pre> 
3. **Install Dependencies**
   <pre><code>pip install -r requirements.txt</code></pre>

4. **Install Node.js Dependencies**
   <pre><code>npm install</code></pre>

5. **Build the Project**
   <pre><code>npm run build</code></pre>

6. **Set up MySQL Database**
   <pre><code>
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
   </code></pre>

7. **Configure Environment Variables**
   <pre><code>
   # Create a .env file in the project root directory and add the following environment variables
   DATABASE_USER=ikokalovic
   DATABASE_PASSWORD=Mikrovela1!
   DATABASE_HOST=localhost
   DATABASE_PORT=3306
   DATABASE_NAME=banking_app
   </code></pre>

## **Usage**

Keep in mind you will need a mysql database running in background in order to run this app properly. 

**Running the Application:**
<pre><code>
# Start MySQL Server
sudo service mysql start

# Run the Flask Application
python app.py
</code></pre>

**Using CI/CD Workflows:**

The project includes GitHub Actions workflows for continuous integration and continuous deployment. These workflows are triggered on push and pull request events.

- **Continuous Integration (CI)**: Runs tests and linting on pull requests and commits to the main branch.
- **Continuous Deployment (CD)**: Deploys the application to GitHub Pages on successful builds.

**Running Tests:**

To run tests locally, use the following command:
<pre><code>npm test</code></pre>

## **Kubernetes Deployment**

### **Prerequisites**

- Docker installed on your local machine
- Kubernetes cluster set up (e.g., Minikube, GKE, EKS, AKS)
- kubectl installed and configured to interact with your Kubernetes cluster

### **Steps**

1. **Build Docker Image**

   Build the Docker image for the application:

   ```sh
   docker build -t koke1997/banking-app:latest .
   ```

2. **Push Docker Image**

   Push the Docker image to a container registry (e.g., Docker Hub):

   ```sh
   docker push koke1997/banking-app:latest
   ```

3. **Apply Kubernetes Manifests**

   Apply the Kubernetes deployment and service configuration files:

   ```sh
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```

4. **Verify Deployment**

   Verify that the application is running in your Kubernetes cluster:

   ```sh
   kubectl get pods
   kubectl get services
   ```

## **Contributing**

Contributions are welcome. Here's how you can contribute:

1. **Fork the Repository**
2. **Create a Feature Branch**
   <pre><code>git checkout -b feature/YourFeature</code></pre>

3. **Commit Your Changes**
   <pre><code>git commit -am 'Add some feature'</code></pre>

4. **Push to the Branch**
   <pre><code>git push origin feature/YourFeature</code></pre>

5. **Submit a Pull Request**

## **License**

- [MIT License](LICENSE)

## **Contact**

For queries or contributions, contact me at [ivankokalovic@protonmail.ch](mailto:ivankokalovic@protonmail.ch).

## **Automatic Issue Creation on PR Failure**

This project includes a GitHub Actions workflow to automatically create issues when a pull request (PR) fails. This helps in tracking and resolving issues promptly.

### **Workflow Description**

The new GitHub Actions workflow file `pr_failure_issue.yml` is designed to detect PR failures and create issues automatically. The workflow is triggered by `pull_request` events and checks for failed jobs. If a job fails, the workflow creates a new issue using the `actions/github-script` action. The issue includes details about the failed job, such as the job name, failure message, and a link to the failed workflow run.

### **Configuration and Usage**

1. **Create the Workflow File**

   Create a new file named `pr_failure_issue.yml` in the `.github/workflows` directory of your repository.

2. **Define the Workflow**

   Add the following content to the `pr_failure_issue.yml` file:

   ```yaml
   name: PR Failure Issue

   on:
     pull_request:
       types: [opened, synchronize, reopened]

   jobs:
     check-failure:
       runs-on: ubuntu-latest

       steps:
       - name: Checkout code
         uses: actions/checkout@v2

       - name: Check for failed jobs
         if: failure()
         uses: actions/github-script@v4
         with:
           script: |
             const { context, github } = require('@actions/github');
             const issueTitle = `PR #${context.payload.pull_request.number} failed`;
             const issueBody = `
               The following job failed:
               - **Job Name**: ${context.job}
               - **Failure Message**: ${context.payload.pull_request.title}
               - **Workflow Run**: ${context.payload.pull_request.html_url}
             `;
             await github.issues.create({
               ...context.repo,
               title: issueTitle,
               body: issueBody,
               labels: ['bug', 'PR Failure']
             });
   ```

3. **Commit and Push**

   Commit the new workflow file and push it to your repository:

   ```sh
   git add .github/workflows/pr_failure_issue.yml
   git commit -m "Add workflow for automatic issue creation on PR failure"
   git push origin main
   ```

4. **Verify**

   Create a pull request and ensure that the workflow runs. If the PR fails, an issue should be automatically created in your repository.

## **Splitting Errors and Saving Logs**

The project now includes enhancements to split errors from linting and functional testing, and to save logs from failed jobs during PR checks.

### **Splitting Errors**

Errors from linting and functional testing are now split to provide better clarity and debugging information. The following scripts have been added to `package.json`:

- **Unit Tests**: `npm run test:unit`
- **Linting**: `npm run test:lint`
- **All Tests**: `npm run test:all`

### **Saving Logs from Failed Jobs**

Logs from failed jobs during PR checks are now saved to help with debugging and issue resolution. The following steps have been added to the CI/CD workflows:

- **CI Workflow**: Added steps to split the `Run tests` step into `Run unit tests` and `Run linting`, and to save logs from failed jobs.
- **PR Failure Issue Workflow**: Added a step to save logs from failed jobs during PR checks.

## **Detailed Documentation for Individual Modules, Functions, and Classes**

### **Modules**

#### **app_factory.py**

- **create_app()**: Initializes and configures the Flask application, including logging, database connections, and blueprints.

#### **cli.py**

- **start_app()**: Starts the application.
- **stop_app()**: Stops the application.
- **restart_app()**: Restarts the application.
- **status_app()**: Checks the status of the application.

### **Functions**

#### **app_factory.py**

- **create_app()**: Initializes and configures the Flask application, including logging, database connections, and blueprints.

#### **cli.py**

- **start_app()**: Starts the application.
- **stop_app()**: Stops the application.
- **restart_app()**: Restarts the application.
- **status_app()**: Checks the status of the application.

### **Classes**

#### **core/models.py**

- **User**: Represents a user in the system.
- **Transaction**: Represents a transaction in the system.
- **Account**: Represents an account in the system.
- **SignedDocument**: Represents a signed document in the system.
- **CryptoAsset**: Represents a crypto asset in the system.
- **StockAsset**: Represents a stock asset in the system.
- **MarketplaceItem**: Represents an item in the marketplace.
- **MarketplaceTransaction**: Represents a transaction in the marketplace.
- **Loan**: Represents a loan in the system.
- **Payment**: Represents a payment in the system.

## **Comprehensive Usage Instructions for Specific Features or Components**

### **User Registration**

To register a new user, send a POST request to the `/register` endpoint with the following JSON payload:

```json
{
    "username": "example",
    "email": "example@example.com",
    "password": "password"
}
```

### **User Login**

To log in an existing user, send a POST request to the `/login` endpoint with the following JSON payload:

```json
{
    "username": "example",
    "password": "password"
}
```

### **Balance Checking**

To check the account balance, send a GET request to the `/balance` endpoint.

### **Transaction History**

To view the transaction history, send a GET request to the `/transactions` endpoint.

## **Detailed API Documentation for Endpoints**

### **Register Endpoint**

Endpoint for user registration.

```http
POST /register
{
    "username": "example",
    "email": "example@example.com",
    "password": "password"
}
```

### **Login Endpoint**

Endpoint for user login.

```http
POST /login
{
    "username": "example",
    "password": "password"
}
```

### **Balance Endpoint**

Endpoint for checking account balance.

```http
GET /balance
```

### **Transactions Endpoint**

Endpoint for viewing transaction history.

```http
GET /transactions
```

### **Full Endpoint List**

Comprehensive list of all endpoints, similar to Swagger or Postman documentation.

```http
GET /accounts
{
    "description": "Retrieve all accounts",
    "example_response": {
        "accounts": [
            {
                "account_id": 1,
                "account_name": "Checking Account",
                "balance": 1000.00
            },
            {
                "account_id": 2,
                "account_name": "Savings Account",
                "balance": 5000.00
            }
        ]
    }
}

POST /accounts
{
    "description": "Create a new account",
    "example_request": {
        "account_name": "New Account",
        "initial_balance": 0.00
    },
    "example_response": {
        "message": "Account created successfully",
        "account_id": 3
    }
}

PUT /accounts/{account_id}
{
    "description": "Update an existing account",
    "example_request": {
        "account_name": "Updated Account Name"
    },
    "example_response": {
        "message": "Account updated successfully"
    }
}

DELETE /accounts/{account_id}
{
    "description": "Delete an account",
    "example_response": {
        "message": "Account deleted successfully"
    }
}
```
