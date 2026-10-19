from flask import Blueprint,render_template,redirect,request,url_for
from db import get_db_connection,fetch_all,fetch_one,execute

Aircrafts_bp=Blueprint(
    'Aircrafts',
    __name__,
    url_prefix='/Aircraft'
)


@Aircrafts_bp.route('/')
def Display_Aircraft():
    sql='SELECT *from Aircraft_Details;'
    Aircraft_Data=fetch_all(sql)
    Airline_Data=fetch_all('select Name,Airline_ID from Airline')
    return render_template('Aircraft.html',Aircraft_Data=Aircraft_Data,Airline_Data=Airline_Data)


@Aircrafts_bp.route('/add',methods=['POST'])
def Add_Aircraft():
    Tail_Number=request.form['Tail_Number']
    Model=request.form['Model']
    Capacity=request.form['Capacity']
    Airline_ID=request.form['Airline_ID']

    params=(Tail_Number,Model,Capacity,Airline_ID)
    sql='insert into Aircraft (Tail_Number,Model,Capacity,Airline_ID) values (%s,%s,%s,%s)'
    execute(sql,params)

    return redirect(url_for('Aircrafts.Display_Aircraft'))


@Aircrafts_bp.route('/delete/<int:id>',methods=['POST'])
def Delete_Aircraft(id):
    if request.method=='POST':
        sql='Delete from Aircraft where Aircraft_ID=%s'
        params=(id,)
        execute(sql,params)
        return redirect(url_for('Aircrafts.Display_Aircraft'))



@Aircrafts_bp.route('/update/<int:id>',methods=["POST",'GET'])
def Update_Aircraft(id):

    if request.method=='POST':
        Tail_Number=request.form['Tail_Number']
        Model=request.form['Model']
        Capacity=request.form['Capacity']
        Airline_ID=request.form['Airline_ID']
        params=(Tail_Number,Model,Capacity,Airline_ID,id)
        sql='update Aircraft set Tail_Number=%s,Model=%s,Capacity=%s,Airline_ID=%s where Aircraft_ID=%s'
        execute(sql,params)
        return redirect(url_for('Aircrafts.Display_Aircraft'))
        
    else:

        sql='CALL Aircraft_To_Edit(%s)'
        params=(id,)
        Aircraft_To_Edit=fetch_one(sql,params)    
        Airline_Data=fetch_all('select Name,Airline_ID from Airline')
        return render_template('Update/UpdateAircraft.html',Airline_Data=Airline_Data,Aircraft=Aircraft_To_Edit)
            

