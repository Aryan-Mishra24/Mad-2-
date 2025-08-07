from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
from extensions import db
from models import User, ParkingLot, ParkingSpot, Reservation

def init_routes(app):
    # Homepage route
    @app.route('/')
    def index():
        lots = ParkingLot.query.all()
        return render_template('index.html', lots=lots)

    # Quick booking route (no login required)
    @app.route('/quick-book/<int:lot_id>', methods=['POST'])
    def quick_book(lot_id):
        user_email = request.form.get('email')
        user = User.query.filter_by(email=user_email).first()
        
        if not user:
            # Create temporary user
            user = User(
                name=request.form.get('name'),
                email=user_email,
                password=generate_password_hash("temp123"),
                pincode="000000"
            )
            db.session.add(user)
            db.session.commit()

        lot = ParkingLot.query.get_or_404(lot_id)
        spot = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').first()
        
        if not spot:
            flash('No available spots!', 'danger')
            return redirect('/')

        # Create reservation
        spot.status = 'O'
        reservation = Reservation(
            user_id=user.id, 
            spot_id=spot.id,
            in_time=datetime.utcnow()
        )
        db.session.add(reservation)
        db.session.commit()
        
        flash('Spot booked successfully! Check your email for details.', 'success')
        return redirect('/')

    # Admin routes
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
     if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check against the specific admin email
        if email == '24f2002119@ds.study.iitm.ac.in' and check_password_hash(User.query.filter_by(email=email).first().password, password):
            session['admin_logged_in'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials!', 'error')
    
     return render_template('admin/login.html')

    @app.route('/admin/logout')
    def admin_logout():
     if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
     session.pop('admin_logged_in', None)
     flash('Admin logged out successfully!', 'success')
     return redirect(url_for('index'))

    def admin_required(f):
     @wraps(f)
     def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please login as admin to access this page', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
     return decorated_function

    @app.route('/admin/dashboard')
    @admin_required
    def admin_dashboard():
     lots = ParkingLot.query.all()
     total_spots = sum(lot.max_spots for lot in lots)
     occupied_spots = sum(lot.occupied_spots for lot in lots)
     available_spots = total_spots - occupied_spots
    
     occupancy_percentage = (occupied_spots / total_spots * 100) if total_spots > 0 else 0
    
     return render_template('admin/dashboard.html', 
                        lots=lots, 
                        total_spots=total_spots,
                        occupied_spots=occupied_spots,
                        available_spots=available_spots,
                        occupancy_percentage=occupancy_percentage)

    @app.route('/admin/add-lot', methods=['GET', 'POST'])
    @admin_required
    def admin_add_lot():
     if request.method == 'POST':
        try:
            lot = ParkingLot(
                location_name=request.form['location_name'],
                address=request.form['address'],
                pincode=request.form['pincode'],
                price=float(request.form['price']),
                max_spots=int(request.form['max_spots'])
            )
            db.session.add(lot)
            db.session.commit()
            
            for _ in range(lot.max_spots):
                spot = ParkingSpot(lot_id=lot.id, status='A')
                db.session.add(spot)
            
            db.session.commit()
            flash(f'Parking lot "{lot.location_name}" added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating parking lot: {str(e)}', 'error')
    
     return render_template('admin/add_lot.html')

    @app.route('/admin/edit-lot/<int:lot_id>', methods=['GET', 'POST'])
    @admin_required
    def admin_edit_lot(lot_id):
     lot = ParkingLot.query.get_or_404(lot_id)
    
     if request.method == 'POST':
        try:
            lot.location_name = request.form['location_name']
            lot.address = request.form['address']
            lot.pincode = request.form['pincode']
            lot.price = float(request.form['price'])
            db.session.commit()
            flash('Parking lot updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating parking lot: {str(e)}', 'error')
    
     return render_template('admin/edit_lot.html', lot=lot)

    @app.route('/admin/delete-lot/<int:lot_id>')
    @admin_required
    def admin_delete_lot(lot_id):
     lot = ParkingLot.query.get_or_404(lot_id)
    
     try:
        db.session.delete(lot)
        db.session.commit()
        flash(f'Parking lot "{lot.location_name}" deleted successfully!', 'success')
     except Exception as e:
        db.session.rollback()
        flash(f'Error deleting parking lot: {str(e)}', 'error')
    
     return redirect(url_for('admin_dashboard'))

    @app.route('/admin/search')
    @admin_required
    def admin_search():
     query = request.args.get('q', '')
     lots = []
    
     if query:
        lots = ParkingLot.query.filter(
            (ParkingLot.location_name.contains(query)) | 
            (ParkingLot.pincode.contains(query))
        ).all()
    
     return render_template('admin/search.html',
                         query=query,
                         lots=lots)

    @app.route('/admin/users')
    @admin_required
    def admin_users():
     users = User.query.order_by(User.created_at.desc()).all()
     return render_template('admin/users.html', users=users)

    @app.route('/admin/reservations')
    @admin_required
    def admin_reservations():
     reservations = Reservation.query.order_by(Reservation.in_time.desc()).all()
     return render_template('admin/history.html', reservations=reservations)

    @app.route('/admin/reports')
    @admin_required
    def admin_reports():
     daily_revenue = db.session.query(
        db.func.date(Reservation.out_time),
        db.func.sum(Reservation.total_cost)
     ).filter(
        Reservation.out_time.isnot(None)
     ).group_by(
        db.func.date(Reservation.out_time)
     ).order_by(
        db.func.date(Reservation.out_time).desc()
     ).limit(30).all()
    
     occupancy_data = []
     for lot in ParkingLot.query.all():
        occupancy_data.append({
            'name': lot.location_name,
            'occupancy': lot.occupancy_percentage
        })
    
     return render_template('admin/reports.html',
                        daily_revenue=daily_revenue,
                        occupancy_data=occupancy_data)

    # User routes
    @app.route('/register', methods=['GET', 'POST'])
    def user_register():
        if request.method == 'POST':
            if User.query.filter_by(email=request.form['email']).first():
                flash('Email already registered!', 'error')
            else:
                try:
                    user = User(
                        name=request.form['name'],
                        email=request.form['email'],
                        password=generate_password_hash(request.form['password']),
                        pincode=request.form['pincode']
                    )
                    db.session.add(user)
                    db.session.commit()
                    flash('Registration successful! Please login.', 'success')
                    return redirect(url_for('user_login'))
                except Exception as e:
                    db.session.rollback()
                    flash(f'Registration failed: {str(e)}', 'error')
        
        return render_template('user/register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def user_login():
        if request.method == 'POST':
            user = User.query.filter_by(email=request.form['email']).first()
            
            if user and check_password_hash(user.password, request.form['password']):
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_email'] = user.email
                flash(f'Welcome back, {user.name}!', 'success')
                return redirect(url_for('user_dashboard'))
            else:
                flash('Invalid email or password!', 'error')
        
        return render_template('user/login.html')

    @app.route('/logout')
    def user_logout():
        session.pop('user_id', None)
        session.pop('user_name', None)
        session.pop('user_email', None)
        flash('You have been logged out.', 'success')
        return redirect(url_for('home'))

    @app.route('/dashboard')
    def user_dashboard():
     if not session.get('user_id'):
        return redirect(url_for('user_login'))
    
     user = User.query.get(session['user_id'])
     active_reservations = Reservation.query.filter_by(
        user_id=user.id,
        status='active'
     ).all()
    
     # Get nearby lots with at least one available spot
     nearby_lots = ParkingLot.query.filter(
        ParkingLot.pincode.startswith(user.pincode[:3]),
        ParkingLot.spots.any(ParkingSpot.status == 'A')
     ).all()
    
     return render_template('user/dashboard.html',
                        user=user,
                        active_reservations=active_reservations,
                        nearby_lots=nearby_lots)
    
    @app.route('/book/<int:lot_id>')
    def user_book_spot(lot_id):
        if not session.get('user_id'):
            return redirect(url_for('user_login'))
        
        lot = ParkingLot.query.get_or_404(lot_id)
        available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
        
        if not available_spot:
            flash('No available spots in this parking lot!', 'error')
            return redirect(url_for('user_dashboard'))
        
        try:
            reservation = Reservation(
                spot_id=available_spot.id,
                user_id=session['user_id'],
                in_time=datetime.utcnow()
            )
            available_spot.status = 'O'
            db.session.add(reservation)
            db.session.commit()
            flash(f'Parking spot booked at {lot.location_name}!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Booking failed: {str(e)}', 'error')
        
        return redirect(url_for('user_dashboard'))

    @app.route('/release/<int:reservation_id>', methods=['POST'])
    def user_release_spot(reservation_id):
        if not session.get('user_id'):
            return redirect(url_for('user_login'))
        
        reservation = Reservation.query.get_or_404(reservation_id)
        
        if reservation.user_id != session['user_id']:
            flash('Unauthorized action!', 'error')
            return redirect(url_for('user_dashboard'))
        
        try:
            reservation.out_time = datetime.utcnow()
            reservation.status = 'completed'
            
            # Calculate cost (minimum 1 hour)
            duration = max(1, (reservation.out_time - reservation.in_time).total_seconds() / 3600)
            reservation.total_cost = duration * reservation.spot.lot.price
            
            reservation.spot.status = 'A'
            db.session.commit()
            
            flash(f'Spot released. Total cost: ${reservation.total_cost:.2f}', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error releasing spot: {str(e)}', 'error')
        
        return redirect(url_for('user_dashboard'))

    @app.route('/history')
    def user_history():
        if not session.get('user_id'):
            return redirect(url_for('user_login'))
        
        reservations = Reservation.query.filter_by(
            user_id=session['user_id']
        ).order_by(
            Reservation.in_time.desc()
        ).all()
        
        stats = {
            'total_bookings': len(reservations),
            'total_spent': sum(r.total_cost or 0 for r in reservations if r.status == 'completed'),
            'total_hours': sum(r.duration_hours for r in reservations if r.status == 'completed')
        }
        
        return render_template('user/history.html',
                            reservations=reservations,
                            stats=stats)

    @app.route('/profile', methods=['GET', 'POST'])
    def user_profile():
        if not session.get('user_id'):
            return redirect(url_for('user_login'))
        
        user = User.query.get(session['user_id'])
        
        if request.method == 'POST':
            try:
                user.name = request.form['name']
                user.pincode = request.form['pincode']
                
                if request.form['new_password']:
                    if not check_password_hash(user.password, request.form['current_password']):
                        flash('Current password is incorrect!', 'error')
                        return redirect(url_for('user_profile'))
                    
                    user.password = generate_password_hash(request.form['new_password'])
                
                db.session.commit()
                session['user_name'] = user.name
                flash('Profile updated successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating profile: {str(e)}', 'error')
        
        return render_template('user/profile.html', user=user)