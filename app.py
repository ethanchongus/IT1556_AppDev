from flask import Flask, render_template
from payment_routes import payment_bp
from admin_routes import admin_bp

# Initialize the Flask app
app = Flask(__name__)
# Set the secret key for the Flask app
app.secret_key = "secret"  # Replace with a strong, unique key

# Register Blueprints
app.register_blueprint(payment_bp, url_prefix='/payment')
app.register_blueprint(admin_bp, url_prefix='/admin/payments')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/')
def admin():
    return render_template('admin_panel.html')

if __name__ == '__main__':
    app.run(debug=True)