from flask import Flask,render_template,redirect,url_for,request,Blueprint,flash
from db import get_db_connection,fetch_all,fetch_one,execute,is_restricted_delete_error

Airlines_bp=Blueprint(

    'Airlines',
    __name__,
    url_prefix='/Airline'

)


@Airlines_bp.route('/')
def Display_Airline():
    Airline_Data=fetch_all('select * from Airline')
    return render_template('Airline.html',Airline_Data=Airline_Data)


@Airlines_bp.route('/Add',methods=['POST'])
def Add_Airline():
    try:
        Airline_Name=request.form['Airline_Name']
        IATA_Code=request.form['IATA_Code']
        ICAO_Code=request.form['ICAO_Code']
        Airline_Country=request.form['Airline_Country']

        params=(Airline_Name,IATA_Code,ICAO_Code,Airline_Country)
        sql='CALL Add_Airline(%s, %s, %s, %s)'
        execute(sql,params)
        flash(f'Airline "{Airline_Name}" was successfully added.', 'success')
    except Exception as e:
        flash(f'Failed to add airline: {str(e)}', 'danger')

    return redirect(url_for('Airlines.Display_Airline'))


@Airlines_bp.route('/Delete/<int:id>',methods=['POST'])
def Delete_Airline(id):
    try:
        params=(id,)
        sql='CALL Delete_Airline(%s)'
        execute(sql,params)
        flash('Airline deleted successfully.', 'success')
    except Exception as e:
        if is_restricted_delete_error(e):
            flash('Cannot delete this airline because related records exist. Delete or reassign them first.', 'danger')
        else:
            flash(f'Failed to delete airline: {str(e)}', 'danger')
    return redirect(url_for('Airlines.Display_Airline'))

@Airlines_bp.route('/Update/<int:id>',methods=['GET','POST'])
def Update_Airline(id):
    if request.method == 'POST':
        try:
            Airline_Name = request.form['Airline_Name']
            IATA_Code = request.form['IATA_Code']
            ICAO_Code = request.form['ICAO_Code']
            Airline_Country = request.form['Airline_Country']

            sql = 'CALL Update_Airline(%s, %s, %s, %s, %s)'
            params = (Airline_Name, IATA_Code, ICAO_Code, Airline_Country, id)
            execute(sql, params)
            flash(f'Airline "{Airline_Name}" updated successfully.', 'success')
            return redirect(url_for('Airlines.Display_Airline'))
        except Exception as e:
            flash(f'Failed to update airline: {str(e)}', 'danger')
            return redirect(url_for('Airlines.Update_Airline', id=id))
    else:
        sql = 'CALL Airline_To_Edit(%s)'
        params = (id,)
        airline_to_edit = fetch_one(sql, params)
        return render_template('Update/UpdateAirline.html', airline=airline_to_edit)
    
