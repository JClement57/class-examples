from flask import Flask, render_template
from flask.ext.babel import Babel, gettext, ngettext
_ = gettext

app = Flask(__name__)
babel = Babel(app)
app.config['SECRET_KEY'] = 'Super Secret Unguessable Key'
app.config['BABEL_DEFAULT_LOCALE'] = 'es'



@app.route('/')
def index():
    # Can supply additional arguments to the string:
    spinal_tap = _('Ours goes to %(limit)s', limit=11)

    vizzini_says = _('Inconceivable!')
    inigo_says = _('Hello! My name is Inigo Montoya')
    princess_bride = _('Vizzini: %(viz)s; Inigo: %(im)s',
                       viz=vizzini_says,
                       im=inigo_says)

    # Variant of 'gettext' for singular/plural
    blind_mice = ngettext('%(num)d blind mouse', '%(num)d blind mice', 3);

    return render_template('index.html', messages=[_('Hello, World'),
                                                   spinal_tap,
                                                   princess_bride,
                                                   blind_mice,
                                                   _('Fred lives in Peru')])


# This must be the last line in this file!
app.run(debug=True)
