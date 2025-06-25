
from database import get_db_connection
from datetime import datetime

class User:
    @staticmethod
    def create(username, email, password_hash, full_name, phone=None):
        """Create a new user"""
        conn = get_db_connection()
        try:
            conn.execute(
                '''INSERT INTO users (username, email, password_hash, full_name, phone)
                   VALUES (?, ?, ?, ?, ?)''',
                (username, email, password_hash, full_name, phone)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        conn.close()
        return user
    
    @staticmethod
    def get_all_users():
        """Get all regular users (not admin)"""
        conn = get_db_connection()
        users = conn.execute(
            'SELECT * FROM users WHERE user_type = ? ORDER BY created_at DESC',
            ('user',)
        ).fetchall()
        conn.close()
        return users

class ParkingLot:
    @staticmethod
    def create(name, address, pin_code, price_per_hour, max_spots):
        """Create a new parking lot with spots"""
        conn = get_db_connection()
        try:
            # Insert parking lot
            cursor = conn.execute(
                '''INSERT INTO parking_lots (prime_location_name, address, pin_code, 
                   price_per_hour, maximum_number_of_spots)
                   VALUES (?, ?, ?, ?, ?)''',
                (name, address, pin_code, price_per_hour, max_spots)
            )
            lot_id = cursor.lastrowid
            
            # Create parking spots
            for spot_num in range(1, max_spots + 1):
                conn.execute(
                    'INSERT INTO parking_spots (lot_id, spot_number) VALUES (?, ?)',
                    (lot_id, spot_num)
                )
            
            conn.commit()
            return lot_id
        except Exception as e:
            print(f"Error creating parking lot: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_all():
        """Get all active parking lots"""
        conn = get_db_connection()
        lots = conn.execute(
            'SELECT * FROM parking_lots WHERE is_active = 1 ORDER BY created_at DESC'
        ).fetchall()
        conn.close()
        return lots
    
    @staticmethod
    def get_by_id(lot_id):
        """Get parking lot by ID"""
        conn = get_db_connection()
        lot = conn.execute(
            'SELECT * FROM parking_lots WHERE id = ?', (lot_id,)
        ).fetchone()
        conn.close()
        return lot
    
    @staticmethod
    def update(lot_id, name, address, pin_code, price_per_hour, max_spots):
        """Update parking lot and adjust spots"""
        conn = get_db_connection()
        try:
            # Update lot details
            conn.execute(
                '''UPDATE parking_lots SET prime_location_name = ?, address = ?, 
                   pin_code = ?, price_per_hour = ?, maximum_number_of_spots = ?
                   WHERE id = ?''',
                (name, address, pin_code, price_per_hour, max_spots, lot_id)
            )
            
            # Get current spot count
            current_spots = conn.execute(
                'SELECT COUNT(*) as count FROM parking_spots WHERE lot_id = ?',
                (lot_id,)
            ).fetchone()['count']
            
            if max_spots > current_spots:
                # Add new spots
                for spot_num in range(current_spots + 1, max_spots + 1):
                    conn.execute(
                        'INSERT INTO parking_spots (lot_id, spot_number) VALUES (?, ?)',
                        (lot_id, spot_num)
                    )
            elif max_spots < current_spots:
                # Remove excess spots (only if they're available)
                conn.execute(
                    '''DELETE FROM parking_spots 
                       WHERE lot_id = ? AND spot_number > ? AND status = 'A' ''',
                    (lot_id, max_spots)
                )
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating parking lot: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    @staticmethod
    def delete(lot_id):
        """Delete parking lot if all spots are available"""
        conn = get_db_connection()
        try:
            # Check if any spots are occupied
            occupied_spots = conn.execute(
                'SELECT COUNT(*) as count FROM parking_spots WHERE lot_id = ? AND status = "O"',
                (lot_id,)
            ).fetchone()['count']
            
            if occupied_spots > 0:
                return False, "Cannot delete lot with occupied spots"
            
            # Delete spots first, then lot
            conn.execute('DELETE FROM parking_spots WHERE lot_id = ?', (lot_id,))
            conn.execute('DELETE FROM parking_lots WHERE id = ?', (lot_id,))
            conn.commit()
            return True, "Parking lot deleted successfully"
        except Exception as e:
            conn.rollback()
            return False, f"Error deleting parking lot: {e}"
        finally:
            conn.close()

class ParkingSpot:
    @staticmethod
    def get_available_spots(lot_id):
        """Get available spots in a parking lot"""
        conn = get_db_connection()
        spots = conn.execute(
            '''SELECT ps.*, pl.prime_location_name, pl.price_per_hour
               FROM parking_spots ps
               JOIN parking_lots pl ON ps.lot_id = pl.id
               WHERE ps.lot_id = ? AND ps.status = 'A'
               ORDER BY ps.spot_number''',
            (lot_id,)
        ).fetchall()
        conn.close()
        return spots
    
    @staticmethod
    def get_lot_summary():
        """Get summary of all parking lots with spot counts"""
        conn = get_db_connection()
        summary = conn.execute(
            '''SELECT pl.id, pl.prime_location_name, pl.address, pl.price_per_hour,
                      COUNT(ps.id) as total_spots,
                      SUM(CASE WHEN ps.status = 'A' THEN 1 ELSE 0 END) as available_spots,
                      SUM(CASE WHEN ps.status = 'O' THEN 1 ELSE 0 END) as occupied_spots
               FROM parking_lots pl
               LEFT JOIN parking_spots ps ON pl.id = ps.lot_id
               WHERE pl.is_active = 1
               GROUP BY pl.id
               ORDER BY pl.prime_location_name''').fetchall()
        conn.close()
        return summary

class Reservation:
    @staticmethod
    def create(user_id, lot_id, vehicle_number):
        """Create a new reservation by finding first available spot"""
        conn = get_db_connection()
        try:
            # Find first available spot
            spot = conn.execute(
                '''SELECT id FROM parking_spots 
                   WHERE lot_id = ? AND status = 'A' 
                   ORDER BY spot_number LIMIT 1''',
                (lot_id,)
            ).fetchone()
            
            if not spot:
                return False, "No available spots"
            
            spot_id = spot['id']
            
            # Create reservation
            conn.execute(
                '''INSERT INTO reservations (spot_id, user_id, vehicle_number)
                   VALUES (?, ?, ?)''',
                (spot_id, user_id, vehicle_number)
            )
            
            # Update spot status
            conn.execute(
                'UPDATE parking_spots SET status = "O" WHERE id = ?',
                (spot_id,)
            )
            
            conn.commit()
            return True, "Parking spot reserved successfully"
        except Exception as e:
            conn.rollback()
            return False, f"Error creating reservation: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def get_user_reservations(user_id):
        """Get all reservations for a user"""
        conn = get_db_connection()
        reservations = conn.execute(
            '''SELECT r.*, ps.spot_number, pl.prime_location_name, pl.address, pl.price_per_hour
               FROM reservations r
               JOIN parking_spots ps ON r.spot_id = ps.id
               JOIN parking_lots pl ON ps.lot_id = pl.id
               WHERE r.user_id = ?
               ORDER BY r.parking_timestamp DESC''',
            (user_id,)
        ).fetchall()
        conn.close()
        return reservations
    
    @staticmethod
    def release_spot(reservation_id, user_id):
        """Release a parking spot and calculate cost"""
        conn = get_db_connection()
        try:
            # Get reservation details
            reservation = conn.execute(
                '''SELECT r.*, ps.spot_number, pl.price_per_hour
                   FROM reservations r
                   JOIN parking_spots ps ON r.spot_id = ps.id
                   JOIN parking_lots pl ON ps.lot_id = pl.id
                   WHERE r.id = ? AND r.user_id = ? AND r.status = 'active' ''',
                (reservation_id, user_id)
            ).fetchone()
            
            if not reservation:
                return False, "Reservation not found"
            
            # Calculate parking cost
            parking_time = datetime.now()
            start_time = datetime.fromisoformat(reservation['parking_timestamp'])
            duration_hours = (parking_time - start_time).total_seconds() / 3600
            cost = duration_hours * reservation['price_per_hour']
            
            # Update reservation
            conn.execute(
                '''UPDATE reservations 
                   SET leaving_timestamp = ?, parking_cost = ?, status = 'completed'
                   WHERE id = ?''',
                (parking_time, cost, reservation_id)
            )
            
            # Update spot status
            conn.execute(
                'UPDATE parking_spots SET status = "A" WHERE id = ?',
                (reservation['spot_id'],)
            )
            
            conn.commit()
            return True, f"Spot released. Total cost: ₹{cost:.2f}"
        except Exception as e:
            conn.rollback()
            return False, f"Error releasing spot: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def get_all_active():
        """Get all active reservations"""
        conn = get_db_connection()
        reservations = conn.execute(
            '''SELECT r.*, u.username, u.full_name, ps.spot_number, 
                      pl.prime_location_name, pl.address
               FROM reservations r
               JOIN users u ON r.user_id = u.id
               JOIN parking_spots ps ON r.spot_id = ps.id
               JOIN parking_lots pl ON ps.lot_id = pl.id
               WHERE r.status = 'active'
               ORDER BY r.parking_timestamp DESC''').fetchall()
        conn.close()
        return reservations
