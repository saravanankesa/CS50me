# Monemome - Personal Finance Management

## Introduction

Monemome is a personal finance management application designed to help users effectively track and manage their financial transactions, accounts, and budget categories. The application supports multiple functionalities such as creating and managing transactions, managing pre-authorized payments, account balances, and categorizing expenses to give users a comprehensive overview of their financial health.

This project was developed as part of [Your Course Name], designed to showcase not only technical skills in web development using Django but also an understanding of practical financial management tools that users can interact with on a daily basis.

## Distinctiveness and Complexity

### Distinctiveness
Monemome distinguishes itself from other finance apps and course projects through its detailed focus on pre-authorized transactions and user experience enhancements. Unlike generic tracking applications, Monemome provides a specialized view for managing recurring payments, which is crucial for users who have multiple subscriptions or recurring bills. This feature allows users to see upcoming payments and ensure they have sufficient funds, which helps in avoiding overdraft fees and managing budgets more effectively.

### Complexity
The complexity of Monemome is evident through its robust backend and frontend development:
- **Backend**: The application uses Django models to handle complex relationships between users, transactions, accounts, and categories. Custom views handle business logic such as ordering transactions by date, filtering them by account or category, and alerting users of upcoming payments.
- **Frontend**: The use of advanced CSS techniques for responsive design and dynamic updates using Django templates provides a seamless and intuitive user experience. The integration of JavaScript for interactive components like modal windows for form submissions enhances usability without requiring page reloads.

## Project Structure

- `monemome/`
  - `settings.py` - Contains settings for the Django project, including configured apps, middleware, and database configurations.
  - `urls.py` - Defines the URL structure of the site. Main routing to the app's views.
- `finance_manager/`
  - `models.py` - Defines the data models for Accounts, Transactions, and Categories.
  - `views.py` - Contains the business logic for processing and responding to user requests.
  - `forms.py` - Defines Django forms for data entry like transactions and account creation.
  - `templates/` - Contains HTML templates for rendering views.
  - `static/` - Stores static files like CSS, JavaScript, and images.
- `requirements.txt` - Lists all Python dependencies for the project.
- `README.md` - This file, describing the project and how to run it.

## How to Run the Application

1. **Set up the environment**:
   - Ensure Python and Django are installed. If not, install them using pip:
     ```
     pip install django
     ```
   - Install other dependencies:
     ```
     pip install -r requirements.txt
     ```

2. **Initialize the database**:
   - Navigate to the project directory where `manage.py` is located.
   - Run the following commands to set up the database:
     ```
     python manage.py makemigrations
     python manage.py migrate
     ```

3. **Run the server**:
   - Start the Django development server:
     ```
     python manage.py runserver
     ```
   - Open a web browser and go to `http://127.0.0.1:8000/` to start using Monemome.

## Additional Information

- **Account Configuration**: Ensure that you set up initial data for accounts and categories through the admin panel or signup flow to fully utilize all features.
- **Security Features**: For educational purposes, this project does not implement advanced security features like two-factor authentication or encryption of sensitive data. It is recommended to add such features before any real-world deployment.

## Conclusion

Monemome is a comprehensive personal finance application built with a focus on user-centric design and practical functionality. It has been crafted with care to ensure that it meets the high standards of software engineering required for academic projects while providing a real-world utility. I am proud of the distinctive aspects and complex functionality it offers, making it a unique contribution to the field of educational projects in web development.
