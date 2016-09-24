import tempfile
import unittest
import os

from flask import g, url_for

import db
from application import app


@unittest.skip
class TrivialTestCase(unittest.TestCase):
    # This method is invoked before EVERY test_xxx method.
    def setUp(self):
        print("In setUp method")

    # This method is invoked after EVERY test_xxx method.
    def tearDown(self):
        print("In tearDown method")

    def test_should_pass(self):
        print("In test_should_pass")
        self.assertTrue(1 == 1)

    @unittest.expectedFailure
    def test_should_fail(self):
        print("In test_should_fail")
        self.assertTrue(1 == 2)


class FlaskTestCase(unittest.TestCase):
    # This is a helper class that sets up the proper Flask execution context
    # so that the test cases that inherit it will work properly.
    def setUp(self):
        # Allow exceptions (if any) to propagate to the test client.
        app.testing = True

        # Create a test client.
        self.client = app.test_client(use_cookies=True)

        # Create an application context for testing.
        self.app_context = app.test_request_context()
        self.app_context.push()

    def tearDown(self):
        # Clean up the application context.
        self.app_context.pop()


class ApplicationTestCase(FlaskTestCase):
    """Test the basic behavior of page routing and display"""

    def test_home_page(self):
        """Verify the home page."""
        resp = self.client.get('/')
        self.assertTrue('Welcome' in resp.data, "Didn't find welcome message on home page")

    def test_user_page(self):
        """Verify the user page."""
        resp = self.client.get(url_for('all_users'))
        self.assertTrue('Click for Comments' in resp.data)


class DatabaseTestCase(FlaskTestCase):
    """Test database access and update functions."""

    # This method is invoked once before all the tests in this test case.
    @classmethod
    def setUpClass(cls):
        """So that we don't overwrite application data, create a temporary database file."""
        (file_descriptor, cls.file_name) = tempfile.mkstemp()
        os.close(file_descriptor)

    # This method is invoked once after all the tests in this test case.
    @classmethod
    def tearDownClass(cls):
        """Remove the temporary database file."""
        os.unlink(cls.file_name)

    @staticmethod
    def execute_script(resource_name):
        """Helper function to run a SQL script on the test database."""
        with app.open_resource(resource_name, mode='r') as f:
            g.db.cursor().executescript(f.read())
        g.db.commit()

    def setUp(self):
        """Open the database connection and create all the tables."""
        super(DatabaseTestCase, self).setUp()
        db.open_db_connection(self.file_name)
        self.execute_script('db/create-db.sql')

    def tearDown(self):
        """Clear all tables in the database and close the connection."""
        self.execute_script('db/clear-db.sql')
        db.close_db_connection()
        super(DatabaseTestCase, self).tearDown()

    def test_add_user(self):
        """Make sure we can add a new user."""
        row_count = db.add_user('test@example.com', 'FirstName', 'LastName', 'pass')
        self.assertEqual(row_count, 1)

        test_user = db.find_user('test@example.com')
        self.assertIsNotNone(test_user)

        self.assertEqual(test_user['first_name'], 'FirstName')
        self.assertEqual(test_user['last_name'], 'LastName')

    def test_update_user(self):
        """Add and then update a user."""
        row_count = db.add_user('test@example.com', 'FirstName', 'LastName', 'pass')
        self.assertEqual(row_count, 1)

        row_count = db.update_user('test@example.com', 'NewFirstName', 'LastName')
        self.assertEqual(row_count, 1)

        test_user = db.find_user('test@example.com')
        self.assertIsNotNone(test_user)

        self.assertEqual(test_user['first_name'], 'NewFirstName')
        self.assertEqual(test_user['last_name'], 'LastName')


# Do the right thing if this file is run standalone.
if __name__ == '__main__':
    unittest.main()
