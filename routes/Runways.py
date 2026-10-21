from flask import Blueprint, request, render_template, redirect, url_for, flash
from db import fetch_one, fetch_all, execute

Runways_bp = Blueprint(
    'Runways',
    __name__,
    url_prefix='/Runway'
)

Status_Enum = ('Active', 'Inactive', 'Maintenance')


@Runways_bp.route('/')
def Display_Runway():
    sql = 'select * from Runway_Details'
    Runway_Data = fetch_all(sql)
    Airport_Data = fetch_all('select Airport_Name, Airport_ID from Airport')
    return render_template('Runway.html', Runway_Data=Runway_Data, Airport_Data=Airport_Data, Status_Enum=Status_Enum)


@Runways_bp.route('/add', methods=['POST'])
def Add_Runway():
    try:
        Runway_Code = request.form['Runway_Code']
        Runway_Length = request.form['Runway_Length']
        Runway_Status = request.form['Runway_Status']
        Airport_ID = request.form['Airport_ID']

        params = (Runway_Code, Runway_Length, Runway_Status, Airport_ID)
        sql = 'CALL Add_Runway(%s, %s, %s, %s)'
        execute(sql, params)
        flash(f'Runway "{Runway_Code}" was successfully added.', 'success')
    except Exception as e:
        flash(f'Failed to add runway: {str(e)}', 'danger')

    return redirect(url_for('Runways.Display_Runway'))


@Runways_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_Runway(id):
    try:
        sql = 'CALL Delete_Runway(%s)'
        params = (id,)
        execute(sql, params)
        flash('Runway deleted successfully.', 'success')
    except Exception as e:
        flash(f'Failed to delete runway: {str(e)}', 'danger')
    return redirect(url_for('Runways.Display_Runway'))


@Runways_bp.route('/update/<int:id>', methods=['GET', 'POST'])
def Update_Runway(id):
    if request.method == 'POST':
        try:
            Runway_Code = request.form['Runway_Code']
            Runway_Length = request.form['Runway_Length']
            Runway_Status = request.form['Runway_Status']
            Airport_ID = request.form['Airport_ID']

            params = (Runway_Code, Runway_Length, Runway_Status, Airport_ID, id)
            sql = 'update Runway set Runway_Code=%s, Runway_Length=%s, Runway_Status=%s, Airport_ID=%s where Runway_ID=%s'
            execute(sql, params)
            flash(f'Runway "{Runway_Code}" updated successfully.', 'success')
            return redirect(url_for('Runways.Display_Runway'))
        except Exception as e:
            flash(f'Failed to update runway: {str(e)}', 'danger')
            return redirect(url_for('Runways.Update_Runway', id=id))

    else:
        sql = 'CALL Runway_To_Edit(%s)'
        params = (id,)
        Runway_To_Edit = fetch_one(sql, params)
        Airport_Data = fetch_all('select Airport_Name, Airport_ID from Airport')
        return render_template('Update/UpdateRunway.html', Runway=Runway_To_Edit, Airport_Data=Airport_Data, Status_Enum=Status_Enum)