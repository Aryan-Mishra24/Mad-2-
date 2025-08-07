from datetime import datetime
from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reservations = db.relationship('Reservation', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    spots = db.relationship('ParkingSpot', backref='lot', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ParkingLot {self.location_name}>'

    @property
    def available_spots(self):
        return len([spot for spot in self.spots if spot.status == 'A'])

    @property
    def occupied_spots(self):
        return len([spot for spot in self.spots if spot.status == 'O'])

    @property
    def occupancy_percentage(self):
        if self.max_spots == 0:
            return 0
        return (self.occupied_spots / self.max_spots) * 100

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status = db.Column(db.String(1), nullable=False, default='A')  # A = Available, O = Occupied

    reservations = db.relationship('Reservation', backref='spot', lazy=True)

    def __repr__(self):
        return f'<ParkingSpot {self.id} - {self.status}>'

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    in_time = db.Column(db.DateTime, default=datetime.utcnow)
    out_time = db.Column(db.DateTime, nullable=True)
    total_cost = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, completed

    def __repr__(self):
        return f'<Reservation {self.id} - User {self.user_id}>'

    @property
    def duration_hours(self):
        if self.out_time:
            duration = self.out_time - self.in_time
            return round(duration.total_seconds() / 3600, 2)
        return 0