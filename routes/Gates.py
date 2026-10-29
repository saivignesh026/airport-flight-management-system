from flask import abort, Blueprint, render_template, redirect, request, url_for, flash
from db import fetch_all, fetch_one, execute, is_restricted_delete_error

Gates_bp = Blueprint(
    'Gates',
    __name__,
    url_prefix='/Gate'
)

Status_Enum = ('Open', 'Closed', 'Maintenance')


@Gates_bp.route('/')
def Display_Gate():
    sql = 'select * from Gate_Details'
    Gate_Data = fetch_all(sql)
    Terminal_Data = fetch_all('select Terminal_ID, Terminal_Name, Terminal_Number from Terminal')
    return render_template('Gate.html', Gate_Data=Gate_Data, Terminal_Data=Terminal_Data, Status_Enum=Status_Enum)


@Gates_bp.route('/add', methods=['POST'])
def Add_Gate():
    try:
        Gate_Number = request.form['Gate_Number']
        Gate_Status = request.form['Gate_Status']
        Terminal_ID = request.form.get('Terminal_ID') or None

        params = (Gate_Number, Gate_Status, Terminal_ID)
        sql = 'CALL Add_Gate(%s, %s, %s)'
        execute(sql, params)
        flash(f'Gate "{Gate_Number}" was successfully added.', 'success')
    except Exception as e:
        flash(f'Failed to add gate: {str(e)}', 'danger')

    return redirect(url_for('Gates.Display_Gate'))


@Gates_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_Gate(id):
    if request.method == 'POST':
        try:
            sql = 'CALL Delete_Gate(%s)'
            params = (id,)
            execute(sql, params)
            flash('Gate deleted successfully.', 'success')
        except Exception as e:
            if is_restricted_delete_error(e):
                flash('Cannot delete this gate because related flight instances exist. Delete or reassign them first.', 'danger')
            else:
                flash(f'Failed to delete gate: {str(e)}', 'danger')
        return redirect(url_for('Gates.Display_Gate'))


@Gates_bp.route('/update/<int:id>', methods=['POST', 'GET'])
def Update_Gate(id):
    if request.method == 'POST':
        try:
            Gate_Number = request.form['Gate_Number']
            Gate_Status = request.form['Gate_Status']
            Terminal_ID = request.form.get('Terminal_ID') or None

            params = (Gate_Number, Gate_Status, Terminal_ID, id)
            sql = 'CALL Update_Gate(%s, %s, %s, %s)'
            execute(sql, params)
            flash(f'Gate "{Gate_Number}" updated successfully.', 'success')
            return redirect(url_for('Gates.Display_Gate'))
        except Exception as e:
            flash(f'Failed to update gate: {str(e)}', 'danger')
            return redirect(url_for('Gates.Update_Gate', id=id))

    else:
        Gate_To_Edit = fetch_one('CALL Gate_To_Edit(%s)', (id,))
        if Gate_To_Edit is None:
            abort(404)
        Terminal_Data = fetch_all('select Terminal_ID, Terminal_Name, Terminal_Number from Terminal')
        return render_template('Update/UpdateGate.html', Gate=Gate_To_Edit, Terminal_Data=Terminal_Data, Status_Enum=Status_Enum)
