from flask import abort, Blueprint, render_template, redirect, request, url_for, flash
from db import fetch_all, fetch_one, execute, is_restricted_delete_error

Roles_bp = Blueprint(
    'Roles',
    __name__,
    url_prefix='/Role'
)

@Roles_bp.route('/')
def Display_Role():
    sql = 'select * from Role_Details'
    Role_Data = fetch_all(sql)
    Department_Data = fetch_all('SELECT Department_ID, Department_Name FROM Department')
    return render_template('Role.html', Role_Data=Role_Data, Department_Data=Department_Data)

@Roles_bp.route('/add', methods=['POST'])
def Add_Role():
    try:
        Role_Name = request.form['Role_Name']
        Department_ID = request.form['Department_ID']

        params = (Role_Name, Department_ID)
        sql = 'CALL Add_Role(%s, %s)'
        execute(sql, params)
        flash(f'Role "{Role_Name}" was successfully added.', 'success')
    except Exception as e:
        flash(f'Failed to add role: {str(e)}', 'danger')

    return redirect(url_for('Roles.Display_Role'))

@Roles_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_Role(id):
    if request.method == 'POST':
        try:
            sql = 'CALL Delete_Role(%s)'
            params = (id,)
            execute(sql, params)
            flash('Role deleted successfully.', 'success')
        except Exception as e:
            if is_restricted_delete_error(e):
                flash('Cannot delete this role because related employees exist. Delete or reassign them first.', 'danger')
            else:
                flash(f'Failed to delete role: {str(e)}', 'danger')
        return redirect(url_for('Roles.Display_Role'))

@Roles_bp.route('/update/<int:id>', methods=["POST", 'GET'])
def Update_Role(id):
    if request.method == 'POST':
        try:
            Role_Name = request.form['Role_Name']
            Department_ID = request.form['Department_ID']

            params = (Role_Name, Department_ID, id)
            sql = 'CALL Update_Role(%s, %s, %s)'
            execute(sql, params)
            flash(f'Role "{Role_Name}" updated successfully.', 'success')
            return redirect(url_for('Roles.Display_Role'))
        except Exception as e:
            flash(f'Failed to update role: {str(e)}', 'danger')
            return redirect(url_for('Roles.Update_Role', id=id))
    else:
        sql = 'call Role_To_Edit(%s)'
        params = (id,)
        Role_To_Edit = fetch_one(sql, params)
        if Role_To_Edit is None:
            abort(404)
        Department_Data = fetch_all('SELECT Department_ID, Department_Name FROM Department')
        return render_template('Update/UpdateRole.html', Department_Data=Department_Data, Role=Role_To_Edit)
