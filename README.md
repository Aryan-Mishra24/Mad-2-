# Vehicle Parking App

A comprehensive multi-user vehicle parking management system built with Flask, SQLite, and Bootstrap.

## Features

### Admin Features
- **Dashboard**: Overview of all parking lots, spots, and reservations
- **Parking Lot Management**: Create, edit, and delete parking lots
- **User Management**: View all registered users
- **Real-time Monitoring**: Track occupied and available spots
- **Reservation Management**: View all active reservations

### User Features
- **Registration/Login**: Secure user authentication
- **Parking Booking**: Reserve available parking spots
- **Dashboard**: View active reservations and booking history
- **Spot Release**: Release parking spots and calculate costs
- **Real-time Availability**: See live parking availability

### Technical Features
- **RESTful APIs**: JSON endpoints for mobile/external integration
- **Responsive Design**: Bootstrap-based mobile-friendly interface
- **Real-time Updates**: Live dashboard statistics
- **Secure Authentication**: Session-based user management
- **Database Integrity**: Foreign key constraints and data validation

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Templating**: Jinja2
- **Icons**: Font Awesome

## Installation & Setup

1. **Clone the repository**
   \`\`\`bash
   git clone <repository-url>
   cd vehicle_parking_app
   \`\`\`

2. **Create virtual environment**
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   \`\`\`

3. **Install dependencies**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

4. **Run the application**
   \`\`\`bash
   python app.py
   \`\`\`

5. **Access the application**
   - Open browser and go to `http://localhost:5000`
   - Admin login: username=`admin`, password=`admin123`

## Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `password_hash`
- `full_name`
- `phone`
- `user_type` (admin/user)
- `created_at`
- `is_active`

### Parking Lots Table
- `id` (Primary Key)
- `prime_location_name`
- `address`
- `pin_code`
- `price_per_hour`
- `maximum_number_of_spots`
- `created_at`
- `is_active`

### Parking Spots Table
- `id` (Primary Key)
- `lot_id` (Foreign Key)
- `spot_number`
- `status` (A=Available, O=Occupied)
- `created_at`

### Reservations Table
- `id` (Primary Key)
- `spot_id` (Foreign Key)
- `user_id` (Foreign Key)
- `parking_timestamp`
- `leaving_timestamp`
- `parking_cost`
- `status` (active/completed)
- `vehicle_number`

## API Endpoints

### Authentication Required
- `GET /api/parking-lots` - Get all parking lots with availability
- `GET /api/parking-lots/<id>/spots` - Get available spots in a lot
- `POST /api/reservations` - Create new reservation
- `POST /api/reservations/<id>/release` - Release a reservation

### Admin Only
- `GET /api/dashboard-stats` - Get dashboard statistics

## Project Structure

\`\`\`
vehicle_parking_app/
├── app.py                     # Main Flask application
├── config.py                  # Configuration settings
├── database.py                # Database initialization
├── models.py                  # Database models
├── routes/                    # Route handlers
│   ├── auth_routes.py         # Authentication routes
│   ├── admin_routes.py        # Admin functionality
│   ├── user_routes.py         # User functionality
│   └── api_routes.py          # API endpoints
├── static/                    # Static files
│   ├── css/style.css          # Custom styles
│   └── js/script.js           # JavaScript functionality
├── templates/                 # HTML templates
│   ├── base.html              # Base template
│   ├── auth/                  # Authentication templates
│   ├── admin/                 # Admin templates
│   └── user/                  # User templates
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
\`\`\`

## Usage

### For Administrators
1. Login with admin credentials
2. Create parking lots with desired number of spots
3. Monitor real-time occupancy and reservations
4. Manage users and view system statistics
5. Edit or delete parking lots as needed

### For Users
1. Register a new account or login
2. Browse available parking lots
3. Book a parking spot by selecting a lot and entering vehicle details
4. View active reservations on dashboard
5. Release parking spot when leaving (cost calculated automatically)

## Key Features Implemented

✅ **Multi-user system** with Admin and User roles  
✅ **Programmatic database creation** with proper relationships  
✅ **Real-time parking availability** tracking  
✅ **Automatic spot allocation** (first available)  
✅ **Cost calculation** based on parking duration  
✅ **Responsive web interface** with Bootstrap  
✅ **RESTful API endpoints** for external integration  
✅ **Session-based authentication**  
✅ **Data validation** and error handling  
✅ **Dashboard analytics** and reporting  

## Security Considerations

- Passwords are hashed using SHA256
- Session-based authentication
- Input validation and sanitization
- SQL injection prevention through parameterized queries
- CSRF protection through Flask's built-in features

## Future Enhancements

- Payment gateway integration
- Email notifications
- Mobile app development
- Advanced reporting and analytics
- Parking spot reservations in advance
- QR code-based check-in/check-out
- Integration with vehicle number plate recognition

## License

This project is developed for educational purposes as part of a Flask web development course.

## Support

For any issues or questions, please refer to the project documentation or contact the development team.
