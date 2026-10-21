from flask import Blueprint, render_template, redirect, request, url_for, flash
from db import fetch_all, fetch_one, execute

Flight_Instances_bp = Blueprint(
    'Flight_Instances',
    __name__,
    url_prefix='/FlightInstance'
)

Instance_Status_Enum = ('On Time', 'Scheduled', 'Delayed', 'Boarding', 'Departed', 'Arrived', 'Cancelled')

@Flight_Instances_bp.route('/')
def Display_Flight_Instance():
    Instance_Data = fetch_all('SELECT * FROM Flight_Operational_Details ORDER BY Instance_ID')
    Flight_Data = fetch_all('SELECT Flight_ID, Flight_Number FROM Flight')
    Aircraft_Data = fetch_all('SELECT Aircraft_ID, Tail_Number, Model FROM Aircraft')
    Gate_Data = fetch_all('SELECT Gate_ID, Gate_Number FROM Gate')
    Runway_Data = fetch_all('SELECT Runway_ID, Runway_Code FROM Runway')
    return render_template(
        'FlightInstance.html',
        Instance_Data=Instance_Data,
        Flight_Data=Flight_Data,
        Aircraft_Data=Aircraft_Data,
        Gate_Data=Gate_Data,
        Runway_Data=Runway_Data,
        Status_Enum=Instance_Status_Enum
    )

@Flight_Instances_bp.route('/add', methods=['POST'])
def Add_Flight_Instance():
    try:
        Flight_ID = request.form.get('Flight_ID') or None
        Aircraft_ID = request.form.get('Aircraft_ID') or None
        Gate_ID = request.form.get('Gate_ID') or None
        Runway_ID = request.form.get('Runway_ID') or None
        Scheduled_Departure = request.form['Scheduled_Departure']
        Scheduled_Arrival = request.form['Scheduled_Arrival']
        Actual_Departure = request.form.get('Actual_Departure') or None
        Actual_Arrival = request.form.get('Actual_Arrival') or None
        Flight_Instance_Status = request.form['Flight_Instance_Status']

        sql = '''INSERT INTO Flight_Instance
                 (Scheduled_Departure, Scheduled_Arrival, Actual_Departure, Actual_Arrival,
                  Flight_Instance_Status, Flight_ID, Aircraft_ID, Gate_ID, Runway_ID)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        params = (
            Scheduled_Departure, Scheduled_Arrival, Actual_Departure, Actual_Arrival,
            Flight_Instance_Status, Flight_ID, Aircraft_ID, Gate_ID, Runway_ID
        )
        execute(sql, params)
        flash('Flight instance was successfully added.', 'success')
    except Exception as e:
        flash(f'Failed to add flight instance: {str(e)}', 'danger')
    return redirect(url_for('Flight_Instances.Display_Flight_Instance'))

@Flight_Instances_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_Flight_Instance(id):
    try:
        execute('DELETE FROM Flight_Instance WHERE Instance_ID = %s', (id,))
        flash('Flight instance deleted successfully.', 'success')
    except Exception as e:
        flash(f'Failed to delete flight instance: {str(e)}', 'danger')
    return redirect(url_for('Flight_Instances.Display_Flight_Instance'))

@Flight_Instances_bp.route('/update/<int:id>', methods=['GET', 'POST'])
def Update_Flight_Instance(id):
    if request.method == 'POST':
        try:
            Flight_ID = request.form.get('Flight_ID') or None
            Aircraft_ID = request.form.get('Aircraft_ID') or None
            Gate_ID = request.form.get('Gate_ID') or None
            Runway_ID = request.form.get('Runway_ID') or None
            Scheduled_Departure = request.form['Scheduled_Departure']
            Scheduled_Arrival = request.form['Scheduled_Arrival']
            Actual_Departure = request.form.get('Actual_Departure') or None
            Actual_Arrival = request.form.get('Actual_Arrival') or None
            Flight_Instance_Status = request.form['Flight_Instance_Status']

            sql = '''UPDATE Flight_Instance
                     SET Scheduled_Departure=%s, Scheduled_Arrival=%s, Actual_Departure=%s, Actual_Arrival=%s,
                         Flight_Instance_Status=%s, Flight_ID=%s, Aircraft_ID=%s, Gate_ID=%s, Runway_ID=%s
                     WHERE Instance_ID=%s'''
            params = (
                Scheduled_Departure, Scheduled_Arrival, Actual_Departure, Actual_Arrival,
                Flight_Instance_Status, Flight_ID, Aircraft_ID, Gate_ID, Runway_ID, id
            )
            execute(sql, params)
            flash('Flight instance updated successfully.', 'success')
            return redirect(url_for('Flight_Instances.Display_Flight_Instance'))
        except Exception as e:
            flash(f'Failed to update flight instance: {str(e)}', 'danger')
            return redirect(url_for('Flight_Instances.Update_Flight_Instance', id=id))
    else:
        Instance = fetch_one('SELECT * FROM Flight_Instance WHERE Instance_ID = %s', (id,))
        Flight_Data = fetch_all('SELECT Flight_ID, Flight_Number FROM Flight')
        Aircraft_Data = fetch_all('SELECT Aircraft_ID, Tail_Number, Model FROM Aircraft')
        Gate_Data = fetch_all('SELECT Gate_ID, Gate_Number FROM Gate')
        Runway_Data = fetch_all('SELECT Runway_ID, Runway_Code FROM Runway')
        return render_template(
            'Update/UpdateFlightInstance.html',
            Instance=Instance,
            Flight_Data=Flight_Data,
            Aircraft_Data=Aircraft_Data,
            Gate_Data=Gate_Data,
            Runway_Data=Runway_Data,
            Status_Enum=Instance_Status_Enum
        )