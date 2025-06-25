
from flask import Blueprint, jsonify, request, session
from models import ParkingLot, ParkingSpot, Reservation, User
from functools import wraps

api_bp = Blueprint('api', __name__)

def api_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/parking-lots', methods=['GET'])
@api_auth_required
def get_parking_lots():
    """Get all parking lots with availability"""
    lot_summary = ParkingSpot.get_lot_summary()
    lots_data = []
    
    for lot in lot_summary:
        lots_data.append({
            'id': lot['id'],
            'name': lot['prime_location_name'],
            'address': lot['address'],
            'price_per_hour': lot['price_per_hour'],
            'total_spots': lot['total_spots'],
            'available_spots': lot['available_spots'],
            'occupied_spots': lot['occupied_spots']
        })
    
    return jsonify({'parking_lots': lots_data})

@api_bp.route('/parking-lots/<int:lot_id>/spots', methods=['GET'])
@api_auth_required
def get_lot_spots(lot_id):
    """Get available spots in a parking lot"""
    spots = ParkingSpot.get_available_spots(lot_id)
    spots_data = []
    
    for spot in spots:
        spots_data.append({
            'id': spot['id'],
            'spot_number': spot['spot_number'],
            'status': spot['status']
        })
    
    return jsonify({'spots': spots_data})

@api_bp.route('/reservations', methods=['POST'])
@api_auth_required
def create_reservation():
    """Create a new reservation via API"""
    data = request.get_json()
    
    if not data or 'lot_id' not in data or 'vehicle_number' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    user_id = session['user_id']
    lot_id = data['lot_id']
    vehicle_number = data['vehicle_number']
    
    success, message = Reservation.create(user_id, lot_id, vehicle_number)
    
    if success:
        return jsonify({'message': message}), 201
    else:
        return jsonify({'error': message}), 400

@api_bp.route('/reservations/<int:reservation_id>/release', methods=['POST'])
@api_auth_required
def release_reservation(reservation_id):
    """Release a reservation via API"""
    user_id = session['user_id']
    success, message = Reservation.release_spot(reservation_id, user_id)
    
    if success:
        return jsonify({'message': message})
    else:
        return jsonify({'error': message}), 400

@api_bp.route('/dashboard-stats', methods=['GET'])
@api_auth_required
def get_dashboard_stats():
    """Get dashboard statistics"""
    if session.get('user_type') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    lot_summary = ParkingSpot.get_lot_summary()
    active_reservations = Reservation.get_all_active()
    total_users = len(User.get_all_users())
    
    total_spots = sum(lot['total_spots'] for lot in lot_summary)
    total_occupied = sum(lot['occupied_spots'] for lot in lot_summary)
    total_available = sum(lot['available_spots'] for lot in lot_summary)
    
    stats = {
        'total_lots': len(lot_summary),
        'total_spots': total_spots,
        'total_occupied': total_occupied,
        'total_available': total_available,
        'total_users': total_users,
        'active_reservations': len(active_reservations)
    }
    
    return jsonify(stats)
