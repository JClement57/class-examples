from flask import Flask, render_template, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FloatField, PasswordField, BooleanField, ValidationError
from wtforms.validators import Email, Length, DataRequired, NumberRange, InputRequired, EqualTo

import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Super Secret Unguessable Key'


@app.before_request
def before():
    db.open_db_connection()


@app.teardown_request
def after(exception):
    db.close_db_connection()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/users')
def all_users():
    return render_template('all-users.html', users=db.all_users())


@app.route('/comments')
def all_comments():
    return render_template('all-comments.html', comments=db.all_comments())


@app.route('/comments/<email>')
def user_comments(email):
    user = db.find_user(email)
    if user is None:
        flash('No user with email {}'.format(email))
        comments = []
    else:
        comments = db.comments_by_user(email)
    return render_template('user-comments.html', user=user, comments=comments)


# Create a form for manipulating user informat.
class UserForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    first_name = StringField('First Name', validators=[Length(min=1, max=40)])
    last_name = StringField('Last Name', validators=[Length(min=1, max=40)])
    password = PasswordField('New Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Save User')


# Create a user
@app.route('/users/create', methods=['GET', 'POST'])
def create_user():
    # Create new user form. Will automatically populate from request.form.
    user_form = UserForm()

    # The validate_on_submit() method checks for two conditions.
    # 1. If we're handling a GET request, it returns false,
    #    and we fall through to render_template(), which sends the empty form.
    # 2. Otherwise, we're handling a POST request, so it runs the validators on the form,
    #    and returns false if any fail, so we also fall through to render_template()
    #    which renders the form and shows any error messages stored by the validators.
    if user_form.validate_on_submit():
        user = db.find_user(user_form.email.data)

        if user is not None:
            flash("User {} already exists".format(user_form.email.data));
        else:
            rowcount = db.create_user(user_form.email.data,
                                      user_form.first_name.data,
                                      user_form.last_name.data,
                                      user_form.password.data)

            if rowcount == 1:
                flash("User {} created".format(user_form.email.data))
                return redirect(url_for('index'))
            else:
                flash("New user not created");

    # We will get here under any of the following conditions:
    # 1. We're handling a GET request, so we render the (empty) form.
    # 2. We're handling a POST request, and some validator failed, so we render the
    #    form with the same values so that the user can try again. The template
    #    will extract and display the error messages stored on the form object
    #    by the validators that failed.
    # 3. The email entered in the form corresponds to an existing user.
    #    The template will render an error message from the flash.
    # 4. Something happened when we tried to update the database (rowcount != 1).
    #    The template will render an error message from the flash.
    return render_template('user-form.html', form=user_form, mode='create')


# Update user information.
@app.route('/users/update/<email>', methods=['GET', 'POST'])
def update_user(email):
    # Retrieve user data.
    row = db.find_user(email)

    if row is None:
        flash("User {} doesn't exist".format(email))
        return redirect(url_for('all_users'));

    # Initialize object with form data if available (this is the default behavior for a FlaskForm;
    # you need not even provide the argument. Otherwise initialize with specific values fetched
    # previously from the database.
    user_form = UserForm(email=row['email'],
                         first_name=row['first_name'],
                         last_name=row['last_name'])

    if user_form.validate_on_submit():
        # If we get here, we're handling a POST request and the form validated successfully.
        rowcount = db.update_user(email,
                                  user_form.first_name.data,
                                  user_form.last_name.data,
                                  user_form.password.data)

        # We're updating a single row, so we're successful if the row count is one.
        if rowcount == 1:
            # Everything worked. Flash a success message and redirect to the home page.
            flash("User '{}' updated".format(email))
            return redirect(url_for('index'))

        else:  # The update operation failed for some reason. Flash a message.
            flash('User not updated')

    return render_template('user-form.html', form=user_form, mode='update', )


@app.route('/accounts')
def all_accounts():
    return render_template('all-accounts.html', accounts=db.all_accounts())


class FundsTransferForm(FlaskForm):
    from_account = SelectField('From Account', coerce=int, validators=[DataRequired()])
    to_account = SelectField('To Account', coerce=int, validators=[DataRequired()])
    amount = FloatField('Amount', validators=[NumberRange(min=0.01)])
    cause_rollback = BooleanField('Cause Rollback')
    submit = SubmitField('Transfer Funds')

    def validate_to_account(form, field):
        if form.from_account.data == form.to_account.data:
            raise ValidationError("Destination account can't be the same as source account")


def account_details(account):
    return "{} ({:.2f})".format(account['name'], account['balance'])


@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    xfer_form = FundsTransferForm()
    all_accounts = db.all_accounts()

    # Set choices for the "from" account using an ordinary loop
    xfer_form.from_account.choices = []
    for account in all_accounts:
        xfer_form.from_account.choices.append((account['id'], account_details(account)))

    # Set choices for the "to" account using list comprehension
    xfer_form.to_account.choices = [(acct['id'], account_details(acct)) for acct in all_accounts]

    if xfer_form.validate_on_submit():
        # Assume we can do the transfer
        can_do_transfer = True

        # Make sure the source account exists.
        from_account = db.find_account(xfer_form.from_account.data)
        if from_account is None:
            can_do_transfer = False
            flash("The From account doesn't exist")

        # Make sure the destination account exists.
        to_account = db.find_account(xfer_form.to_account.data)
        if to_account is None:
            can_do_transfer = False
            flash("The To account doesn't exist")

        # There must be sufficient funds for the requested transfer
        transfer_amount = xfer_form.amount.data
        if from_account['balance'] < transfer_amount:
            can_do_transfer = False
            flash("Insufficient funds: balance in {} is {:.2f}, amount is {:.2f}".format(from_account['name'],
                                                                                         from_account['balance'],
                                                                                         transfer_amount))
        if can_do_transfer:
            # Everything checks out; transfer!
            message = db.transfer_funds(from_account['id'],
                                        to_account['id'],
                                        transfer_amount,
                                        xfer_form.cause_rollback.data)
            flash("Transferred {:.2f} from {} to {}".format(transfer_amount,
                                                            from_account['name'],
                                                            to_account['name']))
            flash("Message from model layer: {}".format(message))
            return redirect(url_for('all_accounts'))

    return render_template('transfer-funds.html', form=xfer_form)


# Make this the last line in the file!
if __name__ == '__main__':
    app.run(debug=True)
