import shelve
from flask import Blueprint, render_template, request, redirect, url_for, flash

# Define a Blueprint for transaction-related routes
transaction_bp = Blueprint('transaction', __name__)

# Transaction class
class Transaction:
    def __init__(self, cardholder_name, card_number, expiration_date, cvv):
        self.cardholder_name = cardholder_name
        self.card_number = card_number
        self.expiration_date = expiration_date
        self.cvv = cvv

# Customer transaction page
@transaction_bp.route('/transaction/', methods=['GET', 'POST'])
def transaction():
    if request.method == 'POST':
        try:
            # Extract payment details from form submission
            cardholder_name = request.form.get('cardholder_name')
            card_number = request.form.get('card_number').replace(" ", "")  # Remove spaces
            expiration_date = request.form.get('expiration_date')
            cvv = request.form.get('cvv')

            # Validate inputs
            if not cardholder_name or not card_number or not expiration_date or not cvv:
                flash("All fields are required.", "danger")
                return render_template('customer_transaction.html')
            if not card_number.isdigit() or len(card_number) != 16:
                flash("Card number must be 16 digits.", "danger")
                return render_template('customer_transaction.html')
            if len(expiration_date) != 5 or expiration_date[2] != '/':
                flash("Expiration date must be in MM/YY format.", "danger")
                return render_template('customer_transaction.html')
            if not cvv.isdigit() or len(cvv) != 3:
                flash("CVV must be 3 digits.", "danger")
                return render_template('customer_transaction.html')

            # Create a Transaction object
            transaction = Transaction(cardholder_name, card_number, expiration_date, cvv)

            # Save the object to shelve
            with shelve.open('transactions.db', writeback=True) as db:
                if 'transactions' not in db:
                    db['transactions'] = []
                db['transactions'].append(transaction)

            flash("Payment submitted successfully.", "success")
            return redirect(url_for('transaction.transaction'))
        except Exception as e:
            print(f"Error: {e}")
            flash("An unexpected error occurred. Please try again later.", "danger")
            return render_template('customer_transaction.html')

    return render_template('customer_transaction.html')

# Admin transaction page
@transaction_bp.route('/admin/transaction/')
def admin_transaction():
    with shelve.open('transactions.db') as db:
        transactions = db.get('transactions', [])
    return render_template('admin_transaction.html', transactions=transactions)


# Update transaction details
@transaction_bp.route('/admin/transaction/update/<int:transaction_id>', methods=['POST'])
def update_transaction(transaction_id):
    try:
        with shelve.open('transactions.db', writeback=True) as db:
            transactions = db.get('transactions', [])
            if 0 <= transaction_id < len(transactions):
                transaction = transactions[transaction_id]

                # Extract updated data from the form
                transaction.cardholder_name = request.form.get('cardholder_name')
                transaction.card_number = request.form.get('card_number').replace(" ", "")
                transaction.expiration_date = request.form.get('expiration_date')
                transaction.cvv = request.form.get('cvv')

                # Validate inputs
                if not transaction.cardholder_name or not transaction.card_number or not transaction.expiration_date or not transaction.cvv:
                    flash("All fields are required.", "danger")
                    return redirect(url_for('transaction.admin_transaction'))
                if not transaction.card_number.isdigit() or len(transaction.card_number) != 16:
                    flash("Card number must be 16 digits.", "danger")
                    return redirect(url_for('transaction.admin_transaction'))
                if len(transaction.expiration_date) != 5 or transaction.expiration_date[2] != '/':
                    flash("Expiration date must be in MM/YY format.", "danger")
                    return redirect(url_for('transaction.admin_transaction'))
                if not transaction.cvv.isdigit() or len(transaction.cvv) != 3:
                    flash("CVV must be 3 digits.", "danger")
                    return redirect(url_for('transaction.admin_transaction'))

                db['transactions'] = transactions
                flash("Transaction updated successfully.", "success")
            else:
                flash("Transaction not found.", "danger")

    except Exception as e:
        print(f"Error during update: {e}")
        flash("An unexpected error occurred. Please try again.", "danger")

    return redirect(url_for('transaction.admin_transaction'))

# Delete transaction
@transaction_bp.route('/admin/transaction/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    try:
        with shelve.open('transactions.db', writeback=True) as db:
            transactions = db.get('transactions', [])
            if 0 <= transaction_id < len(transactions):
                transactions.pop(transaction_id)
                db['transactions'] = transactions
                flash("Transaction deleted successfully.", "success")
            else:
                flash("Transaction not found.", "danger")
    except Exception as e:
        print(f"Error during deletion: {e}")
        flash("An unexpected error occurred. Please try again.", "danger")

    return redirect(url_for('transaction.admin_transaction'))

@transaction_bp.app_template_filter('format_card_number')
def format_card_number(card_number):
    return ' '.join([card_number[i:i+4] for i in range(0, len(card_number), 4)])
