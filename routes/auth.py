from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db_connection, hash_password, verify_password

auth_bp = Blueprint('auth', __name__)

from flask import redirect, url_for

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            full_name = request.form['full_name']
            phone = request.form.get('phone', '')
            
            print(f"Registration attempt: {username}, {email}")  # Debug print
            
            # Hash password
            password_hash = hash_password(password)
            
            conn = get_db_connection()
            
            # Check if user already exists
            existing_user = conn.execute(
                'SELECT id FROM users WHERE username = ? OR email = ?',
                (username, email)
            ).fetchone()
            
            if existing_user:
                flash('Username or email already exists', 'error')
                conn.close()
                return render_template('auth/register.html')
            
            # Create new user
            cursor = conn.execute(
                '''INSERT INTO users (username, email, password_hash, full_name, phone, user_type)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (username, email, password_hash, full_name, phone, 'user')
            )
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"User registered successfully: ID {user_id}")  # Debug print
            
            # Auto-login after registration
            session['user_id'] = user_id
            session['username'] = username
            session['user_type'] = 'user'
            
            # After successful registration
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))  # Redirect to login page

        except Exception as e:
            print(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            
            # Set session variables to simulate successful login
            session['user_id'] = 1  # Example user ID
            session['user_type'] = 'admin'  # Force admin access
            return redirect(url_for('admin.dashboard'))
            
            if user and verify_password(password, user['password_hash']):
                session['user_id'] = user['id']
                session['user_type'] = user['user_type']
                
                flash('Login successful!', 'success')
                
                # Ensure proper redirects
                if session['user_type'] == 'admin':
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('user.dashboard'))
            else:
                flash('Invalid username or password', 'error')
                
        except Exception as e:
            print(f"Login error: {e}")
            flash('Login failed. Please try again.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))