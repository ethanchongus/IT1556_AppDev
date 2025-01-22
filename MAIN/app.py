from flask import Flask, render_template
from transaction import transaction_bp  # Import the Blueprint
from cart import cart_bp  # Import the cart Blueprint

app = Flask(__name__)

# Set the secret key for the Flask app
app.secret_key = "eatmylampa"  # Replace with a strong, unique key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transaction/')
def transaction():
    return render_template('customer_transaction.html')

app.register_blueprint(transaction_bp)

@app.route('/admin/')
def admin():
    return render_template('admin_panel.html')

@app.route('/admin/transaction/')
def admin_transaction():
    return render_template('admin_transaction.html')

@app.route('/activities/')
def activities():
    return render_template('customer_activities.html')

# Register the cart Blueprint
app.register_blueprint(cart_bp, url_prefix='/cart')

if __name__ == '__main__':
    app.run(debug=True)