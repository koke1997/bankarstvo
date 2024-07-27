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

6. **Create .github/labeler.yml Configuration File**
   <pre><code>touch .github/labeler.yml</code></pre>

## **Usage**

Keep in mind you will need a mysql database running in background in order to run this app properly. 

**Running the Application:**
<pre><code>python app.py</code></pre>

## **Demo Page**

A demo page for the banking application is available, showcasing single components and improved documentation with endpoints enlisted on one page. You can access the demo page [here](https://koke1997.github.io/bankarstvo/).

### **Accessing the Enhanced Demo Page**

To access the enhanced demo page with a comprehensive list of all endpoints, follow these steps:

1. **Run the Application**: Ensure the application is running by executing `python app.py`.
2. **Open the Demo Page**: Open your web browser and navigate to `http://localhost:5000/docs`.
3. **Explore the Documentation**: The enhanced demo page includes detailed descriptions and examples for each endpoint, similar to Swagger or Postman documentation.

## **Configuration**

- Update the `app_factory.py` & `DatabaseHandling\connection.py` file with your database and other environment-specific settings.
- Ensure the `GITHUB_TOKEN` secret is configured with write permissions for the `gh-pages` branch.

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
