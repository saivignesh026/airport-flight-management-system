from flask import abort, Blueprint, render_template, redirect, request, url_for, flash
from db import fetch_all, fetch_one, execute, is_restricted_delete_error

Aircrafts_bp = Blueprint(
    'Aircrafts',
    __name__,
    url_prefix='/Aircraft'
)

@Aircrafts_bp.route('/')
def Display_Aircraft():
    sql = 'SELECT * from Aircraft_Details;'
    Aircraft_Data = fetch_all(sql)
    Airline_Data = fetch_all('select Name, Airline_ID from Airline')
    return render_template('Aircraft.html', Aircraft_Data=Aircraft_Data, Airline_Data=Airline_Data)


@Aircrafts_bp.route('/add', methods=['POST'])
def Add_Aircraft():
    try:
        Tail_Number = request.form['Tail_Number']
        Model = request.form['Model']
        Capacity = request.form['Capacity']
        Airline_ID = request.form['Airline_ID']

        params = (Tail_Number, Model, Capacity, Airline_ID)
        sql = 'CALL Add_Aircraft(%s, %s, %s, %s)'
        execute(sql, params)
        flash(f'Aircraft "{Tail_Number}" was successfully added.', 'success')
    except Exception as e:
        flash(f'Failed to add aircraft: {str(e)}', 'danger')

    return redirect(url_for('Aircrafts.Display_Aircraft'))


@Aircrafts_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_Aircraft(id):
    try:
        sql = 'CALL Delete_Aircraft(%s)'
        params = (id,)
        execute(sql, params)
        flash('Aircraft deleted successfully.', 'success')
    except Exception as e:
        if is_restricted_delete_error(e):
            flash('Cannot delete this aircraft because related flight instances exist. Delete or reassign them first.', 'danger')
        else:
            flash(f'Failed to delete aircraft: {str(e)}', 'danger')

    return redirect(url_for('Aircrafts.Display_Aircraft'))


@Aircrafts_bp.route('/update/<int:id>', methods=['POST', 'GET'])
def Update_Aircraft(id):
    if request.method == 'POST':
        try:
            Tail_Number = request.form['Tail_Number']
            Model = request.form['Model']
            Capacity = request.form['Capacity']
            Airline_ID = request.form['Airline_ID']

            params = (Tail_Number, Model, Capacity, Airline_ID, id)
            sql = 'CALL Update_Aircraft(%s, %s, %s, %s, %s)'
            execute(sql, params)
            flash(f'Aircraft "{Tail_Number}" updated successfully.', 'success')
            return redirect(url_for('Aircrafts.Display_Aircraft'))
        except Exception as e:
            flash(f'Failed to update aircraft: {str(e)}', 'danger')
            return redirect(url_for('Aircrafts.Update_Aircraft', id=id))

    else:
        sql = 'CALL Aircraft_To_Edit(%s)'
        params = (id,)
        Aircraft_To_Edit = fetch_one(sql, params)
        if Aircraft_To_Edit is None:
            abort(404)
        Airline_Data = fetch_all('select Name, Airline_ID from Airline')
        return render_template('Update/UpdateAircraft.html', Airline_Data=Airline_Data, Aircraft=Aircraft_To_Edit)
