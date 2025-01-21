from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/')
def admin():
    return render_template('admin_panel.html')

@app.route('/admin/transaction/')
def admin_transaction():
    return render_template('admin_transaction.html')



if __name__ == '__main__':
    app.run(debug=True)