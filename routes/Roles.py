from flask import Blueprint, render_template, redirect, request, url_for
from db import fetch_all, fetch_one, execute

Roles_bp = Blueprint(
    'Roles',
    __name__,
    url_prefix='/Role'
)

@Roles_bp.route('/')
def Display_Role():
    sql = 'SELECT r.Role_ID, r.Role_Name, r.Department_ID, d.Department_Name \
           FROM Role r \
           JOIN Department d ON r.Department_ID = d.Department_ID \
           ORDER BY r.Role_ID'
    Role_Data = fetch_all(sql)
    Department_Data = fetch_all('SELECT Department_ID, Department_Name FROM Department')
    return render_template('Role.html', Role_Data=Role_Data, Department_Data=Department_Data)

@Roles_bp.route('/add', methods=['POST'])
def Add_Role():
    Role_Name = request.form['Role_Name']
    Department_ID = request.form['Department_ID']

    params = (Role_Name, Department_ID)
    sql = 'INSERT INTO Role (Role_Name, Department_ID) VALUES (%s, %s)'
    execute(sql, params)

    return redirect(url_for('Roles.Display_Role'))

@Roles_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_Role(id):
    if request.method == 'POST':
        sql = 'DELETE FROM Role WHERE Role_ID=%s'
        params = (id,)
        execute(sql, params)
        return redirect(url_for('Roles.Display_Role'))

@Roles_bp.route('/update/<int:id>', methods=["POST", 'GET'])
def Update_Role(id):
    if request.method == 'POST':
        Role_Name = request.form['Role_Name']
        Department_ID = request.form['Department_ID']
        
        params = (Role_Name, Department_ID, id)
        sql = 'UPDATE Role SET Role_Name=%s, Department_ID=%s WHERE Role_ID=%s'
        execute(sql, params)
        return redirect(url_for('Roles.Display_Role'))
    else:
        sql = 'SELECT r.Role_ID, r.Role_Name, r.Department_ID, d.Department_Name \
               FROM Role r \
               JOIN Department d ON r.Department_ID = d.Department_ID \
               WHERE r.Role_ID=%s'
        params = (id,)
        Role_To_Edit = fetch_one(sql, params)    
        Department_Data = fetch_all('SELECT Department_ID, Department_Name FROM Department')
        return render_template('UpdateRole.html', Department_Data=Department_Data, Role=Role_To_Edit)