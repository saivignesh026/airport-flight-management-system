from flask import Blueprint, render_template, redirect, request, url_for, flash
from db import fetch_all, fetch_one, transaction, is_restricted_delete_error
from datetime import datetime

Bookings_bp = Blueprint(
    'Bookings',
    __name__,
    url_prefix='/Booking'
)

Booking_Status_Enum = ('Pending', 'Confirmed', 'Cancelled', 'Refunded')
Class_Enum = ('Economy', 'Business', 'First')
Payment_Method_Enum = ('UPI', 'Credit Card', 'Debit Card', 'Net Banking')
Payment_Status_Enum = ('Pending', 'Payment Received', 'Failed', 'Refunded')
CheckIn_Status_Enum = ('Pending', 'Checked-In', 'No Show')
Boarding_Status_Enum = ('Not Boarded', 'Boarding', 'Boarded')
Baggage_Type_Enum = ('Checked', 'Cabin')
Baggage_Status_Enum = ('Checked-In', 'Screened', 'Sorted', 'Loaded', 'In-Transit', 'Unloaded', 'Claimed', 'Lost')

@Bookings_bp.route('/')
def Display_Booking():
    sql ='select * from Booking_Details;'
    Booking_Data = fetch_all(sql)
    Passenger_Data = fetch_all('SELECT Passenger_ID, First_Name, Last_Name, Passport_Number FROM Passenger')
    Instance_Data = fetch_all('''
        SELECT fi.Instance_ID, f.Flight_Number, fi.Scheduled_Departure
        FROM Flight_Instance fi
        JOIN Flight f ON fi.Flight_ID = f.Flight_ID
        ORDER BY fi.Scheduled_Departure DESC
    ''')
    return render_template(
        'Booking.html',
        Booking_Data=Booking_Data,
        Passenger_Data=Passenger_Data,
        Instance_Data=Instance_Data,
        Booking_Status_Enum=Booking_Status_Enum,
        Class_Enum=Class_Enum,
        Payment_Method_Enum=Payment_Method_Enum,
        Payment_Status_Enum=Payment_Status_Enum,
        CheckIn_Status_Enum=CheckIn_Status_Enum,
        Boarding_Status_Enum=Boarding_Status_Enum,
        Baggage_Type_Enum=Baggage_Type_Enum,
        Baggage_Status_Enum=Baggage_Status_Enum
    )

@Bookings_bp.route('/add', methods=['POST'])
def Add_Booking():
    try:
        Passenger_ID = request.form['Passenger_ID']
        Instance_ID = request.form['Instance_ID']
        Seat_Number = request.form['Seat_Number']
        Class = request.form['Class']
        Booking_Price = request.form['Booking_Price']
        Booking_Status = request.form['Booking_Status']

        Payment_Method = request.form['Payment_Method']
        Payment_Status = request.form['Payment_Status']
        Transaction_Reference = request.form.get('Transaction_Reference') or None

        CheckIn_Status = request.form['CheckIn_Status']
        Boarding_Status = request.form['Boarding_Status']

        Baggage_Type = request.form['Baggage_Type']
        Weight_KG = request.form.get('Weight_KG') or 0.00
        Baggage_Status = request.form['Baggage_Status']

        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with transaction() as cur:
            cur.callproc('Add_Booking', (
                Booking_Status, Booking_Price, Seat_Number, Class, Passenger_ID, Instance_ID
            ))
            for result in cur.stored_results():
                result.fetchall()

            cur.execute('SELECT LAST_INSERT_ID() AS Booking_ID')
            booking_id = cur.fetchone()['Booking_ID']

            cur.callproc('Add_Payment', (
                booking_id, Booking_Price, now_str, Payment_Method, Payment_Status, Transaction_Reference
            ))
            for result in cur.stored_results():
                result.fetchall()

            cur.callproc('Add_Check_In', (
                booking_id, now_str, CheckIn_Status, Boarding_Status
            ))
            for result in cur.stored_results():
                result.fetchall()

            cur.callproc('Add_Baggage', (
                Weight_KG, Baggage_Type, Baggage_Status, booking_id
            ))
            for result in cur.stored_results():
                result.fetchall()
        flash('Booking was successfully added.', 'success')
    except Exception as e:
        flash(f'Failed to add booking: {str(e)}', 'danger')

    return redirect(url_for('Bookings.Display_Booking'))

@Bookings_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_Booking(id):
    try:
        with transaction() as cur:
            cur.callproc('Delete_Booking', (id,))
            for result in cur.stored_results():
                result.fetchall()
        flash('Booking deleted successfully.', 'success')
    except Exception as e:
        if is_restricted_delete_error(e):
            flash('Cannot delete this booking because related payment, check-in, or baggage records exist. Delete them first.', 'danger')
        else:
            flash(f'Failed to delete booking: {str(e)}', 'danger')
    return redirect(url_for('Bookings.Display_Booking'))

@Bookings_bp.route('/update/<int:id>', methods=['GET', 'POST'])
def Update_Booking(id):
    if request.method == 'POST':
        try:
            Passenger_ID = request.form['Passenger_ID']
            Instance_ID = request.form['Instance_ID']
            Seat_Number = request.form['Seat_Number']
            Class = request.form['Class']
            Booking_Price = request.form['Booking_Price']
            Booking_Status = request.form['Booking_Status']

            Payment_Method = request.form['Payment_Method']
            Payment_Status = request.form['Payment_Status']
            Transaction_Reference = request.form.get('Transaction_Reference') or None

            CheckIn_Status = request.form['CheckIn_Status']
            Boarding_Status = request.form['Boarding_Status']

            Baggage_Type = request.form['Baggage_Type']
            Weight_KG = request.form.get('Weight_KG') or 0.00
            Baggage_Status = request.form['Baggage_Status']

            params = (
                Passenger_ID, Instance_ID, Seat_Number, Class, Booking_Price, Booking_Status,
                Payment_Method, Payment_Status, Transaction_Reference, CheckIn_Status,
                Boarding_Status, Baggage_Type, Weight_KG, Baggage_Status, id
            )
            execute(
                'CALL Update_Booking(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                params
            )

            flash('Booking updated successfully.', 'success')
            return redirect(url_for('Bookings.Display_Booking'))
        except Exception as e:
            flash(f'Failed to update booking: {str(e)}', 'danger')
            return redirect(url_for('Bookings.Update_Booking', id=id))
    else:
        Booking = fetch_one('CALL Booking_To_Edit(%s)', (id,))
        Passenger_Data = fetch_all('SELECT Passenger_ID, First_Name, Last_Name, Passport_Number FROM Passenger')
        Instance_Data = fetch_all('''
            SELECT fi.Instance_ID, f.Flight_Number, fi.Scheduled_Departure
            FROM Flight_Instance fi
            JOIN Flight f ON fi.Flight_ID = f.Flight_ID
        ''')
        return render_template(
            'Update/UpdateBooking.html',
            Booking=Booking,
            Passenger_Data=Passenger_Data,
            Instance_Data=Instance_Data,
            Booking_Status_Enum=Booking_Status_Enum,
            Class_Enum=Class_Enum,
            Payment_Method_Enum=Payment_Method_Enum,
            Payment_Status_Enum=Payment_Status_Enum,
            CheckIn_Status_Enum=CheckIn_Status_Enum,
            Boarding_Status_Enum=Boarding_Status_Enum,
            Baggage_Type_Enum=Baggage_Type_Enum,
            Baggage_Status_Enum=Baggage_Status_Enum
        )
