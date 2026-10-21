from flask import Blueprint, render_template, redirect, request, url_for, flash
from db import fetch_all, fetch_one, execute

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
        sql = 'insert into Gate (Gate_Number, Gate_Status, Terminal_ID) values (%s, %s, %s)'
        execute(sql, params)
        flash(f'Gate "{Gate_Number}" was successfully added.', 'success')
    except Exception as e:
        flash(f'Failed to add gate: {str(e)}', 'danger')

    return redirect(url_for('Gates.Display_Gate'))


@Gates_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_Gate(id):
    if request.method == 'POST':
        try:
            sql = 'delete from Gate where Gate_ID = %s'
            params = (id,)
            execute(sql, params)
            flash('Gate deleted successfully.', 'success')
        except Exception as e:
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
            sql = 'update Gate set Gate_Number=%s, Gate_Status=%s, Terminal_ID=%s where Gate_ID=%s'
            execute(sql, params)
            flash(f'Gate "{Gate_Number}" updated successfully.', 'success')
            return redirect(url_for('Gates.Display_Gate'))
        except Exception as e:
            flash(f'Failed to update gate: {str(e)}', 'danger')
            return redirect(url_for('Gates.Update_Gate', id=id))

    else:
        sql = 'select Gate_ID, Gate_Number, Gate_Status, Terminal_ID \
               from Gate \
               where Gate_ID = %s'
        params = (id,)
        Gate_To_Edit = fetch_one(sql, params)
        Terminal_Data = fetch_all('select Terminal_ID, Terminal_Name, Terminal_Number from Terminal')
        return render_template('Update/UpdateGate.html', Gate=Gate_To_Edit, Terminal_Data=Terminal_Data, Status_Enum=Status_Enum)