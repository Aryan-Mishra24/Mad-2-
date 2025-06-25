import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent))

from flask import Flask, render_template, redirect, url_for, session, flash
from database import init_db, create_admin_user
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.user import user_bp
from routes.api_routes import api_bp
from config import Config
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import functools

# Import your database module
import database # Assuming database.py is in the same directory

# Import blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.user import user_bp
from routes.api_routes import api_bp

app = Flask(__name__)
# TEMPORARY: For debugging, hardcode the secret key. REMOVE THIS FOR PRODUCTION!
app.secret_key = "@Iamsherlockedic223145"
# app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24)) # Revert to this for production

# Configure the database path
app.config['DATABASE'] = os.path.join(app.root_path, 'instance', 'flaskr.sqlite')
# Ensure the instance folder exists
os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    """Home page - redirect based on user type"""
    if 'user_id' in session:
        if session.get('user_type') == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    return render_template('index.html')

if __name__ == '__main__':
    # Ensure database is initialized
    init_db()
    create_admin_user()
    app.run(debug=True)
def create_app():
    """Application factory function"""
    app = Flask(__name__)
    
    # Load configuration
    app.secret_key = Config.SECRET_KEY
    app.config.from_object(Config)