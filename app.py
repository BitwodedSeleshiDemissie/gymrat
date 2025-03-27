from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
import json
import os

app = Flask(__name__)
app.secret_key = 'gym-booking-secret-key'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

BOOKINGS_FILE = 'bookings.json'

def load_bookings():
    with open(BOOKINGS_FILE, 'r') as f:
        return json.load(f)

def save_bookings(bookings):
    with open(BOOKINGS_FILE, 'w') as f:
        json.dump(bookings, f)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if (username == 'yoni' and password == 'yoni') or (username == 'bita' and password == 'bita'):
        session['username'] = username
        return redirect(url_for('dashboard'))
    return render_template('login.html', error='Invalid credentials')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return render_template('dashboard.html', days=days)

@app.route('/get-bookings')
def get_bookings():
    bookings = load_bookings()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    valid_bookings = []
    
    for booking in bookings:
        # Ensure day is an integer
        if not isinstance(booking.get('day'), int):
            # Set a default day if day is null or invalid
            booking['day'] = 0  # Default to Monday
        if booking['day'] < 0 or booking['day'] >= len(days):
            booking['day'] = 0  # Default to Monday if day is out of range
        
        booking['day_name'] = days[booking['day']]
        valid_bookings.append(booking)
    
    return jsonify(valid_bookings)

@app.route('/book-slot', methods=['POST'])
def book_slot():
    data = request.get_json()
    username = session.get('username')
    
    if not username:
        return jsonify({'error': 'Unauthorized'}), 401
    
    bookings = load_bookings()
    
    if 'day' not in data or not data['day']:
        return jsonify({'error': 'Day is required'}), 400
    
    try:
        day = int(data.get('day'))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid day provided'}), 400
    
    if day < 0 or day >= 7:
        return jsonify({'error': 'Invalid day provided'}), 400
    
    # Check if user has already booked 3 days
    user_bookings = [b for b in bookings if b.get('username') == username]
    if len(user_bookings) >= 3:
        return jsonify({'error': 'You have already booked 3 days'}), 400
    
    # Check for time conflicts
    conflicts = [b for b in bookings if 
                 b.get('time') == data.get('time') and 
                 b.get('day') == day]
    
    if conflicts:
        return jsonify({'error': 'Time slot already booked'}), 400
    
    # Add new booking
    new_booking = {
        'username': username,
        'day': day,
        'time': data.get('time'),
        'note': data.get('note', '')
    }
    bookings.append(new_booking)
    save_bookings(bookings)
    
    return jsonify({
        'message': 'Booking successful',
        'booking': new_booking
    })
@app.route('/delete-booking', methods=['POST'])
def delete_booking():
    data = request.get_json()
    username = session.get('username')
    
    if not username:
        return jsonify({'error': 'Unauthorized'}), 401
    
    bookings = load_bookings()
    
    # Find the index of the booking to delete
    bookingIndex = -1
    for i, booking in enumerate(bookings):
        if booking['username'] == data['username'] and booking['day'] == data['day'] and booking['time'] == data['time']:
            bookingIndex = i
            break
    
    if bookingIndex == -1:
        return jsonify({'error': 'Booking not found'}), 404

    if bookings[bookingIndex]['username'] != username:
        return jsonify({'error': 'Unauthorized to delete this booking'}), 401
    
    # Delete the booking
    del bookings[bookingIndex]
    save_bookings(bookings)
    
    return jsonify({'message': 'Booking deleted successfully'})

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)