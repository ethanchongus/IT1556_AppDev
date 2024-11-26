from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Create a secret key for the app
app.config['SECRET_KEY'] = 'my_secret_key'

# Create a directory to store the transaction data
transaction_dir = 'transactions'
if not os.path.exists(transaction_dir):
    os.makedirs(transaction_dir)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/transaction', methods=['POST'])
def handle_transaction():
    data = request.get_json()
    card_number = data['cardNumber']
    name = data['name']
    cvv = data['cvv']
    expiry_date = data['expiryDate']

    # Process the transaction data here
    print(f"Card Number: {card_number}")
    print(f"Name: {name}")
    print(f"CVV: {cvv}")
    print(f"Expiry Date: {expiry_date}")

    # Save the transaction data to a file
    with open('transaction_details.txt', 'a') as f:
        f.write(f"Card Number: {card_number}\n")
        f.write(f"Name: {name}\n")
        f.write(f"CVV: {cvv}\n")
        f.write(f"Expiry Date: {expiry_date}\n\n")

    # Save the transaction data to a file in the transactions directory
    transaction_file = os.path.join(transaction_dir, f"{card_number}.txt")
    with open(transaction_file, 'w') as f:
        f.write(f"Card Number: {card_number}\n")
        f.write(f"Name: {name}\n")
        f.write(f"CVV: {cvv}\n")
        f.write(f"Expiry Date: {expiry_date}\n")

    return jsonify({'message': 'Transaction successful'})

if __name__ == '__main__':
    app.run(debug=True)

    ## This good?