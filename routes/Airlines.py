from flask import Flask,render_template,redirect,url_for,request,Blueprint
from db import get_db_connection,fetch_all,fetch_one,execute

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
    Airline_Name=request.form['Airline_Name']
    IATA_Code=request.form['IATA_Code']
    ICAO_Code=request.form['ICAO_Code']
    Airline_Country=request.form['Airline_Country']

    params=(Airline_Name,IATA_Code,ICAO_Code,Airline_Country)
    sql='insert into Airline (Name,IATA_Code,ICAO_Code,Country) values (%s,%s,%s,%s)'
    execute(sql,params)

    return redirect(url_for('Airlines.Display_Airline'))


@Airlines_bp.route('/Delete/<int:id>',methods=['POST'])
def Delete_Airline(id):
    params=(id,)
    sql='Delete from Airline Where Airline_ID=%s'
    execute(sql,params)
    return redirect(url_for('Airlines.Display_Airline'))

@Airlines_bp.route('/Update/<int:id>',methods=['GET','POST'])
def Update_Airline(id):
    if request.method == 'POST':
        Airline_Name = request.form['Airline_Name']
        IATA_Code = request.form['IATA_Code']
        ICAO_Code = request.form['ICAO_Code']
        Airline_Country = request.form['Airline_Country']

        # The SQL UPDATE command
        sql = 'UPDATE Airline SET Name=%s, IATA_Code=%s, ICAO_Code=%s, Country=%s WHERE Airline_ID=%s'
        params = (Airline_Name, IATA_Code, ICAO_Code, Airline_Country, id)
        execute(sql, params)

        return redirect(url_for('Airlines.Display_Airline'))
    else:
        sql = 'SELECT * FROM Airline WHERE Airline_ID=%s'
        params = (id,)
        airline_to_edit = fetch_one(sql, params)
        return render_template('Update/UpdateAirline.html', airline=airline_to_edit)
    
