from flask import Flask, render_template, redirect, url_for
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'very secret-y key value; shhhhh!'


def db_connect():
    # Update to correspond to your MySQL server and schema.
    conn = mysql.connector.connect(user='test', password='password',
                                   host='localhost', database='flask_test')
    return conn

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/users')
def show_users():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    conn.close()
    return render_template('show-users.html', users=users)


class UserForm(Form):
    username = StringField('User Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit User')


@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    user_form = UserForm()
    if user_form.validate_on_submit():
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user (username, password) VALUES (%(username)s, %(password)s)",
                       {'username': user_form.username.data,
                        'password': user_form.password.data})
        conn.commit()
        conn.close()
        return redirect(url_for('show_users'))
    return render_template('add-user.html', form=user_form)

if __name__ == '__main__':
    app.run(debug=True)
