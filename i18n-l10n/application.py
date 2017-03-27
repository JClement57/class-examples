from flask import Flask, render_template
from flask.ext.babel import Babel, gettext, ngettext
_ = gettext

app = Flask(__name__)
babel = Babel(app)
app.config['SECRET_KEY'] = 'Super Secret Unguessable Key'
app.config['BABEL_DEFAULT_LOCALE'] = 'es'


@app.route('/')
def index():
    return render_template('index.html', messages=[_('Hello, World')])


# This must be the last line in this file!
app.run(debug=True)
