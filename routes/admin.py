from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import ParkingLot, ParkingSpot, Reservation, User # Changed import
from flask import render_template, Blueprint, session, redirect, url_for, flash, g
import functools
import database # Assuming you have a database module

admin_bp = Blueprint('admin', __name__)

# Decorator to ensure admin access
def admin_required(view):
    @functools.wraps(view)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'admin':
            flash('Admin access required!', 'error')
            return redirect(url_for('auth.login')) # Redirect to login if not admin
        return view(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
def dashboard():
    # Remove the admin_required decorator temporarily for testing
    return render_template('admin/dashboard.html')
    # Fetch statistics from the database
    db = database.get_db()
    
    # Example: Get total number of users
    total_users = db.execute('SELECT COUNT(id) FROM users').fetchone()[0]
    
    # Example: Get total parking lots (you'll need a 'parking_lots' table for this)
    # For now, let's use a placeholder or assume a fixed number if no table exists yet
    # If you have a parking_lots table:
    # total_lots = db.execute('SELECT COUNT(id) FROM parking_lots').fetchone()[0]
    # Otherwise, use a placeholder:
    total_lots = 100 # Placeholder: Replace with actual logic to get total parking lots

    # You can add more stats here, e.g., available_lots, occupied_lots, etc.
    # For demonstration, let's create a simple stats dictionary
    stats = {
        'total_lots': total_lots,
        'total_users': total_users,
        # Add other stats as needed by your dashboard.html
        'available_lots': 75, # Example placeholder
        'occupied_lots': 25   # Example placeholder
    }

    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/parking-lots')
@admin_required
def parking_lots():
    """View all parking lots"""
    lots = ParkingLot.get_all()
    lot_summary = ParkingSpot.get_lot_summary()
    return render_template('admin/parking_lots.html', lots=lots, lot_summary=lot_summary)

@admin_bp.route('/parking-lots/create', methods=['GET', 'POST'])
@admin_required
def create_parking_lot():
    """Create new parking lot"""
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        pin_code = request.form['pin_code']
        price_per_hour = float(request.form['price_per_hour'])
        max_spots = int(request.form['max_spots'])
        
        if max_spots <= 0 or max_spots > 1000:
            flash('Number of spots must be between 1 and 1000!', 'error')
            return render_template('admin/create_parking_lot.html')
        
        lot_id = ParkingLot.create(name, address, pin_code, price_per_hour, max_spots)
        if lot_id:
            flash(f'Parking lot created successfully with {max_spots} spots!', 'success')
            return redirect(url_for('admin.parking_lots'))
        else:
            flash('Failed to create parking lot!', 'error')
    
    return render_template('admin/create_parking_lot.html')

@admin_bp.route('/parking-lots/<int:lot_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_parking_lot(lot_id):
    """Edit parking lot"""
    lot = ParkingLot.get_by_id(lot_id)
    if not lot:
        flash('Parking lot not found!', 'error')
        return redirect(url_for('admin.parking_lots'))
    
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        pin_code = request.form['pin_code']
        price_per_hour = float(request.form['price_per_hour'])
        max_spots = int(request.form['max_spots'])
        
        if ParkingLot.update(lot_id, name, address, pin_code, price_per_hour, max_spots):
            flash('Parking lot updated successfully!', 'success')
            return redirect(url_for('admin.parking_lots'))
        else:
            flash('Failed to update parking lot!', 'error')
    
    return render_template('admin/edit_parking_lot.html', lot=lot)

@admin_bp.route('/parking-lots/<int:lot_id>/delete', methods=['POST'])
@admin_required
def delete_parking_lot(lot_id):
    """Delete parking lot"""
    success, message = ParkingLot.delete(lot_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('admin.parking_lots'))

@admin_bp.route('/users')
@admin_required
def users():
    """View all users"""
    all_users = User.get_all_users()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/reservations')
@admin_required
def reservations():
    """View all active reservations"""
    active_reservations = Reservation.get_all_active()
    return render_template('admin/reservations.html', reservations=active_reservations)

@admin_bp.route('/search-spot')
@admin_required
def search_spot():
    """Search for specific parking spot"""
    lot_id = request.args.get('lot_id', type=int)
    spot_number = request.args.get('spot_number', type=int)
    
    if lot_id and spot_number:
        # Implementation for spot search
        pass
    
    lots = ParkingLot.get_all()
    return render_template('admin/search_spot.html', lots=lots)
