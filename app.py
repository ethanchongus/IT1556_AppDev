from flask import Flask, render_template

# Initialize the Flask app
app = Flask(__name__)

# Set the secret key for the Flask app
app.secret_key = "secret"  # Replace with a strong, unique key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/')
def admin():
    return render_template('admin_panel.html')

if __name__ == '__main__':
    app.run(debug=True)