from flask import Blueprint, render_template, redirect, request, url_for
from db import fetch_all, fetch_one, transaction
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
        cur.execute('''
            INSERT INTO Booking (Booking_Date, Booking_Status, Booking_Price, Seat_Number, Class, Passenger_ID, Instance_ID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (now_str, Booking_Status, Booking_Price, Seat_Number, Class, Passenger_ID, Instance_ID))
        booking_id = cur.lastrowid

        cur.execute('''
            INSERT INTO Payment (Booking_ID, Amount, Payment_Date, Payment_Method, Payment_Status, Transaction_Reference)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (booking_id, Booking_Price, now_str, Payment_Method, Payment_Status, Transaction_Reference))

        cur.execute('''
            INSERT INTO Check_In (Booking_ID, CheckIn_Time, CheckIn_Status, Boarding_Status)
            VALUES (%s, %s, %s, %s)
        ''', (booking_id, now_str, CheckIn_Status, Boarding_Status))

        cur.execute('''
            INSERT INTO Baggage (Weight_KG, Baggage_Type, Baggage_Status, Booking_ID)
            VALUES (%s, %s, %s, %s)
        ''', (Weight_KG, Baggage_Type, Baggage_Status, booking_id))

    return redirect(url_for('Bookings.Display_Booking'))

@Bookings_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_Booking(id):
    with transaction() as cur:
        cur.execute('DELETE FROM Baggage WHERE Booking_ID = %s', (id,))
        cur.execute('DELETE FROM Check_In WHERE Booking_ID = %s', (id,))
        cur.execute('DELETE FROM Payment WHERE Booking_ID = %s', (id,))
        cur.execute('DELETE FROM Booking WHERE Booking_ID = %s', (id,))
    return redirect(url_for('Bookings.Display_Booking'))

@Bookings_bp.route('/update/<int:id>', methods=['GET', 'POST'])
def Update_Booking(id):
    if request.method == 'POST':
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

        with transaction() as cur:
            cur.execute('''
                UPDATE Booking
                SET Booking_Status=%s, Booking_Price=%s, Seat_Number=%s, Class=%s, Passenger_ID=%s, Instance_ID=%s
                WHERE Booking_ID=%s
            ''', (Booking_Status, Booking_Price, Seat_Number, Class, Passenger_ID, Instance_ID, id))

            cur.execute('''
                UPDATE Payment
                SET Amount=%s, Payment_Method=%s, Payment_Status=%s, Transaction_Reference=%s
                WHERE Booking_ID=%s
            ''', (Booking_Price, Payment_Method, Payment_Status, Transaction_Reference, id))

            cur.execute('''
                UPDATE Check_In
                SET CheckIn_Status=%s, Boarding_Status=%s
                WHERE Booking_ID=%s
            ''', (CheckIn_Status, Boarding_Status, id))

            cur.execute('''
                UPDATE Baggage
                SET Weight_KG=%s, Baggage_Type=%s, Baggage_Status=%s
                WHERE Booking_ID=%s
            ''', (Weight_KG, Baggage_Type, Baggage_Status, id))

        return redirect(url_for('Bookings.Display_Booking'))
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