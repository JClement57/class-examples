from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Super Secret Unguessable Key'


@app.route('/')
def index():
    return redirect(url_for('fixed'))


@app.route('/fixed')
def fixed():
    return render_template('fixed-content.html')


@app.route('/responsive-small')
def responsive_small():
    return render_template('responsive-small.html')


@app.route('/responsive-medium')
def responsive_medium():
    return render_template('responsive-medium.html')


# Make this the last line in the file!
if __name__ == '__main__':
    app.run(debug=True)
