import sqlite3
import hashlib
from config import Config
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with all required tables"""
    conn = get_db_connection()
    
    # Enable foreign key constraints
    conn.execute('PRAGMA foreign_keys = ON')
    
    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT,
            user_type TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Parking lots table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS parking_lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prime_location_name TEXT NOT NULL,
            address TEXT NOT NULL,
            pin_code TEXT NOT NULL,
            price_per_hour REAL NOT NULL,
            maximum_number_of_spots INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Parking spots table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS parking_spots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_id INTEGER NOT NULL,
            spot_number INTEGER NOT NULL,
            status TEXT DEFAULT 'A',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lot_id) REFERENCES parking_lots (id) ON DELETE CASCADE,
            UNIQUE(lot_id, spot_number),
            CHECK (status IN ('A', 'O'))
        )
    ''')
    
    # Reservations table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spot_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            parking_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            leaving_timestamp TIMESTAMP,
            parking_cost REAL,
            status TEXT DEFAULT 'active',
            vehicle_number TEXT,
            FOREIGN KEY (spot_id) REFERENCES parking_spots (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            CHECK (status IN ('active', 'completed', 'cancelled'))
        )
    ''')
    
    # Create indexes for better performance
    conn.execute('CREATE INDEX IF NOT EXISTS idx_parking_spots_lot_status ON parking_spots(lot_id, status)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_reservations_user ON reservations(user_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_reservations_spot ON reservations(spot_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_users_type ON users(user_type)')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def create_admin_user():
    """Create default admin user if not exists"""
    conn = get_db_connection()
    
    # Check if admin exists
    admin = conn.execute(
        'SELECT id FROM users WHERE username = ? AND user_type = ?',
        (Config.ADMIN_USERNAME, 'admin')
    ).fetchone()
    
    if not admin:
        password_hash = hashlib.sha256(Config.ADMIN_PASSWORD.encode()).hexdigest()
        conn.execute(
            '''INSERT INTO users (username, email, password_hash, full_name, user_type)
               VALUES (?, ?, ?, ?, ?)''',
            (Config.ADMIN_USERNAME, 'admin@parking.com', password_hash, 'System Administrator', 'admin')
        )
        conn.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists.")
    
    conn.close()

def create_sample_data():
    """Create sample parking lots and spots for testing"""
    conn = get_db_connection()
    
    # Check if sample data already exists
    existing_lots = conn.execute('SELECT COUNT(*) as count FROM parking_lots').fetchone()
    
    if existing_lots['count'] == 0:
        # Create sample parking lots
        sample_lots = [
            {
                'name': 'City Center Mall',
                'address': '123 Main Street, Downtown Area, City Center',
                'pin_code': '380001',
                'price': 25.00,
                'spots': 20
            },
            {
                'name': 'Business District Plaza',
                'address': '456 Corporate Avenue, Business District',
                'pin_code': '380015',
                'price': 40.00,
                'spots': 15
            },
            {
                'name': 'Airport Terminal Parking',
                'address': '789 Airport Road, Terminal 1, International Airport',
                'pin_code': '382475',
                'price': 60.00,
                'spots': 30
            },
            {
                'name': 'Railway Station Complex',
                'address': '321 Station Road, Central Railway Station',
                'pin_code': '380002',
                'price': 20.00,
                'spots': 25
            }
        ]
        
        for lot_data in sample_lots:
            # Insert parking lot
            cursor = conn.execute(
                '''INSERT INTO parking_lots 
                   (prime_location_name, address, pin_code, price_per_hour, maximum_number_of_spots)
                   VALUES (?, ?, ?, ?, ?)''',
                (lot_data['name'], lot_data['address'], lot_data['pin_code'], 
                 lot_data['price'], lot_data['spots'])
            )
            
            lot_id = cursor.lastrowid
            
            # Create parking spots for this lot
            for spot_num in range(1, lot_data['spots'] + 1):
                conn.execute(
                    'INSERT INTO parking_spots (lot_id, spot_number, status) VALUES (?, ?, ?)',
                    (lot_id, spot_num, 'A')
                )
        
        conn.commit()
        print("Sample parking lots and spots created successfully!")
    else:
        print("Sample data already exists.")
    
    conn.close()

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

def get_dashboard_stats():
    """Get dashboard statistics"""
    conn = get_db_connection()
    
    stats = {}
    
    # Total parking lots
    stats['total_lots'] = conn.execute('SELECT COUNT(*) as count FROM parking_lots WHERE is_active = 1').fetchone()['count']
    
    # Total parking spots
    stats['total_spots'] = conn.execute('SELECT COUNT(*) as count FROM parking_spots').fetchone()['count']
    
    # Available spots
    stats['available_spots'] = conn.execute(
        'SELECT COUNT(*) as count FROM parking_spots WHERE status = "A"'
    ).fetchone()['count']
    
    # Occupied spots
    stats['occupied_spots'] = conn.execute(
        'SELECT COUNT(*) as count FROM parking_spots WHERE status = "O"'
    ).fetchone()['count']
    
    # Total users (excluding admin)
    stats['total_users'] = conn.execute(
        'SELECT COUNT(*) as count FROM users WHERE user_type != "admin" AND is_active = 1'
    ).fetchone()['count']
    
    # Active reservations
    stats['active_reservations'] = conn.execute(
        'SELECT COUNT(*) as count FROM reservations WHERE status = "active"'
    ).fetchone()['count']
    
    # Revenue (simplified calculation)
    revenue_result = conn.execute(
        'SELECT SUM(parking_cost) as total FROM reservations WHERE status = "completed"'
    ).fetchone()
    stats['total_revenue'] = revenue_result['total'] if revenue_result['total'] else 0
    
    conn.close()
    return stats

def get_lot_occupancy_data():
    """Get occupancy data for charts"""
    conn = get_db_connection()
    occupancy_data = conn.execute('''
        SELECT pl.prime_location_name as name,
               COUNT(ps.id) as total_spots,
               SUM(CASE WHEN ps.status = 'A' THEN 1 ELSE 0 END) as available,
               SUM(CASE WHEN ps.status = 'O' THEN 1 ELSE 0 END) as occupied
        FROM parking_lots pl
        LEFT JOIN parking_spots ps ON pl.id = ps.lot_id
        WHERE pl.is_active = 1
        GROUP BY pl.id, pl.prime_location_name
        ORDER BY pl.prime_location_name
    ''').fetchall()
    
    conn.close()
    return [dict(row) for row in occupancy_data]

def search_parking_spots(search_term=None, lot_id=None, status=None):
    """Search parking spots with filters"""
    conn = get_db_connection()
    
    query = '''
        SELECT ps.*, pl.prime_location_name, pl.address, r.vehicle_number, u.username, u.full_name
        FROM parking_spots ps
        JOIN parking_lots pl ON ps.lot_id = pl.id
        LEFT JOIN reservations r ON ps.id = r.spot_id AND r.status = 'active'
        LEFT JOIN users u ON r.user_id = u.id
        WHERE 1=1
    '''
    params = []
    
    if search_term:
        query += ' AND (pl.prime_location_name LIKE ? OR pl.address LIKE ? OR u.username LIKE ?)'
        search_param = f'%{search_term}%'
        params.extend([search_param, search_param, search_param])
    
    if lot_id:
        query += ' AND ps.lot_id = ?'
        params.append(lot_id)
    
    if status:
        query += ' AND ps.status = ?'
        params.append(status)
    
    query += ' ORDER BY pl.prime_location_name, ps.spot_number'
    
    results = conn.execute(query, params).fetchall()

    conn.commit()
    conn.close()
    
    return [dict(row) for row in results]

