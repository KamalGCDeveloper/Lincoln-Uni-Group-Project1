import os
from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.config['SECRET_KEY'] = 'theta_group_secret_key'
app.config['UPLOAD_FOLDER'] = 'app/static/profile_images'
app.config['UPLOAD_COMP_FOLDER'] = 'app/static/competitor_images'
bcrypt = Bcrypt(app)

# Configure ProxyFix if running on PythonAnywhere
if os.environ.get('PYTHONANYWHERE_SITE'):
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

from app import routes
from app import profile
from app import competitions
from app import scrutineer
from app import voter

# Set error redirect page
@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error.html'), 500