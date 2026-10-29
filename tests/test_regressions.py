import importlib
import unittest
from contextlib import ExitStack
from datetime import timedelta
from unittest.mock import MagicMock, patch

import db
from app import app, html_time


class RoutesTest(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch('app.fetch_all', return_value=[]))
        self.stack.enter_context(patch('app.fetch_one', return_value={'count': 0}))
        for name in app.blueprints:
            module = importlib.import_module('routes.' + name)
            self.stack.enter_context(patch.object(module, 'fetch_all', return_value=[]))
            self.stack.enter_context(patch.object(module, 'fetch_one', return_value=None))

    def test_every_listing_renders_with_empty_database(self):
        for rule in app.url_map.iter_rules():
            if 'GET' in rule.methods and not rule.arguments:
                with self.subTest(url=rule.rule):
                    self.assertEqual(self.client.get(rule.rule).status_code, 200)

    def test_every_edit_returns_404_for_missing_record(self):
        for rule in app.url_map.iter_rules():
            if 'GET' in rule.methods and rule.arguments == {'id'}:
                with self.subTest(url=rule.rule):
                    self.assertEqual(self.client.get(rule.rule.replace('<int:id>', '999')).status_code, 404)

    def test_manifest_uses_view_columns_and_bound_filters(self):
        with patch('routes.Passengers.fetch_all', return_value=[]) as fetch:
            self.assertEqual(self.client.get('/Passenger/manifest?flight_id=7&from_airport_id=2').status_code, 200)
            sql, params = fetch.call_args_list[0].args
            self.assertIn('ORDER BY Scheduled_Departure DESC, Flight_Number, Seat_Number', sql)
            self.assertEqual(params, ('7', '2'))

    def test_booking_update_does_not_touch_checkin_or_baggage(self):
        booking = {'Booking_ID': 1, 'Passenger_ID': 2, 'Instance_ID': 3}
        fields = dict(Instance_ID='3', Seat_Number='12A', Class='Economy',
                      Booking_Price='100', Booking_Status='Confirmed',
                      Payment_Method='UPI', Payment_Status='Payment Received')
        cur = MagicMock()
        cur.fetchone.side_effect = [
            {'Flight_Instance_Status': 'Scheduled'}, {'Booking_ID': 1}, None, {'Payment_ID': 7}]
        with patch('routes.Bookings.fetch_one', return_value=booking), patch('routes.Bookings.transaction') as transaction:
            transaction.return_value.__enter__.return_value = cur
            response = self.client.post('/Booking/update/1', data=fields)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith('/Booking/'))
            writes = [call.args[0] for call in cur.execute.call_args_list if call.args[0].lstrip().startswith(('UPDATE', 'INSERT'))]
            self.assertEqual(len(writes), 2)
            self.assertFalse(any('Check_In' in sql or 'Baggage' in sql for sql in writes))

    def test_new_booking_creates_passenger_ticket_payment_only(self):
        fields = dict(First_Name='New', Last_Name='Traveler', Nationality='India',
                      Contact_Number='1234567890', Email='new@example.com',
                      Instance_ID='3', Seat_Number='12A', Class='Economy',
                      Booking_Price='100', Booking_Status='Confirmed',
                      Payment_Method='UPI', Payment_Status='Payment Received')
        cur = MagicMock()
        cur.fetchone.return_value = {'Flight_Instance_Status': 'Scheduled'}
        with patch('routes.Bookings.transaction') as transaction:
            transaction.return_value.__enter__.return_value = cur
            response = self.client.post('/Booking/add', data=fields)
            self.assertEqual(response.status_code, 302)
            writes = [call.args[0] for call in cur.execute.call_args_list if call.args[0].lstrip().startswith('INSERT')]
            self.assertEqual(len(writes), 3)
            for table, sql in zip(('Passenger', 'Booking', 'Payment'), writes):
                self.assertIn('INSERT INTO ' + table, sql)

    def test_invalid_fare_does_not_open_transaction(self):
        with patch('routes.Bookings.transaction') as transaction:
            self.client.post('/Booking/add', data={'Instance_ID': '1', 'Booking_Status': 'Confirmed', 'Booking_Price': '-1'})
            transaction.assert_not_called()

    def test_boarding_requires_checkin(self):
        with patch('routes.CheckIns.fetch_one', return_value={'Booking_ID': 1}), patch('routes.CheckIns.execute') as execute:
            self.client.post('/CheckIn/update/1', data={'CheckIn_Status': 'Pending', 'Boarding_Status': 'Boarded'})
            execute.assert_not_called()

    def test_checkin_delete_surfaces_procedure_validation(self):
        with patch('routes.CheckIns.execute', side_effect=ValueError('Delete baggage first.')) as execute:
            response = self.client.post('/CheckIn/delete/1')
            self.assertIn('/CheckIn/#checkin-workspace', response.location)
            execute.assert_called_once_with('CALL Delete_Check_In(%s)', (1,))
            with self.client.session_transaction() as session:
                self.assertIn('Delete baggage first.', session['_flashes'][-1][1])

    def test_baggage_delete_passes_booking_and_bag_to_procedure(self):
        with patch('routes.Baggage.execute', side_effect=ValueError('Wrong booking.')) as execute:
            response = self.client.post('/Baggage/delete/1/99')
            self.assertIn('/Baggage/#baggage-workspace', response.location)
            execute.assert_called_once_with('CALL Delete_Baggage(%s, %s)', (1, 99))

    def test_checkin_and_baggage_have_separate_crud_pages(self):
        booking = dict(Booking_ID=1, CheckIn_ID=2, Passenger_Name='Test Traveler',
                       Flight_Number='AF1', Scheduled_Departure='2026-12-01',
                       Seat_Number='12A', Booking_Status='Confirmed', Payment_Status='Payment Received',
                       CheckIn_Status='Checked-In', Boarding_Status='Not Boarded', CheckIn_Time='2026-12-01')
        bag = dict(Booking_ID=1, Passenger_Name='Test Traveler', Flight_Number='AF1', Baggage_ID=3, Baggage_Type='Cabin', Weight_KG='7', Baggage_Status='Checked-In')
        with patch('routes.CheckIns.fetch_all', return_value=[booking]):
            response = self.client.get('/CheckIn/')
            self.assertEqual(response.status_code, 200)
            body = response.data.split(b'<body', 1)[1]
            self.assertIn(b'/CheckIn/update/1', body)
            self.assertIn(b'<h2>Add check-in</h2>', body)
            self.assertIn(b'action="/CheckIn/add"', body)
            self.assertNotIn(b'<td><form action="/CheckIn/update/', body)
            self.assertIn(b'/CheckIn/delete/1', body)
            self.assertNotIn(b'<h2>Baggage records</h2>', body)
        with patch('routes.Baggage.fetch_all', side_effect=[[bag], [booking]]):
            response = self.client.get('/Baggage/')
            self.assertEqual(response.status_code, 200)
            body = response.data.split(b'<body', 1)[1]
            for action in ('/Baggage/add', '/Baggage/update/1/3', '/Baggage/delete/1/3'):
                self.assertIn(action.encode(), body)
            self.assertIn(b'<h2>Add baggage</h2>', body)
            self.assertNotIn(b'<td><form action="/Baggage/update/', body)
            self.assertNotIn(b'action="/CheckIn/update/', body)

    def test_mysql_time_format(self):
        self.assertEqual(html_time(timedelta(hours=7, minutes=5)), '07:05:00')
        self.assertEqual(html_time(None), '')


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.cur = self.conn.cursor.return_value
        self.cur.with_rows = True
        self.cur.nextset.side_effect = [True, None]
        self.patcher = patch('db.get_db_connection', return_value=self.conn)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_execute_drains_procedure_results_before_commit(self):
        db.execute('CALL Example(%s)', (1,))
        self.assertEqual(self.cur.nextset.call_count, 2)
        self.conn.commit.assert_called_once()
        self.cur.close.assert_called_once()
        self.conn.close.assert_called_once()

    def test_execute_rolls_back_on_error(self):
        self.cur.execute.side_effect = RuntimeError('failed')
        with self.assertRaises(RuntimeError):
            db.execute('CALL Example()')
        self.conn.rollback.assert_called_once()
        self.conn.commit.assert_not_called()
        self.conn.close.assert_called_once()

    def test_cursor_creation_failure_closes_connection(self):
        self.conn.cursor.side_effect = RuntimeError('failed')
        with self.assertRaises(RuntimeError):
            db.fetch_one('SELECT 1')
        self.conn.close.assert_called_once()

    def test_fetch_one_consumes_remaining_rows(self):
        self.cur.fetchone.return_value = {'id': 1}
        self.assertEqual(db.fetch_one('CALL Example()'), {'id': 1})
        self.assertEqual(self.cur.fetchall.call_count, 2)


if __name__ == '__main__':
    unittest.main()
