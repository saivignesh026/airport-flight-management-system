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
        return render_template('UpdatePassenger.html', Passenger=Passenger)