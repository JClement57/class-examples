from flask import g
import psycopg2
import psycopg2.extras

# Database Utilities ########################################

data_source_name = "dbname=isd user=tom host=localhost"


def open_db_connection():
    """Open a connection to the database.

    Open a connection to the SQLite database at `db_path`.
    Store the resulting connection in the `g.sql` global object.
    """
    g.connection = psycopg2.connect(data_source_name)
    g.cursor = g.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)


def close_db_connection():
    g.cursor.close()
    g.connection.close()


# Users and Comments ########################################


def create_member(email, first_name, last_name, password):
    """Create a new member."""
    query = '''
INSERT INTO member (email, first_name, last_name, password)
VALUES (%(email)s, %(first)s, %(last)s, %(pass)s)
    '''
    g.cursor.execute(query, {'email': email, 'first': first_name, 'last': last_name, 'pass': password})
    g.connection.commit()
    return g.cursor.rowcount


def init_photo(email):
    """Create a photo record and return its ID"""
    query_dictionary = {'email': email}
    g.cursor.execute("INSERT INTO photo (member_email) VALUES (%(email)s)", query_dictionary)
    g.connection.commit()

    g.cursor.execute("SELECT * FROM photo WHERE member_email = (%(email)s)", query_dictionary)
    return g.cursor.fetchone()


def set_photo(photo_id, file_path):
    """Update a photo record with the proper file name"""
    query = """
    UPDATE photo SET file_path = %(file_path)s
    WHERE id = %(id)s
    """
    g.cursor.execute(query, {'file_path': file_path, 'id': photo_id})
    g.connection.commit()
    return g.cursor.rowcount


def last_photo_seq():
    g.cursor.execute('SELECT last_value FROM photo_id_seq')
    return g.cursor.fetchone()[0]


def all_members():
    """List all members."""
    g.cursor.execute('SELECT * FROM member ORDER BY email')
    return g.cursor.fetchall()


def all_comments():
    """List all comments."""
    query = '''
SELECT first_name, last_name, email, body
FROM member INNER JOIN comment ON member.email = comment.member
ORDER BY last_name ASC, first_name ASC'''
    g.cursor.execute(query)
    return g.cursor.fetchall()


def find_member(memberEmail):
    """Look up a single member."""
    query = """
    SELECT m.email, m.first_name, m.last_name, p.file_path
    FROM member AS m
       LEFT OUTER JOIN photo AS p ON m.email = p.member_email 
    WHERE email = %(emailParam)s
    """
    g.cursor.execute(query, {'emailParam': memberEmail})
    return g.cursor.fetchone()


def comments_by_member(email):
    """Retrieve comments for a member with the given e-mail address."""
    g.cursor.execute('SELECT * FROM comment WHERE member = %(email)s', {'email': email})
    return g.cursor.fetchall()


def update_member(email, first_name, last_name, password):
    """Update a member's profile."""
    query = '''
UPDATE member SET first_name = %(first)s, last_name = %(last)s, password = %(pass)s
WHERE email = %(email)s
    '''
    g.cursor.execute(query, {'first': first_name, 'last': last_name, 'email': email, 'pass': password})
    g.connection.commit()
    return g.cursor.rowcount


# Accounts ########################################

def all_accounts():
    """Return all data in the account table."""
    g.cursor.execute('SELECT * FROM account ORDER BY name')
    return g.cursor.fetchall()


def find_account(account_id):
    """Return the balance for the account with id 'account_id'."""
    g.cursor.execute('SELECT * FROM account WHERE id=%(id)s', {'id': account_id})
    return g.cursor.fetchone()


def read_balance(account_id):
    """Get the balance for an account."""
    g.cursor.execute('SELECT balance FROM account WHERE id=%(id)s', {'id': account_id})
    row = g.cursor.fetchone()
    return row['balance']


def update_balance(account_id, new_balance):
    """Set the balance in account 'account_id' to 'new_balance'.

    Note that this function does not commit to the database
    so that we can illustrate commit and rollback behavior
    in the transfer_funds function.
    """
    g.cursor.execute('UPDATE account SET balance = %(balance)s WHERE id=%(id)s',
                     {'id': account_id, 'balance': new_balance})
    if g.cursor.rowcount != 1:
        raise RuntimeError("Failed to update account {}".format(account_id))


def transfer_funds(from_account_id, to_account_id, transfer_amount, cause_rollback):
    """Transfer funds."""

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
        g.connection.rollback()
        return message
    else:
        # Commit the transaction. The member can see that the database updates are
        # persistent by viewing the current account balances.
        g.connection.commit()
        return "Committed transaction"
