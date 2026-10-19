from flask import Flask,render_template,redirect,url_for,request,Blueprint
from db import get_db_connection,fetch_all,fetch_one,execute


Airports_bp=Blueprint(

    'Airports',
    __name__,
    url_prefix='/Airport'
)

@Airports_bp.route('/')
def Display_Airport():
    sql='Select *from Airport'
    Airport_Data=fetch_all(sql)
    return render_template('Airport.html',Airport_Data=Airport_Data)




@Airports_bp.route('/Add',methods=['POST'])
def Add_Airport():
    Airport_IATA_Code=request.form['Airport_IATA_Code']
    Airport_Name=request.form['Airport_Name']
    Airport_City=request.form['Airport_City']
    Airport_Country=request.form['Airport_Country']
    sql='insert into Airport (IATA_Code, Airport_Name, Airport_City, Airport_Country)  values (%s,%s,%s,%s)'
    params=(Airport_IATA_Code,Airport_Name,Airport_City,Airport_Country)
    execute(sql,params)
    return redirect(url_for('Airports.Display_Airport'))

@Airports_bp.route('/Delete/<int:id>',methods=['POST'])
def Delete_Airport(id):
    if request.method=='POST':
        sql='delete from Airport where Airport_ID=%s'
        params=(id,)
        execute(sql,params)
        return redirect(url_for('Airports.Display_Airport'))

@Airports_bp.route('/Update/<int:id>',methods=['POST','GET'])
def Update_Airport(id):
    if request.method == 'POST':
            Airport_IATA_Code=request.form['Airport_IATA_Code']
            Airport_Name=request.form['Airport_Name']
            Airport_City=request.form['Airport_City']
            Airport_Country=request.form['Airport_Country']

            sql='update Airport set IATA_Code=%s,Airport_Name=%s,Airport_City=%s,Airport_Country=%s where Airport_ID=%s'
            params=(Airport_IATA_Code,Airport_Name,Airport_City,Airport_Country,id)

            execute(sql,params)

            return redirect(url_for('Airports.Display_Airport'))
    else:
        sql='select *from Airport where Airport_ID=%s'
        params=(id,)
        Airport_To_Edit=fetch_one(sql,params)
        return render_template('Update/UpdateAirport.html',Airport=Airport_To_Edit)
        
