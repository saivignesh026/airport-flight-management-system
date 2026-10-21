from flask import Blueprint, render_template, redirect, request, url_for, flash
from db import fetch_all, fetch_one, execute

Terminals_bp = Blueprint(
    'Terminals',
    __name__,
    url_prefix='/Terminal'
)

Status_Enum = ('Operational', 'Under Construction', 'Closed')


@Terminals_bp.route('/')
def Display_Terminal():
    sql = 'SELECT * from Terminal_Details'
    Terminal_Data = fetch_all(sql)
    Airport_Data = fetch_all('select Airport_Name, Airport_ID from Airport')
    return render_template('Terminal.html', Terminal_Data=Terminal_Data, Airport_Data=Airport_Data, Status_Enum=Status_Enum)


@Terminals_bp.route('/add', methods=['POST'])
def Add_Terminal():
    try:
        Terminal_Number = request.form.get('Terminal_Number')
        Terminal_Name = request.form['Terminal_Name']
        Terminal_Status = request.form['Terminal_Status']
        Airport_ID = request.form['Airport_ID']

        params = (Terminal_Number, Terminal_Name, Terminal_Status, Airport_ID)
        sql = 'CALL Add_Terminal(%s, %s, %s, %s)'
        execute(sql, params)
        flash(f'Terminal "{Terminal_Name}" was successfully added.', 'success')
    except Exception as e:
        flash(f'Failed to add terminal: {str(e)}', 'danger')

    return redirect(url_for('Terminals.Display_Terminal'))


@Terminals_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_Terminal(id):
    if request.method == 'POST':
        try:
            sql = 'CALL Delete_Terminal(%s)'
            params = (id,)
            execute(sql, params)
            flash('Terminal deleted successfully.', 'success')
        except Exception as e:
            flash(f'Failed to delete terminal: {str(e)}', 'danger')
        return redirect(url_for('Terminals.Display_Terminal'))


@Terminals_bp.route('/update/<int:id>', methods=['POST', 'GET'])
def Update_Terminal(id):
    if request.method == 'POST':
        try:
            Terminal_Number = request.form.get('Terminal_Number')
            Terminal_Name = request.form['Terminal_Name']
            Terminal_Status = request.form['Terminal_Status']
            Airport_ID = request.form['Airport_ID']

            params = (Terminal_Number, Terminal_Name, Terminal_Status, Airport_ID, id)
            sql = 'update Terminal set Terminal_Number=%s, Terminal_Name=%s, Terminal_Status=%s, Airport_ID=%s where Terminal_ID=%s'
            execute(sql, params)
            flash(f'Terminal "{Terminal_Name}" updated successfully.', 'success')
            return redirect(url_for('Terminals.Display_Terminal'))
        except Exception as e:
            flash(f'Failed to update terminal: {str(e)}', 'danger')
            return redirect(url_for('Terminals.Update_Terminal', id=id))

    else:
        sql = 'CALL Terminal_To_Edit(%s)'
        params = (id,)
        Terminal_To_Edit = fetch_one(sql, params)
        Airport_Data = fetch_all('select Airport_Name, Airport_ID from Airport')
        return render_template('Update/UpdateTerminal.html', Terminal=Terminal_To_Edit, Airport_Data=Airport_Data, Status_Enum=Status_Enum)