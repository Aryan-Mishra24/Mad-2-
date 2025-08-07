from flask import Flask
from extensions import db
from models import User, ParkingLot, ParkingSpot, Reservation
from werkzeug.security import generate_password_hash
import os

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'change-this-secret-key'
    
    # SQLite Database Configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'parking.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Import routes
    from routes import init_routes
    
    # Initialize database and routes
    with app.app_context():
        initialize_database()
        init_routes(app)
    
    return app

def initialize_database():
    # Create database directory if it doesn't exist
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    # Create all database tables
    db.create_all()
    
    # Create admin user if not exists
    if not User.query.filter_by(email='23f1002447@ds.study.iitm.ac.in').first():
        admin = User(
            name='Admin',
            email='23f1002447@ds.study.iitm.ac.in',
            password=generate_password_hash('admin123'),
            pincode='600036'
        )
        db.session.add(admin)
        db.session.commit()
    
    # Create sample parking lot if none exists
    if not ParkingLot.query.first():
        lot = ParkingLot(
            location_name="Krishna", 
            address="IIT MAdras", 
            pincode="600036", 
            price=50.0, 
            max_spots=10
        )
        db.session.add(lot)
        db.session.commit()
        
        for i in range(lot.max_spots):
            db.session.add(ParkingSpot(lot_id=lot.id, status='A'))
        db.session.commit()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)