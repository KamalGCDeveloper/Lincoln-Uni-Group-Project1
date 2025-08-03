# COMP639S2_project_1_Theta

This is a Flask web application developed by Theta Group. The application includes various modules for user profiles, competitions, admin/scrutineer dashboards, and voter functionalities. 

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Environment Configuration](#environment-configuration)
- [Deployment](#deployment)
- [Error Handling](#error-handling)

## Features
User profile management with image uploads.
Competition creation and management.
Scrutineer dashboard for competition oversight.
Voting system with secure password management using flask_bcrypt.

## Requirements
blinker==1.8.2
click==8.1.7
Flask==3.0.3
Flask-Hashing==1.1
Jinja2==3.1.4
MarkupSafe==2.1.5
mysql-connector-python==9.0.0
Werkzeug==3.0.3
Flask-Session==0.4.0

## Installation
1. Clone the repository:
open bash and input the following code:
git clone https://github.com/yourusername/yourrepository.git
cd [yourrepository]
2. Create a virtual environment:
use bash and input the following code:
python -m venv venv
source venv/bin/activate
3. Install the dependencies:
use bash and input the following code:
pip install -r requirements.txt

## Usage
1. Set the environment variables (optional):
use bash and input the following code:
export FLASK_APP=run.py
export FLASK_ENV=development
2. Run the application:
use bash and input the following code:
flask run
3. Access the application at http://127.0.0.1:5000.

## Environment Configuration
SECRET_KEY: Secret key for session management.
UPLOAD_FOLDER: Directory for storing user profile images.
UPLOAD_COMP_FOLDER: Directory for storing competitor images.
PYTHONANYWHERE_SITE: Set this variable if deploying on PythonAnywhere.

## Deployment
PythonAnywhere
If deploying on PythonAnywhere, make sure to configure ProxyFix in __init__.py:

if os.environ.get('PYTHONANYWHERE_SITE'):
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

## Error Handling
Custom error handling is implemented for common HTTP errors:
404 Not Found: Redirects to error.html.
500 Internal Server Error: Redirects to error.html.
