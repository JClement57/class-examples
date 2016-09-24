from flask import Flask, render_template, redirect, url_for, flash

from flask.ext.login import LoginManager, login_user, logout_user, login_required
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zippy zappy zoopy'      # Needed because we're doing WTForms

login_mgr = LoginManager(app)                       # Simple way to initialize

# Fake up a "database" of users and an authentication function.
valid_users = [
    { 'email': 'fred@ziffle.com', 'password': 'fred-pass' },
    { 'email': 'zelda@ziffle.com', 'password': 'zelda-pass'},
]


def authenticate(email, password):
    """Check whether the arguments match a user from the "database" of valid users."""
    for user in valid_users:
        if email == user['email'] and password == user['password']:
            return email
    return None


class User(object):
    """Class for the currently logged-in user (if there is one). Only stores the user's e-mail."""
    def __init__(self, email):
        self.email = email
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        """Return the unique ID for this user. Used by Flask-Login to keep track of the user in the session object."""
        return self.email

    def __repr__(self):
        return "<User '{}' {} {} {}>".format(self.email, self.is_authenticated, self.is_active, self.is_anonymous)


# Flask-Login calls this function on every request to recreate the current user object
# based on the unique ID it stored previously the session object.
@login_mgr.user_loader
def load_user(id):
    """Return the currently logged-in user when given the user's unique ID"""
    return User(id)


class LoginForm(Form):
    email = StringField('E-mail Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user log in"""
    form = LoginForm()
    if form.validate_on_submit():
        if authenticate(form.email.data, form.password.data):
            # Credentials authenticated.
            # Create the user object, let Flask-Login know, and redirect to the home page
            user = User(form.email.data)
            login_user(user)
            flash('Logged in successfully as {}'.format(form.email.data))
            return redirect(url_for('index'))
        else:
            # Authentication failed.
            flash('Invalid email address or password')
    # Show the login page. Provide some cheat notes.
    return render_template('login.html', form=form, hacker_news=valid_users)


@app.route('/logout')
@login_required
def logout():
    """Log out the user."""
    logout_user()
    flash('Logged out')
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
