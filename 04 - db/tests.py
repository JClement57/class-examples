import tempfile
import unittest
import os

from flask import g, url_for

import db
from application import app


# @unittest.skip
class TrivialTestCase(unittest.TestCase):
    # This method is invoked before EVERY test_xxx method.
    def setUp(self):
        print("In setUp method")

    # This method is invoked after EVERY test_xxx method.
    def tearDown(self):
        print("In tearDown method")

    def test_should_pass(self):
        print("In test_should_pass")
        self.assertEqual(1, 1, "Expect this to succeed")

    def test_should_also_pass(self):
        print("In test_should_also_pass")
        self.assertTrue(17 < 42, "Expect this to succeed also")

    # @unittest.expectedFailure
    # def test_should_fail(self):
    #     print("In test_should_fail")
    #     self.assertTrue(1 == 2, "Expect this to fail")


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
        self.assertTrue(b'Welcome' in resp.data, "Didn't find welcome message on home page")

    def test_member_page(self):
        """Verify the member page."""
        resp = self.client.get(url_for('all_members'))
        self.assertTrue(b'Comments' in resp.data)


class DatabaseTestCase(FlaskTestCase):
    """Test database access and update functions."""

    @staticmethod
    def execute_sql(resource_name):
        """Helper function to run a SQL script on the test database."""
        with app.open_resource(resource_name, mode='r') as f:
            g.cursor.execute(f.read())
        g.connection.commit()

    def setUp(self):
        """Open the database connection and create all the tables."""
        super(DatabaseTestCase, self).setUp()
        db.open_db_connection()
        self.execute_sql('sql/create-db.sql')

    def tearDown(self):
        """Clear all tables in the database and close the connection."""
        db.close_db_connection()
        super(DatabaseTestCase, self).tearDown()

    def test_add_member(self):
        """Make sure we can add a new member."""
        row_count = db.create_member('test@example.com', 'FirstName', 'LastName', 'pass')
        self.assertEqual(row_count, 1)

        test_member = db.find_member('test@example.com')
        self.assertIsNotNone(test_member)

        self.assertEqual(test_member['first_name'], 'FirstName')
        self.assertEqual(test_member['last_name'], 'LastName')

    def test_update_member(self):
        """Add and then update a member."""
        row_count = db.create_member('test@example.com', 'FirstName', 'LastName', 'pass')
        self.assertEqual(row_count, 1)

        row_count = db.update_member('test@example.com', 'NewFirstName', 'LastName', 'newpass')
        self.assertEqual(row_count, 1)

        test_member = db.find_member('test@example.com')
        self.assertIsNotNone(test_member)

        self.assertEqual(test_member['first_name'], 'NewFirstName')
        self.assertEqual(test_member['last_name'], 'LastName')


# Do the right thing if this file is run standalone.
if __name__ == '__main__':
    unittest.main()
