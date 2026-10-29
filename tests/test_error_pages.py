import unittest
from unittest.mock import patch

from mysql.connector import OperationalError
from werkzeug.exceptions import TooManyRequests

from app import app, handle_http_error


class ErrorPagesTest(unittest.TestCase):
    def setUp(self):
        self.config = patch.dict(app.config, TESTING=True, PROPAGATE_EXCEPTIONS=False)
        self.config.start()
        self.addCleanup(self.config.stop)
        self.client = app.test_client()

    def test_missing_page_has_custom_design_and_correct_status(self):
        response = self.client.get('/a-page-that-does-not-exist')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'A little off course', response.data)
        self.assertIn(b'class="error-page"', response.data)
        self.assertIn(b'css/errors.css', response.data)
        self.assertIn(b'Back to dashboard', response.data)

    def test_missing_record_uses_same_page(self):
        with patch('routes.Passengers.fetch_one', return_value=None):
            response = self.client.get('/Passenger/update/999999')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'A little off course', response.data)

    def test_method_not_allowed_preserves_allow_header(self):
        response = self.client.post('/')
        self.assertEqual(response.status_code, 405)
        self.assertIn('GET', response.headers['Allow'])
        self.assertIn(b'A different route is needed', response.data)

    def test_rate_limit_preserves_retry_after(self):
        with app.test_request_context('/'):
            response = handle_http_error(TooManyRequests(retry_after=60))
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers['Retry-After'], '60')

    def test_unexpected_failure_hides_exception_details(self):
        with patch('app.fetch_one', side_effect=RuntimeError('private-internal-details')), patch.object(app.logger, 'error'):
            response = self.client.get('/')
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'An unexpected stop', response.data)
        self.assertNotIn(b'private-internal-details', response.data)
        self.assertNotIn(b'Traceback', response.data)

    def test_database_failure_has_service_page_without_database_details(self):
        with patch('app.fetch_one', side_effect=OperationalError('private-db-details')), patch.object(app.logger, 'error'):
            response = self.client.get('/')
        self.assertEqual(response.status_code, 503)
        self.assertIn(b'A short operational pause', response.data)
        self.assertNotIn(b'private-db-details', response.data)


if __name__ == '__main__':
    unittest.main()
