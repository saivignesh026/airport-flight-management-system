from flask import Blueprint, render_template, redirect, request, url_for
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
    Terminal_Number = request.form.get('Terminal_Number')
    Terminal_Name = request.form['Terminal_Name']
    Terminal_Status = request.form['Terminal_Status']
    Airport_ID = request.form['Airport_ID']

    params = (Terminal_Number, Terminal_Name, Terminal_Status, Airport_ID)
    sql = 'insert into Terminal (Terminal_Number, Terminal_Name, Terminal_Status, Airport_ID) values (%s, %s, %s, %s)'
    execute(sql, params)

    return redirect(url_for('Terminals.Display_Terminal'))


@Terminals_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_Terminal(id):
    if request.method == 'POST':
        sql = 'delete from Terminal where Terminal_ID = %s'
        params = (id,)
        execute(sql, params)
        return redirect(url_for('Terminals.Display_Terminal'))


@Terminals_bp.route('/update/<int:id>', methods=['POST', 'GET'])
def Update_Terminal(id):
    if request.method == 'POST':
        Terminal_Number = request.form.get('Terminal_Number')
        Terminal_Name = request.form['Terminal_Name']
        Terminal_Status = request.form['Terminal_Status']
        Airport_ID = request.form['Airport_ID']

        params = (Terminal_Number, Terminal_Name, Terminal_Status, Airport_ID, id)
        sql = 'update Terminal set Terminal_Number=%s, Terminal_Name=%s, Terminal_Status=%s, Airport_ID=%s where Terminal_ID=%s'
        execute(sql, params)
        return redirect(url_for('Terminals.Display_Terminal'))

    else:
        sql = 'CALL Terminal_To_Edit(%s)'
        params = (id,)
        Terminal_To_Edit = fetch_one(sql, params)
        Airport_Data = fetch_all('select Airport_Name, Airport_ID from Airport')
        return render_template('UpdateTerminal.html', Terminal=Terminal_To_Edit, Airport_Data=Airport_Data, Status_Enum=Status_Enum)