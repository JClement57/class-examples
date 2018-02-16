from flask import Flask, session, redirect, url_for, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import Email, Length

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key for session application'


# Default route shows a simple home page.
@app.route('/')
def index():
    return render_template('index.html')


# Log in form with validation.
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[Length(min=6, max=40)])
    remember = BooleanField('Remember me on this machine', default=False)
    submit = SubmitField('Log In')


# Log in
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Use the form we've just defined
    login_form = LoginForm()

    if login_form.validate_on_submit():
        # If we get here, we've received a POST request and
        # our login form has been validated.
        if login_form.password.data != 'password':
            # Bogus password
            flash('Invalid password')
        else:
            # Correct password. Add a value to the session object
            # to show that the user is logged in. Redirect to home page.
            session['email'] = login_form.email.data
            session['remember'] = login_form.remember.data
            flash('User {} logged in'.format(session['email']))
            return redirect(url_for('index'))

    # Render the form if:
    # 1. This is a GET request and we want to send the empty form.
    # 2. This is a POST request and the form failed to validate.
    # 3. The form validated but the password was wrong.
    return render_template('login.html', form=login_form)


# Log out
@app.route('/logout')
def logout():
    # Remove the 'email' entry from the session.
    # The pop() method behaves as follows:
    # 1. If 'email' is in the session, remove it and return its value.
    #    The value will be the user name stored there by the login() view function.
    #    Removing the email from the session has the effect of logging out the user.
    # 2. If 'email' is not in the session, return the second argument (None)
    session.pop('remember', None)
    user_name = session.pop('email', None)
    flash('User {} logged out'.format(user_name))
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
