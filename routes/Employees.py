from flask import abort, Blueprint, render_template, redirect, request, url_for, flash
from db import fetch_all, fetch_one, execute, is_restricted_delete_error

Employees_bp = Blueprint(
    'Employees',
    __name__,
    url_prefix='/Employee'
)

@Employees_bp.route('/')
def Display_Employee():
    sql = 'SELECT * FROM Employee_Details'
    Employee_Data = fetch_all(sql)
    Department_Data = fetch_all('SELECT Department_ID, Department_Name FROM Department')
    Role_Data = fetch_all('SELECT Role_ID, Role_Name FROM Role')
    return render_template('Employee.html', Employee_Data=Employee_Data, Department_Data=Department_Data, Role_Data=Role_Data)

@Employees_bp.route('/add', methods=['POST'])
def Add_Employee():
    try:
        Employee_Name = request.form['Employee_Name']
        Employee_Email = request.form['Employee_Email']
        Contact_Number = request.form['Contact_Number']
        Department_ID = request.form['Department_ID'] or None
        Role_ID = request.form['Role_ID'] or None
        Hire_Date = request.form['Hire_Date'] or None
        Employee_Status = request.form['Employee_Status']

        params = (Employee_Name, Employee_Email, Contact_Number, Department_ID, Role_ID, Hire_Date, Employee_Status)
        sql = 'CALL Add_Employee(%s, %s, %s, %s, %s, %s, %s)'
        execute(sql, params)
        flash(f'Employee "{Employee_Name}" was successfully added.', 'success')
    except Exception as e:
        flash(f'Failed to add employee: {str(e)}', 'danger')
    return redirect(url_for('Employees.Display_Employee'))

@Employees_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_Employee(id):
    if request.method == 'POST':
        try:
            sql = 'CALL Delete_Employee(%s)'
            execute(sql, (id,))
            flash('Employee deleted successfully.', 'success')
        except Exception as e:
            if is_restricted_delete_error(e):
                flash('Cannot delete this employee because related records exist. Delete or reassign them first.', 'danger')
            else:
                flash(f'Failed to delete employee: {str(e)}', 'danger')
        return redirect(url_for('Employees.Display_Employee'))

@Employees_bp.route('/update/<int:id>', methods=['POST', 'GET'])
def Update_Employee(id):
    if request.method == 'POST':
        try:
            Employee_Name = request.form['Employee_Name']
            Employee_Email = request.form['Employee_Email']
            Contact_Number = request.form['Contact_Number']
            Department_ID = request.form['Department_ID'] or None
            Role_ID = request.form['Role_ID'] or None
            Hire_Date = request.form['Hire_Date'] or None
            Employee_Status = request.form['Employee_Status']

            params = (Employee_Name, Employee_Email, Contact_Number, Department_ID, Role_ID, Hire_Date, Employee_Status, id)
            sql = 'CALL Update_Employee(%s, %s, %s, %s, %s, %s, %s, %s)'
            execute(sql, params)
            flash(f'Employee "{Employee_Name}" updated successfully.', 'success')
            return redirect(url_for('Employees.Display_Employee'))
        except Exception as e:
            flash(f'Failed to update employee: {str(e)}', 'danger')
            return redirect(url_for('Employees.Update_Employee', id=id))
    else:
        Employee_To_Edit = fetch_one('CALL Employee_To_Edit(%s)', (id,))
        if Employee_To_Edit is None:
            abort(404)
        Department_Data = fetch_all('SELECT Department_ID, Department_Name FROM Department')
        Role_Data = fetch_all('SELECT Role_ID, Role_Name FROM Role')
        return render_template('Update/UpdateEmployee.html', Department_Data=Department_Data, Role_Data=Role_Data, Employee=Employee_To_Edit)
