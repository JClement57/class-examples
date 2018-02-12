from flask import Flask, session, redirect, url_for, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Email, Length

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key for session application'

# Default route shows a simple home page.
@app.route('/')
def index():
    return render_template('index.html')

# Request a user name and password. Doesn't fiddle with hiding the password, etc.
class LoginForm(FlaskForm):
    username = StringField('Email', validators=[Length(min=1, max=40)])
    password = StringField('Password', validators=[Length(min=1, max=40)])
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
            session['username'] = login_form.username.data
            flash('User {} logged in'.format(session['username']))
            return redirect(url_for('index'))

    # Render the form if:
    # 1. This is a GET request and we want to send the empty form.
    # 2. This is a POST request and the form failed to validate.
    # 3. The form validated but the password was wrong.
    return render_template('login.html', form=login_form)

# Log out
@app.route('/logout')
def logout():
    # Remove the 'username' entry from the session.
    # The pop() method behaves as follows:
    # 1. If 'username' is in the session, remove it and return its value.
    #    The value will be the user name stored there by the login() view function.
    #    Removing the username from the session has the effect of logging out the user.
    # 2. If 'username' is not in the session, return the second argument (None)
    user_name = session.pop('username', None)
    flash('User {} logged out'.format(user_name))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
