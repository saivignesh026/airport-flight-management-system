"""Ticket reservations and payments. Airport check-in is handled separately."""
from decimal import Decimal, InvalidOperation
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from db import fetch_all, fetch_one, execute, transaction, is_restricted_delete_error

Bookings_bp = Blueprint('Bookings', __name__, url_prefix='/Booking')
Booking_Status_Enum = ('Pending', 'Confirmed', 'Cancelled', 'Refunded')
Class_Enum = ('Economy', 'Business', 'First')
Payment_Method_Enum = ('UPI', 'Credit Card', 'Debit Card', 'Net Banking')
Payment_Status_Enum = ('Pending', 'Payment Received', 'Failed', 'Refunded')

# Pick one payment explicitly; older databases may contain multiple attempts.
BOOKING_QUERY = '''
    SELECT b.*, CONCAT(p.First_Name, ' ', p.Last_Name) AS Passenger_Name,
           p.Passport_Number, f.Flight_Number, fi.Scheduled_Departure,
           py.Payment_Method, py.Payment_Status, py.Transaction_Reference
    FROM Booking b
    JOIN Passenger p ON p.Passenger_ID = b.Passenger_ID
    JOIN Flight_Instance fi ON fi.Instance_ID = b.Instance_ID
    JOIN Flight f ON f.Flight_ID = fi.Flight_ID
    LEFT JOIN Payment py ON py.Payment_ID =
        (SELECT MAX(p2.Payment_ID) FROM Payment p2 WHERE p2.Booking_ID = b.Booking_ID)
'''


def choices():
    return dict(
        Passenger_Data=fetch_all('SELECT Passenger_ID, First_Name, Last_Name, Email FROM Passenger ORDER BY First_Name, Last_Name'),
        Instance_Data=fetch_all('''SELECT fi.Instance_ID, f.Flight_Number,
            fi.Scheduled_Departure FROM Flight_Instance fi
            JOIN Flight f ON f.Flight_ID = fi.Flight_ID
            WHERE fi.Flight_Instance_Status NOT IN ('Cancelled', 'Departed', 'Arrived')
            ORDER BY fi.Scheduled_Departure DESC'''),
        Booking_Status_Enum=Booking_Status_Enum, Class_Enum=Class_Enum,
        Payment_Method_Enum=Payment_Method_Enum, Payment_Status_Enum=Payment_Status_Enum,
    )


def required(name, limit=100):
    value = request.form.get(name, '').strip()
    if not value or len(value) > limit:
        raise ValueError(f'{name.replace("_", " ")} is required (maximum {limit} characters).')
    return value


def choice(name, values):
    value = required(name)
    if value not in values:
        raise ValueError(f'Invalid {name.replace("_", " ")}.')
    return value


def amount(name):
    try:
        value = Decimal(required(name))
    except InvalidOperation:
        raise ValueError(f'Invalid {name.replace("_", " ")}.') from None
    if not value.is_finite() or value < 0 or value > Decimal('99999999.99') or value != value.quantize(Decimal('.01')):
        raise ValueError(f'{name.replace("_", " ")} must be a non-negative amount with at most two decimal places.')
    return value


def ticket_fields():
    instance = int(required('Instance_ID'))
    if instance <= 0:
        raise ValueError('Select a valid flight schedule.')
    return (choice('Booking_Status', Booking_Status_Enum), amount('Booking_Price'),
            required('Seat_Number', 3).upper(), choice('Class', Class_Enum), instance)


def payment_fields():
    return (choice('Payment_Method', Payment_Method_Enum),
            choice('Payment_Status', Payment_Status_Enum),
            request.form.get('Transaction_Reference', '').strip() or None)


def lock_schedule(cur, instance):
    cur.execute('SELECT Flight_Instance_Status FROM Flight_Instance WHERE Instance_ID=%s FOR UPDATE', (instance,))
    flight = cur.fetchone()
    if not flight or flight['Flight_Instance_Status'] in ('Cancelled', 'Departed', 'Arrived'):
        raise ValueError('This flight schedule is no longer available for booking.')


@Bookings_bp.route('/')
def Display_Booking():
    return render_template('Booking.html', Booking_Data=fetch_all(BOOKING_QUERY + ' ORDER BY b.Booking_ID DESC'), **choices())


@Bookings_bp.route('/add', methods=['POST'])
def Add_Booking():
    try:
        status, price, seat, cabin, instance = ticket_fields()
        payment = payment_fields()
        passenger_id = request.form.get('Passenger_ID', '').strip()
        if passenger_id:
            passenger_id = int(passenger_id)
            if passenger_id <= 0:
                raise ValueError('Select a valid passenger.')
        else:
            passenger = (required('First_Name'), required('Last_Name'),
                         request.form.get('Passport_Number', '').strip() or None,
                         required('Nationality'), required('Contact_Number'), required('Email'))
        with transaction() as cur:
            lock_schedule(cur, instance)
            if not passenger_id:
                cur.execute('''INSERT INTO Passenger
                    (First_Name, Last_Name, Passport_Number, Nationality, Contact_Number, Email)
                    VALUES (%s, %s, %s, %s, %s, %s)''', passenger)
                passenger_id = cur.lastrowid
            cur.execute('''INSERT INTO Booking
                (Booking_Date, Booking_Status, Booking_Price, Seat_Number, Class, Passenger_ID, Instance_ID)
                VALUES (NOW(), %s, %s, %s, %s, %s, %s)''',
                (status, price, seat, cabin, passenger_id, instance))
            booking_id = cur.lastrowid
            cur.execute('''INSERT INTO Payment
                (Booking_ID, Amount, Payment_Date, Payment_Method, Payment_Status, Transaction_Reference)
                VALUES (%s, %s, NOW(), %s, %s, %s)''', (booking_id, price, *payment))
        flash(f'Booking #{booking_id} created. Complete check-in separately when the passenger arrives.', 'success')
    except Exception as exc:
        flash(f'Failed to add booking: {exc}', 'danger')
    return redirect(url_for('Bookings.Display_Booking'))


@Bookings_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_Booking(id):
    try:
        execute('CALL Delete_Booking(%s)', (id,))
        flash('Booking deleted successfully.', 'success')
    except Exception as exc:
        if is_restricted_delete_error(exc):
            flash('Cannot delete this booking because related records exist.', 'danger')
        else:
            flash(f'Failed to delete booking: {exc}', 'danger')
    return redirect(url_for('Bookings.Display_Booking'))


@Bookings_bp.route('/update/<int:id>', methods=['GET', 'POST'])
def Update_Booking(id):
    booking = fetch_one(BOOKING_QUERY + ' WHERE b.Booking_ID=%s', (id,))
    if booking is None:
        abort(404)
    if request.method == 'POST':
        try:
            status, price, seat, cabin, instance = ticket_fields()
            payment = payment_fields()
            with transaction() as cur:
                lock_schedule(cur, instance)
                cur.execute('SELECT Booking_ID FROM Booking WHERE Booking_ID=%s FOR UPDATE', (id,))
                if not cur.fetchone():
                    raise ValueError('Booking no longer exists.')
                cur.execute('SELECT CheckIn_Status FROM Check_In WHERE Booking_ID=%s', (id,))
                checkin = cur.fetchone()
                if checkin and checkin['CheckIn_Status'] == 'Checked-In':
                    raise ValueError('A checked-in booking cannot be edited. Update check-in first.')
                cur.execute('''UPDATE Booking SET Booking_Status=%s, Booking_Price=%s,
                    Seat_Number=%s, Class=%s, Instance_ID=%s WHERE Booking_ID=%s''',
                    (status, price, seat, cabin, instance, id))
                cur.execute('SELECT Payment_ID FROM Payment WHERE Booking_ID=%s ORDER BY Payment_ID DESC LIMIT 1', (id,))
                existing = cur.fetchone()
                if existing:
                    cur.execute('''UPDATE Payment SET Amount=%s, Payment_Method=%s,
                        Payment_Status=%s, Transaction_Reference=%s WHERE Payment_ID=%s''',
                        (price, *payment, existing['Payment_ID']))
                else:
                    cur.execute('''INSERT INTO Payment (Booking_ID, Amount, Payment_Date,
                        Payment_Method, Payment_Status, Transaction_Reference)
                        VALUES (%s, %s, NOW(), %s, %s, %s)''', (id, price, *payment))
            flash('Booking updated successfully.', 'success')
            return redirect(url_for('Bookings.Display_Booking'))
        except Exception as exc:
            flash(f'Failed to update booking: {exc}', 'danger')
    data = choices()
    # Retain the current schedule in the edit form even if it is no longer bookable.
    if not any(row['Instance_ID'] == booking['Instance_ID'] for row in data['Instance_Data']):
        data['Instance_Data'].append(booking)
    return render_template('Update/UpdateBooking.html', Booking=booking, **data)
