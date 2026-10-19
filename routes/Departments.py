from flask import Blueprint, render_template, redirect, request, url_for
from db import fetch_all, fetch_one, execute

Departments_bp = Blueprint(
    'Departments',
    __name__,
    url_prefix='/Department'
)

@Departments_bp.route('/')
def Display_Department():
    sql = 'SELECT Department_ID, Department_Name, Description FROM Department ORDER BY Department_ID'
    Department_Data = fetch_all(sql)
    return render_template('Department.html', Department_Data=Department_Data)

@Departments_bp.route('/add', methods=['POST'])
def Add_Department():
    Department_Name = request.form['Department_Name']
    Description = request.form['Description']

    params = (Department_Name, Description)
    sql = 'INSERT INTO Department (Department_Name, Description) VALUES (%s, %s)'
    execute(sql, params)

    return redirect(url_for('Departments.Display_Department'))

@Departments_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_Department(id):
    if request.method == 'POST':
        sql = 'DELETE FROM Department WHERE Department_ID=%s'
        params = (id,)
        execute(sql, params)
        return redirect(url_for('Departments.Display_Department'))

@Departments_bp.route('/update/<int:id>', methods=["POST", 'GET'])
def Update_Department(id):
    if request.method == 'POST':
        Department_Name = request.form['Department_Name']
        Description = request.form['Description']
        
        params = (Department_Name, Description, id)
        sql = 'UPDATE Department SET Department_Name=%s, Description=%s WHERE Department_ID=%s'
        execute(sql, params)
        return redirect(url_for('Departments.Display_Department'))
    else:
        sql = 'SELECT Department_ID, Department_Name, Description FROM Department WHERE Department_ID=%s'
        params = (id,)
        Department_To_Edit = fetch_one(sql, params)    
        return render_template('Update/UpdateDepartment.html', Department=Department_To_Edit)