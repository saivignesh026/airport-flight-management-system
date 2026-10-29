"""Airport check-in, boarding, and individual baggage records."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from db import fetch_all, fetch_one, execute
from routes.Bookings import choice

CheckIns_bp = Blueprint('CheckIns', __name__, url_prefix='/CheckIn')
CheckIn_Status_Enum = ('Pending', 'Checked-In', 'No Show')
Boarding_Status_Enum = ('Not Boarded', 'Boarding', 'Boarded')
Baggage_Type_Enum = ('Checked', 'Cabin')
Baggage_Status_Enum = ('Checked-In', 'Screened', 'Sorted', 'Loaded', 'In-Transit', 'Unloaded', 'Claimed', 'Lost')
CHECKIN_QUERY = 'SELECT * FROM Booking_Check_In_Details'


@CheckIns_bp.route('/')
def Display_CheckIn():
    return render_template('CheckIn.html',
        CheckIn_Data=fetch_all('SELECT * FROM Check_In_Details ORDER BY CheckIn_ID DESC'),
        Booking_Data=fetch_all(CHECKIN_QUERY + " WHERE CheckIn_ID IS NULL AND Booking_Status='Confirmed' ORDER BY Booking_ID DESC"),
        CheckIn_Status_Enum=CheckIn_Status_Enum, Boarding_Status_Enum=Boarding_Status_Enum)


def workspace_url():
    return url_for('CheckIns.Display_CheckIn', _anchor='checkin-workspace')


@CheckIns_bp.route('/update/<int:id>', methods=['GET', 'POST'])
def Update_CheckIn(id):
    booking = fetch_one('CALL Check_In_To_Edit(%s)', (id,))
    if booking is None:
        abort(404)
    if request.method == 'POST':
        try:
            status = choice('CheckIn_Status', CheckIn_Status_Enum)
            boarding = choice('Boarding_Status', Boarding_Status_Enum)
            if status != 'Checked-In' and boarding != 'Not Boarded':
                raise ValueError('Complete check-in before boarding.')
            procedure = 'Add_Check_In' if request.endpoint == 'CheckIns.Create_CheckIn' else 'Update_Check_In'
            execute(f'CALL {procedure}(%s, %s, %s)', (id, status, boarding))
            flash('Check-in and boarding updated.', 'success')
        except Exception as exc:
            flash(f'Failed to update check-in: {exc}', 'danger')
        return redirect(workspace_url())
    return render_template('Update/UpdateCheckIn.html', Booking=booking,
        CheckIn_Status_Enum=CheckIn_Status_Enum, Boarding_Status_Enum=Boarding_Status_Enum)


@CheckIns_bp.route('/delete/<int:id>', methods=['POST'])
def Delete_CheckIn(id):
    try:
        execute('CALL Delete_Check_In(%s)', (id,))
        flash('Check-in deleted. The booking is still available for a new check-in.', 'success')
    except Exception as exc:
        flash(f'Failed to delete check-in: {exc}', 'danger')
    return redirect(workspace_url())


@CheckIns_bp.route('/add', methods=['POST'])
def Create_CheckIn():
    booking_id = request.form.get('Booking_ID', type=int)
    if not booking_id or booking_id < 1:
        flash('Select a booking before creating check-in.', 'danger')
        return redirect(url_for('CheckIns.Display_CheckIn'))
    return Update_CheckIn(booking_id)
