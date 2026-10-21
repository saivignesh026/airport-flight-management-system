from flask import Blueprint, render_template, redirect, request, url_for, flash
from db import fetch_all, fetch_one, execute

Flights_bp = Blueprint(
    'Flights',
    __name__,
    url_prefix='/Flight'
)

Status_Enum = ('Scheduled', 'Delayed', 'Cancelled')

@Flights_bp.route('/')
def Display_Flight():
    sql ='select * from Flight_Details'
    Flight_Data = fetch_all(sql)
    Airline_Data = fetch_all('SELECT Airline_ID, Name FROM Airline')
    Airport_Data = fetch_all('SELECT Airport_ID, Airport_Name, IATA_Code FROM Airport')
    return render_template(
        'Flight.html',
        Flight_Data=Flight_Data,
        Airline_Data=Airline_Data,
        Airport_Data=Airport_Data,
        Status_Enum=Status_Enum
    )

@Flights_bp.route('/add', methods=['POST'])
def Add_Flight():
    try:
        Flight_Number = request.form['Flight_Number']
        Airline_ID = request.form['Airline_ID']
        Departure_Airport_ID = request.form['Departure_Airport_ID']
        Arrival_Airport_ID = request.form['Arrival_Airport_ID']
        Scheduled_Departure_Time = request.form['Scheduled_Departure_Time']
        Scheduled_Arrival_Time = request.form['Scheduled_Arrival_Time']
        Status = request.form['Status']

        sql = 'CALL Add_Flight(%s, %s, %s, %s, %s, %s, %s)'
        params = (Flight_Number, Airline_ID, Departure_Airport_ID, Arrival_Airport_ID, Scheduled_Departure_Time, Scheduled_Arrival_Time, Status)
        execute(sql, params)
        flash(f'Flight "{Flight_Number}" was successfully added.', 'success')
    except Exception as e:
        flash(f'Failed to add flight: {str(e)}', 'danger')
    return redirect(url_for('Flights.Display_Flight'))

@Flights_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_Flight(id):
    try:
        execute('CALL Delete_Flight(%s)', (id,))
        flash('Flight deleted successfully.', 'success')
    except Exception as e:
        flash(f'Failed to delete flight: {str(e)}', 'danger')
    return redirect(url_for('Flights.Display_Flight'))

@Flights_bp.route('/update/<int:id>', methods=['GET', 'POST'])
def Update_Flight(id):
    if request.method == 'POST':
        try:
            Flight_Number = request.form['Flight_Number']
            Airline_ID = request.form['Airline_ID']
            Departure_Airport_ID = request.form['Departure_Airport_ID']
            Arrival_Airport_ID = request.form['Arrival_Airport_ID']
            Scheduled_Departure_Time = request.form['Scheduled_Departure_Time']
            Scheduled_Arrival_Time = request.form['Scheduled_Arrival_Time']
            Status = request.form['Status']

            sql = '''UPDATE Flight
                     SET Flight_Number=%s, Airline_ID=%s, Departure_Airport_ID=%s, Arrival_Airport_ID=%s,
                         Scheduled_Departure_Time=%s, Scheduled_Arrival_Time=%s, Status=%s
                     WHERE Flight_ID=%s'''
            params = (Flight_Number, Airline_ID, Departure_Airport_ID, Arrival_Airport_ID, Scheduled_Departure_Time, Scheduled_Arrival_Time, Status, id)
            execute(sql, params)
            flash(f'Flight "{Flight_Number}" updated successfully.', 'success')
            return redirect(url_for('Flights.Display_Flight'))
        except Exception as e:
            flash(f'Failed to update flight: {str(e)}', 'danger')
            return redirect(url_for('Flights.Update_Flight', id=id))
    else:
        Flight_To_Edit = fetch_one('CALL Flight_To_Edit(%s)', (id,))
        Airline_Data = fetch_all('SELECT Airline_ID, Name FROM Airline')
        Airport_Data = fetch_all('SELECT Airport_ID, Airport_Name, IATA_Code FROM Airport')
        return render_template(
            'Update/UpdateFlight.html',
            Flight=Flight_To_Edit,
            Airline_Data=Airline_Data,
            Airport_Data=Airport_Data,
            Status_Enum=Status_Enum
        )