"""CRUD for baggage, separate from passenger check-in."""
from flask import abort, Blueprint, flash, redirect, render_template, request, url_for
from db import fetch_all, fetch_one, execute
from routes.Bookings import amount, choice
from routes.CheckIns import CHECKIN_QUERY, Baggage_Type_Enum, Baggage_Status_Enum

Baggage_bp = Blueprint('Baggage', __name__, url_prefix='/Baggage')


@Baggage_bp.route('/')
def Display_Baggage():
    return render_template('Baggage.html',
        Baggage_Data=fetch_all('SELECT * FROM Baggage_Details ORDER BY Baggage_ID DESC'),
        CheckIn_Data=fetch_all(CHECKIN_QUERY + " WHERE CheckIn_Status='Checked-In' AND Booking_Status='Confirmed' ORDER BY Booking_ID DESC"),
        Baggage_Type_Enum=Baggage_Type_Enum, Baggage_Status_Enum=Baggage_Status_Enum)


def workspace_url():
    return url_for('Baggage.Display_Baggage', _anchor='baggage-workspace')


@Baggage_bp.route('/add/<int:id>', methods=['POST'])
def Add_Baggage(id):
    try:
        weight = amount('Weight_KG')
        bag_type = choice('Baggage_Type', Baggage_Type_Enum)
        execute('CALL Add_Baggage(%s, %s, %s)', (id, weight, bag_type))
        flash('Baggage added.', 'success')
    except Exception as exc:
        flash(f'Failed to add baggage: {exc}', 'danger')
    return redirect(workspace_url())


@Baggage_bp.route('/update/<int:id>/<int:bag_id>', methods=['GET', 'POST'])
def Update_Baggage(id, bag_id):
    if request.method == 'GET':
        bag = fetch_one('CALL Baggage_To_Edit(%s, %s)', (bag_id, id))
        if bag is None:
            abort(404)
        return render_template('Update/UpdateBaggage.html', Bag=bag,
            Baggage_Type_Enum=Baggage_Type_Enum, Baggage_Status_Enum=Baggage_Status_Enum)
    try:
        status = choice('Baggage_Status', Baggage_Status_Enum)
        weight = amount('Weight_KG') if 'Weight_KG' in request.form else None
        bag_type = choice('Baggage_Type', Baggage_Type_Enum) if 'Baggage_Type' in request.form else None
        execute('CALL Update_Baggage(%s, %s, %s, %s, %s)', (id, bag_id, weight, bag_type, status))
        flash('Baggage updated.', 'success')
    except Exception as exc:
        flash(f'Failed to update baggage: {exc}', 'danger')
    return redirect(workspace_url())


@Baggage_bp.route('/delete/<int:id>/<int:bag_id>', methods=['POST'])
def Delete_Baggage(id, bag_id):
    try:
        execute('CALL Delete_Baggage(%s, %s)', (id, bag_id))
        flash('Baggage deleted.', 'success')
    except Exception as exc:
        flash(f'Failed to delete baggage: {exc}', 'danger')
    return redirect(workspace_url())


@Baggage_bp.route('/add', methods=['POST'])
def Create_Baggage():
    booking_id = request.form.get('Booking_ID', type=int)
    if not booking_id or booking_id < 1:
        flash('Select a booking before adding baggage.', 'danger')
        return redirect(url_for('Baggage.Display_Baggage'))
    return Add_Baggage(booking_id)
