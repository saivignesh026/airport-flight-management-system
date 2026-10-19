from flask import Blueprint, render_template, redirect, request, url_for
from db import fetch_all, fetch_one, execute

Employees_bp = Blueprint(
    'Employees',
    __name__,
    url_prefix='/Employee'
)

@Employees_bp.route('/')
def Display_Employee():
    sql = 'select * from Employee_Details'
    Employee_Data = fetch_all(sql)
    Department_Data = fetch_all('SELECT Department_ID, Department_Name FROM Department')
    Role_Data = fetch_all('SELECT Role_ID, Role_Name FROM Role')
    
    return render_template('Employee.html', Employee_Data=Employee_Data, Department_Data=Department_Data, Role_Data=Role_Data)

@Employees_bp.route('/add', methods=['POST'])
def Add_Employee():
    Employee_Name = request.form['Employee_Name']
    Department_ID = request.form['Department_ID'] or None
    Role_ID = request.form['Role_ID'] or None
    Hire_Date = request.form['Hire_Date'] or None
    Employee_Status = request.form['Employee_Status']

    params = (Employee_Name, Department_ID, Role_ID, Hire_Date, Employee_Status)
    sql = 'INSERT INTO Employee (Employee_Name, Department_ID, Role_ID, Hire_Date, Employee_Status) \
           VALUES (%s, %s, %s, %s, %s)'
    execute(sql, params)

    return redirect(url_for('Employees.Display_Employee'))

@Employees_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_Employee(id):
    if request.method == 'POST':
        sql = 'DELETE FROM Employee WHERE Employee_ID=%s'
        params = (id,)
        execute(sql, params)
        return redirect(url_for('Employees.Display_Employee'))

@Employees_bp.route('/update/<int:id>', methods=["POST", 'GET'])
def Update_Employee(id):
    if request.method == 'POST':
        Employee_Name = request.form['Employee_Name']
        Department_ID = request.form['Department_ID'] or None
        Role_ID = request.form['Role_ID'] or None
        Hire_Date = request.form['Hire_Date'] or None
        Employee_Status = request.form['Employee_Status']
        
        params = (Employee_Name, Department_ID, Role_ID, Hire_Date, Employee_Status, id)
        sql = 'UPDATE Employee SET Employee_Name=%s, Department_ID=%s, Role_ID=%s, Hire_Date=%s, Employee_Status=%s \
               WHERE Employee_ID=%s'
        execute(sql, params)
        return redirect(url_for('Employees.Display_Employee'))
    else:
        sql = 'call Employee_To_Edit(%s)'
        params = (id,)
        Employee_To_Edit = fetch_one(sql, params)    
        Department_Data = fetch_all('SELECT Department_ID, Department_Name FROM Department')
        Role_Data = fetch_all('SELECT Role_ID, Role_Name FROM Role')
        
        return render_template('Update/UpdateEmployee.html', Department_Data=Department_Data, Role_Data=Role_Data, Employee=Employee_To_Edit)