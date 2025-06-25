
import os

class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this'
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parking_app.db')
    
    # Admin default credentials
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'  # Change this in production
    
    # Application settings
    ITEMS_PER_PAGE = 10
    MAX_PARKING_SPOTS = 1000
