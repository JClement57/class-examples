from flask import Flask, render_template

app = Flask(__name__)


# Default hello, world template
@app.route('/')
def hello_world():
    print("Got into hello world view function.")
    return render_template('hello.html')


@app.route('/home')
def home_page():
    """Display a workable home page."""
    return render_template('home.html')


# Pass single argument to template
@app.route('/name')
def hello_name():
    return render_template('hello-name.html', name='Zelda Ziffle')


# Pass single argument to template from URL
@app.route('/name/<who>')
def hello_name_from_url(who):
    return render_template('hello-name.html', name=who)


# List in template
@app.route('/comments')
def comments():
    fake_comments = [{'who': 'Wesley',
                      'what': 'As you wish!'},
                     {'who': 'Vincini',
                      'what': 'Inconceivable'},
                     {'who': 'Old Woman',
                      'what': 'You had love in your heart'}
                     ]
    return render_template('comments.html', comments=fake_comments)


# Template Inheritance
@app.route('/base')
def base():
    return render_template('base.html')


@app.route('/one')
def child_page_one():
    return render_template('child_one.html')


@app.route('/two')
def child_page_two():
    return render_template('child_two.html')


# Run like the wind, Bullseye!
if __name__ == '__main__':
    app.run(debug=True)
