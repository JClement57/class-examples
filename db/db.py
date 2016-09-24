import sqlite3
from flask import g
from application import app

import os

##### Database Utilities ########################################

DATABASE = 'test-db.sqlite'


# Connect to the database.
def connect_db(db_path):
    if db_path is None:
        db_path = os.path.join(os.getcwd(), DATABASE)
    if not os.path.isfile(db_path):
        raise RuntimeError("Can't find database file '{}'".format(db_path))
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


# Open a database connection and hang on to it in the global object.
def open_db_connection(db_path=None):
    """Open a connection to the database.

    Open a connection to the SQLite database at `db_path`.
    Store the resulting connection in the `g.db` global object.
    """
    g.db = connect_db(db_path)


# If the database is open, close it.
def close_db_connection():
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

##### Users and Comments ########################################

# List all users in the database.
def all_users():
    cursor = g.db.execute('select * from user')
    return cursor.fetchall()

# List all comments in the database.
def all_comments():
    query = '''
SELECT first_name, last_name, email, body
FROM user INNER JOIN comment ON user.email = comment.user
ORDER BY last_name ASC, first_name ASC'''
    return g.db.execute(query).fetchall()

# Look up a single user
def find_user(email):
    return g.db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()

# Retrieve comments for a user with the given e-mail address.
def comments_by_user(email):
    cursor = g.db.execute('SELECT * FROM comment WHERE user = ?', (email,))
    return cursor.fetchall()

# Update a user's profile (first and last name)
def update_user(email, first_name, last_name):
    query ='''
UPDATE user SET first_name = :first, last_name = :last
WHERE email = :email'''
    cursor = g.db.execute(query, {'first': first_name, 'last': last_name, 'email': email})
    g.db.commit()
    return cursor.rowcount

# Add a user profile
def add_user(email, first_name, last_name, password):
    insert_stmt = '''INSERT INTO user(email, first_name, last_name, password)
VALUES(:email, :first, :last, :pass)'''
    cursor = g.db.execute(insert_stmt, {'email': email, 'first': first_name, 'last': last_name, 'pass': password})
    g.db.commit()
    return cursor.rowcount

##### Accounts ########################################

# Return all data in the account table.
def all_accounts():
    return g.db.execute('SELECT * FROM account').fetchall()

# Return the balance for the account with id 'account_id'.
def find_account(account_id):
    return g.db.execute('SELECT * FROM account WHERE id=:id', {'id': account_id}).fetchone()

# Get the balance for an account.
def read_balance(account_id):
    cursor = g.db.execute('SELECT balance FROM account WHERE id=:id', {'id': account_id})
    row = cursor.fetchone()
    return row['balance']

# Set the balance in account 'account_id' to 'new_balance'. Note that this
# function does not commit to the database so that we can illustrate commit
# and rollback behavior in the transfer_funds function.
def update_balance(account_id, new_balance):
    cursor = g.db.execute('UPDATE account SET balance = :balance WHERE id=:id',
                          {'id': account_id, 'balance': new_balance})
    if cursor.rowcount != 1:
        raise RuntimeError("Failed to update account {}".format(account_id))

# Transfer funds
def transfer_funds(from_account_id, to_account_id, transfer_amount, cause_rollback):
    # Get the balance of the source account.
    from_balance = read_balance(from_account_id)

    # Ensure sufficient funds; we've already checked this in the controller,
    # but it doesn't hurt to make sure a transfer is valid.
    if from_balance < transfer_amount:
        raise RuntimeError('Insufficient funds')

    # Get the balance of the destination account.
    to_balance = read_balance(to_account_id)

    # Transfer funds!
    update_balance(from_account_id, from_balance - transfer_amount)
    update_balance(to_account_id, to_balance + transfer_amount)

    # Either roll back or commit the current transaction.
    if cause_rollback:
        # Roll back. To demonstrate that database updates are reversed
        # during a rollback, create a message containing the current
        # account balances.
        pending_from_balance = read_balance(from_account_id)
        pending_to_balance = read_balance(to_account_id)
        message = "Rolled back transaction: from was {:.2f}, to was {:.2f}".format(pending_from_balance,
                                                                                   pending_to_balance)
        # Roll back the transaction and return the message
        g.db.rollback()
        return message
    else:
        # Commit the transaction. The user can see that the database updates are
        # persistent by viewing the current account balances.
        g.db.commit()
        return "Committed transaction"
