from flask import Flask, request, jsonify, render_template, redirect, url_for
import shelve

app = Flask(__name__)

# Helper function to generate unique IDs
def get_next_id(db):
    if 'counter' not in db:
        db['counter'] = 1
    else:
        db['counter'] += 1
    return db['counter']

@app.route('/')
def customer_page():
    return render_template('customer.html')

@app.route('/admin')
def admin_page():
    with shelve.open('transactions.db') as db:
        transactions = [
            {'id': key, **db[key]} for key in db if key != 'counter'
        ]
    return render_template('admin.html', transactions=transactions)

# Create a transaction (Customer functionality)
@app.route('/transaction', methods=['POST'])
def create_transaction():
    data = request.form
    with shelve.open('transactions.db') as db:
        transaction_id = str(get_next_id(db))
        db[transaction_id] = {
            'card_number': data['card_number'],
            'name': data['name'],
            'cvv': data['cvv'],
            'expiry_date': data['expiry_date'],
            'email': data['email']
        }
    return redirect(url_for('customer_page'))

# Read a specific transaction (Admin functionality)
@app.route('/transaction/<id>', methods=['GET'])
def read_transaction(id):
    with shelve.open('transactions.db') as db:
        if id in db:
            transaction = db[id]
            return jsonify({'id': id, **transaction})
        else:
            return jsonify({'error': 'Transaction not found'}), 404

# Update a transaction (Admin functionality)
@app.route('/transaction/<id>', methods=['POST'])
def update_transaction(id):
    data = request.form
    with shelve.open('transactions.db') as db:
        if id in db:
            db[id] = {
                'card_number': data['card_number'],
                'name': data['name'],
                'cvv': data['cvv'],
                'expiry_date': data['expiry_date'],
                'email': data['email']
            }
    return redirect(url_for('admin_page'))

# Delete a transaction (Admin functionality)
@app.route('/transaction/<id>', methods=['DELETE'])
def delete_transaction(id):
    with shelve.open('transactions.db') as db:
        if id in db:
            del db[id]
            return jsonify({'message': 'Transaction deleted successfully'})
        else:
            return jsonify({'error': 'Transaction not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)