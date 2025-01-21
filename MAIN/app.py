from flask import Flask, render_template
from user import *
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/')
def admin():
    return render_template('admin_panel.html')

if __name__ == '__main__':
    app.run(debug=True)