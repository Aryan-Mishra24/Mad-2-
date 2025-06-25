
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import ParkingLot, ParkingSpot, Reservation
from functools import wraps

user_bp = Blueprint('user', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page!', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user_id = session['user_id']
    reservations = Reservation.get_user_reservations(user_id)
    
    # Get active reservation
    active_reservation = None
    for res in reservations:
        if res['status'] == 'active':
            active_reservation = res
            break
    
    # Get available parking lots
    available_lots = ParkingLot.get_all()
    lot_summary = ParkingSpot.get_lot_summary()
    
    return render_template('user/dashboard.html', 
                         active_reservation=active_reservation,
                         reservations=reservations[:5],  # Show latest 5
                         available_lots=available_lots,
                         lot_summary=lot_summary)

@user_bp.route('/book-parking', methods=['GET', 'POST'])
@login_required
def book_parking():
    """Book a parking spot"""
    if request.method == 'POST':
        lot_id = int(request.form['lot_id'])
        vehicle_number = request.form['vehicle_number']
        user_id = session['user_id']
        
        # Check if user already has an active reservation
        user_reservations = Reservation.get_user_reservations(user_id)
        for res in user_reservations:
            if res['status'] == 'active':
                flash('You already have an active parking reservation!', 'error')
                return redirect(url_for('user.dashboard'))
        
        success, message = Reservation.create(user_id, lot_id, vehicle_number)
        if success:
            flash(message, 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash(message, 'error')
    
    # Get available lots with spot counts
    lot_summary = ParkingSpot.get_lot_summary()
    available_lots = [lot for lot in lot_summary if lot['available_spots'] > 0]
    
    return render_template('user/book_parking.html', available_lots=available_lots)

@user_bp.route('/my-bookings')
@login_required
def my_bookings():
    """View user's booking history"""
    user_id = session['user_id']
    reservations = Reservation.get_user_reservations(user_id)
    return render_template('user/my_bookings.html', reservations=reservations)

@user_bp.route('/release-spot/<int:reservation_id>', methods=['POST'])
@login_required
def release_spot(reservation_id):
    """Release a parking spot"""
    user_id = session['user_id']
    success, message = Reservation.release_spot(reservation_id, user_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('user.dashboard'))
