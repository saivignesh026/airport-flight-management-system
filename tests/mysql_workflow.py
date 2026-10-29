"""Integration check against an isolated dump; never uses .env credentials.

Usage: python tests/mysql_workflow.py /path/to/AFMS.sql /tmp/initialized-mysql-datadir /path/to/external-update.sql
Initialize the temporary datadir with mysqld --initialize-insecure first.
"""
import pathlib
import subprocess
import sys
import time
import uuid
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import mysql.connector
import db
from app import app


def main():
    dump, datadir, migration = map(pathlib.Path, sys.argv[1:])
    if not datadir.is_relative_to('/tmp'):
        raise ValueError('Integration testing requires an isolated datadir under /tmp.')
    socket = str(datadir / 'workflow.sock')
    server = subprocess.Popen(['mysqld', '--no-defaults', f'--datadir={datadir}',
        '--tmpdir=/tmp', f'--socket={socket}', f'--pid-file={datadir}/workflow.pid',
        f'--log-error={datadir}/workflow.log', '--skip-networking', '--mysqlx=OFF'])
    try:
        for _ in range(100):
            try:
                conn = mysql.connector.connect(user='root', unix_socket=socket)
                conn.close()
                break
            except mysql.connector.Error:
                if server.poll() is not None:
                    raise RuntimeError((datadir / 'workflow.log').read_text())
                time.sleep(.1)
        else:
            raise RuntimeError('Temporary MySQL did not start.')
        command = ['mysql', '--no-defaults', f'--socket={socket}', '-u', 'root']
        with dump.open('rb') as source:
            subprocess.run(command, stdin=source, check=True)
        with migration.open('rb') as source:
            subprocess.run(command + ['AF_DB2'], stdin=source, check=True)
        def connect():
            return mysql.connector.connect(user='root', unix_socket=socket,
                database='AF_DB2', time_zone='+05:30')
        with patch('db.get_db_connection', side_effect=connect):
            verify_workflow()
    finally:
        if server.poll() is None:
            subprocess.run(['mysqladmin', '--no-defaults', f'--socket={socket}', '-u', 'root', 'shutdown'], check=False)
        server.wait(timeout=20)


def verify_workflow():
    app.config.update(TESTING=True)
    client = app.test_client()
    def request_ok(url, data=None):
        response = client.get(url, follow_redirects=True) if data is None else client.post(url, data=data, follow_redirects=True)
        assert response.status_code == 200, (url, response.status_code)
        assert b'Failed to ' not in response.data, (url, response.data.decode()[:1000])
        return response
    for rule in app.url_map.iter_rules():
        if 'GET' in rule.methods and not rule.arguments:
            request_ok(rule.rule)
    instance = db.fetch_one("SELECT Instance_ID FROM Flight_Instance WHERE Flight_Instance_Status='Scheduled' LIMIT 1")['Instance_ID']
    suffix = uuid.uuid4().hex[:12]
    email = f'workflow-{suffix}@example.com'
    data = dict(First_Name='Workflow', Last_Name='Test', Nationality='India',
        Contact_Number='1234567890', Email=email, Instance_ID=str(instance),
        Seat_Number='Z9X', Class='Economy', Booking_Price='100.00',
        Booking_Status='Confirmed', Payment_Method='UPI', Payment_Status='Payment Received',
        Transaction_Reference=f'workflow-{suffix}')
    request_ok('/Booking/add', data)
    passenger = db.fetch_one('SELECT * FROM Passenger WHERE Email=%s', (email,))
    assert passenger, 'New passenger was not saved'
    booking = db.fetch_one('SELECT * FROM Booking WHERE Passenger_ID=%s', (passenger['Passenger_ID'],))
    bid = booking['Booking_ID']
    try:
        assert db.fetch_one('SELECT * FROM Check_In WHERE Booking_ID=%s', (bid,)) is None
        assert db.fetch_one('SELECT * FROM Baggage WHERE Booking_ID=%s', (bid,)) is None
        assert db.fetch_one('SELECT * FROM Booking_Status_Details WHERE Booking_ID=%s', (bid,))
        assert db.fetch_one('SELECT * FROM Passenger_Manifest WHERE Booking_ID=%s', (bid,))
        request_ok(f'/Booking/update/{bid}')
        request_ok(f'/Booking/update/{bid}', data)
        request_ok(f'/CheckIn/update/{bid}')
        # Duplicate seats must roll back the passenger created in the same transaction.
        duplicate = dict(data, Email=f'duplicate-{suffix}@example.com', Transaction_Reference='')
        response = client.post('/Booking/add', data=duplicate, follow_redirects=True)
        assert b'Failed to add booking' in response.data
        assert db.fetch_one('SELECT * FROM Passenger WHERE Email=%s', (duplicate['Email'],)) is None
        # Reject check-in until payment is received.
        db.execute("UPDATE Payment SET Payment_Status='Pending' WHERE Booking_ID=%s", (bid,))
        response = client.post(f'/CheckIn/update/{bid}', data={'CheckIn_Status': 'Checked-In', 'Boarding_Status': 'Not Boarded'}, follow_redirects=True)
        assert b'Payment must be received' in response.data
        db.execute("UPDATE Payment SET Payment_Status='Payment Received' WHERE Booking_ID=%s", (bid,))
        request_ok('/CheckIn/add', {'Booking_ID': str(bid), 'CheckIn_Status': 'Checked-In', 'Boarding_Status': 'Not Boarded'})
        checked_in = db.fetch_one('SELECT * FROM Check_In WHERE Booking_ID=%s', (bid,))
        assert checked_in['CheckIn_Time'] is not None
        request_ok(f'/CheckIn/update/{bid}', {'CheckIn_Status': 'Checked-In', 'Boarding_Status': 'Boarded'})
        assert db.fetch_one('SELECT * FROM Check_In WHERE Booking_ID=%s', (bid,))['CheckIn_Time'] == checked_in['CheckIn_Time']
        request_ok(f'/Baggage/add/{bid}', {'Weight_KG': '15.5', 'Baggage_Type': 'Checked'})
        request_ok(f'/Baggage/add/{bid}', {'Weight_KG': '7', 'Baggage_Type': 'Cabin'})
        bags = db.fetch_all('SELECT * FROM Baggage WHERE Booking_ID=%s ORDER BY Baggage_ID', (bid,))
        assert len(bags) == 2
        request_ok(f'/Baggage/update/{bid}/{bags[0]["Baggage_ID"]}')
        request_ok(f'/Baggage/update/{bid}/{bags[0]["Baggage_ID"]}', {'Baggage_Status': 'Loaded'})
        bags = db.fetch_all('SELECT * FROM Baggage WHERE Booking_ID=%s ORDER BY Baggage_ID', (bid,))
        assert [bag['Baggage_Status'] for bag in bags] == ['Loaded', 'Checked-In']
        summary = db.fetch_all('SELECT * FROM Booking_Status_Details WHERE Booking_ID=%s', (bid,))
        assert len(summary) == 1 and float(summary[0]['Weight_KG']) == 22.5
        response = client.post(f'/Booking/update/{bid}', data=data, follow_redirects=True)
        assert b'A checked-in booking cannot be edited' in response.data
        # All CRUD operations stay in the selected booking's single-page workspace.
        request_ok(f'/CheckIn/?booking_id={bid}')
        request_ok(f'/Baggage/update/{bid}/{bags[0]["Baggage_ID"]}',
                   {'Weight_KG': '12.25', 'Baggage_Type': 'Cabin', 'Baggage_Status': 'Screened'})
        edited = db.fetch_one('SELECT * FROM Baggage WHERE Baggage_ID=%s', (bags[0]['Baggage_ID'],))
        assert float(edited['Weight_KG']) == 12.25 and edited['Baggage_Type'] == 'Cabin'
        response = client.post(f'/CheckIn/delete/{bid}', follow_redirects=True)
        assert b'Delete the baggage records on the baggage page' in response.data
        assert db.fetch_one('SELECT * FROM Check_In WHERE Booking_ID=%s', (bid,))
        for bag in bags:
            request_ok(f'/Baggage/delete/{bid}/{bag["Baggage_ID"]}', {})
        assert not db.fetch_all('SELECT * FROM Baggage WHERE Booking_ID=%s', (bid,))
        request_ok(f'/CheckIn/delete/{bid}', {})
        assert db.fetch_one('SELECT * FROM Check_In WHERE Booking_ID=%s', (bid,)) is None
        assert db.fetch_one('SELECT * FROM Booking WHERE Booking_ID=%s', (bid,))
        assert db.fetch_one('SELECT * FROM Payment WHERE Booking_ID=%s', (bid,))
        request_ok('/CheckIn/add', {'Booking_ID': str(bid), 'CheckIn_Status': 'Checked-In', 'Boarding_Status': 'Not Boarded'})
        request_ok('/Passenger/manifest')
        request_ok('/')
        # Check every existing edit template against actual stored-procedure results.
        entities = [('Aircraft', 'Aircraft', 'Aircraft_ID'), ('Airline', 'Airline', 'Airline_ID'),
            ('Airport', 'Airport', 'Airport_ID'), ('Runway', 'Runway', 'Runway_ID'),
            ('Terminal', 'Terminal', 'Terminal_ID'), ('Gate', 'Gate', 'Gate_ID'),
            ('Department', 'Department', 'Department_ID'), ('Role', 'Role', 'Role_ID'),
            ('Employee', 'Employee', 'Employee_ID'), ('Flight', 'Flight', 'Flight_ID'),
            ('FlightInstance', 'Flight_Instance', 'Instance_ID'), ('Passenger', 'Passenger', 'Passenger_ID')]
        for prefix, table, key in entities:
            row = db.fetch_one(f'SELECT {key} FROM {table} LIMIT 1')
            upper = prefix in ('Airline', 'Airport')
            if row:
                request_ok(f'/{prefix}/{"Update" if upper else "update"}/{row[key]}')
        print('PASS: dump import, SQL migration, populated pages, booking, payment, rollback, check-in, boarding, separate check-in and baggage CRUD pages, multiple bags, manifest, dashboard, and edit pages')
    finally:
        db.execute('CALL Delete_Booking(%s)', (bid,))
        db.execute('DELETE FROM Passenger WHERE Passenger_ID=%s', (passenger['Passenger_ID'],))


if __name__ == '__main__':
    main()
