# Based on example from Flask documentation:
# http://flask.pocoo.org/docs/0.12/quickstart/#sessions

from flask import Flask, render_template, session, request, redirect, url_for


app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'


@app.route('/')
def index():
    if 'user' in session:
        return render_template("member.html",
                               message='Logged in as {}'.format(session['user']['name']))
    else:
        return render_template("guest.html",
                               message="You are not logged in");


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        session['user'] = {
            'name': request.form['name'],
            'email': request.form['email']
        }
        return redirect(url_for('index'))
    else:
        return render_template("signup.html", message="Please sign up")


@app.route('/logout')
def log_out():
    # Remove username from session if present
    session.pop('user', None)
    return redirect(url_for('index'))


# Go!
app.run(debug=True)
