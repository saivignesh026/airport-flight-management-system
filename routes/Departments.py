from flask import Blueprint, render_template, redirect, request, url_for, flash
from db import fetch_all, fetch_one, execute, is_restricted_delete_error

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
    try:
        Department_Name = request.form['Department_Name']
        Description = request.form['Description']

        params = (Department_Name, Description)
        sql = 'INSERT INTO Department (Department_Name, Description) VALUES (%s, %s)'
        execute(sql, params)
        flash(f'Department "{Department_Name}" was successfully added.', 'success')
    except Exception as e:
        flash(f'Failed to add department: {str(e)}', 'danger')

    return redirect(url_for('Departments.Display_Department'))

@Departments_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_Department(id):
    if request.method == 'POST':
        try:
            sql = 'DELETE FROM Department WHERE Department_ID=%s'
            params = (id,)
            execute(sql, params)
            flash('Department deleted successfully.', 'success')
        except Exception as e:
            if is_restricted_delete_error(e):
                flash('Cannot delete this department because related roles or employees exist. Delete or reassign them first.', 'danger')
            else:
                flash(f'Failed to delete department: {str(e)}', 'danger')
        return redirect(url_for('Departments.Display_Department'))

@Departments_bp.route('/update/<int:id>', methods=["POST", 'GET'])
def Update_Department(id):
    if request.method == 'POST':
        try:
            Department_Name = request.form['Department_Name']
            Description = request.form['Description']

            params = (Department_Name, Description, id)
            sql = 'CALL Update_Department(%s, %s, %s)'
            execute(sql, params)
            flash(f'Department "{Department_Name}" updated successfully.', 'success')
            return redirect(url_for('Departments.Display_Department'))
        except Exception as e:
            flash(f'Failed to update department: {str(e)}', 'danger')
            return redirect(url_for('Departments.Update_Department', id=id))
    else:
        sql = 'CALL Department_To_Edit(%s)'
        params = (id,)
        Department_To_Edit = fetch_one(sql, params)    
        return render_template('Update/UpdateDepartment.html', Department=Department_To_Edit)
