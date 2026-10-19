from flask import Blueprint, render_template, redirect, request, url_for
from db import fetch_all, fetch_one, execute

Passengers_bp = Blueprint(
    'Passengers',
    __name__,
    url_prefix='/Passenger'
)

@Passengers_bp.route('/')
def Display_Passenger():
    Passenger_Data = fetch_all('SELECT * FROM Passenger ORDER BY Passenger_ID')
    return render_template('Passenger.html', Passenger_Data=Passenger_Data)

@Passengers_bp.route('/add', methods=['POST'])
def Add_Passenger():
    First_Name = request.form['First_Name']
    Last_Name = request.form['Last_Name']
    Passport_Number = request.form['Passport_Number'] or None
    Nationality = request.form['Nationality']
    Contact_Number = request.form['Contact_Number']
    Email = request.form['Email']

    sql = '''INSERT INTO Passenger
             (First_Name, Last_Name, Passport_Number, Nationality, Contact_Number, Email)
             VALUES (%s, %s, %s, %s, %s, %s)'''
    execute(sql, (First_Name, Last_Name, Passport_Number, Nationality, Contact_Number, Email))
    return redirect(url_for('Passengers.Display_Passenger'))

@Passengers_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_Passenger(id):
    execute('DELETE FROM Passenger WHERE Passenger_ID = %s', (id,))
    return redirect(url_for('Passengers.Display_Passenger'))

@Passengers_bp.route('/update/<int:id>', methods=['GET', 'POST'])
def Update_Passenger(id):
    if request.method == 'POST':
        First_Name = request.form['First_Name']
        Last_Name = request.form['Last_Name']
        Passport_Number = request.form['Passport_Number'] or None
        Nationality = request.form['Nationality']
        Contact_Number = request.form['Contact_Number']
        Email = request.form['Email']

        sql = '''UPDATE Passenger
                 SET First_Name=%s, Last_Name=%s, Passport_Number=%s, Nationality=%s, Contact_Number=%s, Email=%s
                 WHERE Passenger_ID=%s'''
        execute(sql, (First_Name, Last_Name, Passport_Number, Nationality, Contact_Number, Email, id))
        return redirect(url_for('Passengers.Display_Passenger'))
    else:
        Passenger = fetch_one('SELECT * FROM Passenger WHERE Passenger_ID = %s', (id,))
        return render_template('Update/UpdatePassenger.html', Passenger=Passenger)


@Passengers_bp.route('/manifest', methods=['GET'])
def Flight_Passenger_Manifest():
    flight_id = request.args.get('flight_id', '')
    from_airport_id = request.args.get('from_airport_id', '')
    to_airport_id = request.args.get('to_airport_id', '')

    sql ='select * from Passenger_Manifest where 1=1 '
    params = []

    if flight_id:
        sql += ' AND Flight_ID = %s'
        params.append(flight_id)
    if from_airport_id:
        sql += ' AND From_Airport_ID = %s'
        params.append(from_airport_id)
    if to_airport_id:
        sql += ' AND  To_Airport_ID = %s'
        params.append(to_airport_id)

    sql += ' ORDER BY fi.Scheduled_Departure DESC, f.Flight_Number, b.Seat_Number'

    Manifest_Data = fetch_all(sql, tuple(params))
    Flight_List = fetch_all('SELECT Flight_ID, Flight_Number FROM Flight ORDER BY Flight_Number')
    Airport_List = fetch_all('SELECT Airport_ID, Airport_Name, IATA_Code, Airport_City FROM Airport ORDER BY Airport_City')

    return render_template(
        'PassengerManifest.html',
        Manifest_Data=Manifest_Data,
        Flight_List=Flight_List,
        Airport_List=Airport_List,
        selected_flight=flight_id,
        selected_from=from_airport_id,
        selected_to=to_airport_id
    )