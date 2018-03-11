from flask import Flask, render_template, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FloatField, PasswordField, BooleanField, ValidationError
from wtforms.validators import Email, Length, DataRequired, NumberRange, InputRequired, EqualTo

import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Super Secret Unguessable Key'

@app.before_request
def before_request():
    db.open_db_connection()


@app.teardown_request
def teardown_request(exception):
    db.close_db_connection()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/members')
def all_members():
    return render_template('all-members.html', members=db.all_members())


@app.route('/comments')
def all_comments():
    return render_template('all-comments.html', comments=db.all_comments())


@app.route('/comments/<email>')
def member_comments(email):
    member = db.find_member(email)
    if member is None:
        flash('No member with email {}'.format(email))
        comments = []
    else:
        comments = db.comments_by_member(email)
    return render_template('member-comments.html', member=member, comments=comments)


# Create a form for manipulating member informat.
class MemberForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    first_name = StringField('First Name', validators=[Length(min=1, max=40)])
    last_name = StringField('Last Name', validators=[Length(min=1, max=40)])
    password = PasswordField('New Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Save Member')


# Create a member
@app.route('/members/create', methods=['GET', 'POST'])
def create_member():
    # Create new member form. Will automatically populate from request.form.
    member_form = MemberForm()

    # The validate_on_submit() method checks for two conditions.
    # 1. If we're handling a GET request, it returns false,
    #    and we fall through to render_template(), which sends the empty form.
    # 2. Otherwise, we're handling a POST request, so it runs the validators on the form,
    #    and returns false if any fail, so we also fall through to render_template()
    #    which renders the form and shows any error messages stored by the validators.
    if member_form.validate_on_submit():
        member = db.find_member(member_form.email.data)

        if member is not None:
            flash("Member {} already exists".format(member_form.email.data));
        else:
            rowcount = db.create_member(member_form.email.data,
                                        member_form.first_name.data,
                                        member_form.last_name.data,
                                        member_form.password.data)

            if rowcount == 1:
                flash("Member {} created".format(member_form.email.data))
                return redirect(url_for('all_members'))
            else:
                flash("New member not created");

    # We will get here under any of the following conditions:
    # 1. We're handling a GET request, so we render the (empty) form.
    # 2. We're handling a POST request, and some validator failed, so we render the
    #    form with the same values so that the member can try again. The template
    #    will extract and display the error messages stored on the form object
    #    by the validators that failed.
    # 3. The email entered in the form corresponds to an existing member.
    #    The template will render an error message from the flash.
    # 4. Something happened when we tried to update the database (rowcount != 1).
    #    The template will render an error message from the flash.
    return render_template('member-form.html', form=member_form, mode='create')


# Update member information.
@app.route('/members/update/<email>', methods=['GET', 'POST'])
def update_member(email):
    # Retrieve member data.
    row = db.find_member(email)

    if row is None:
        flash("Member {} doesn't exist".format(email))
        return redirect(url_for('all_members'));

    # Initialize object with form data if available (this is the default behavior for a FlaskForm;
    # you need not even provide the argument. Otherwise initialize with specific values fetched
    # previously from the database.
    member_form = MemberForm(email=row['email'],
                             first_name=row['first_name'],
                             last_name=row['last_name'])

    if member_form.validate_on_submit():
        # If we get here, we're handling a POST request and the form validated successfully.
        rowcount = db.update_member(email,
                                    member_form.first_name.data,
                                    member_form.last_name.data,
                                    member_form.password.data)

        # We're updating a single row, so we're successful if the row count is one.
        if rowcount == 1:
            # Everything worked. Flash a success message and redirect to the home page.
            flash("Member '{}' updated".format(email))
            return redirect(url_for('all_members'))

        else:  # The update operation failed for some reason. Flash a message.
            flash('Member not updated')

    return render_template('member-form.html', form=member_form, mode='update')


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
