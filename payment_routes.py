from flask import Blueprint, render_template, request, redirect, url_for, flash
import shelve
import os

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

# Initialize shelve safely
def initialize_shelve(db_name):
    """Safely initialize the shelve database."""
    if not os.path.exists(db_name):
        with shelve.open(db_name) as db:
            db['payments'] = []  # Initialize with an empty list

initialize_shelve('payments.db')

# Dummy activity data for demonstration
dummy_activities = [
    {"id": 1, "name": "Rainforest Hike", "location": "Eco Park", "price": 100, "quantity": 1},
    {"id": 2, "name": "Mountain Trek", "location": "Mountain Base", "price": 120, "quantity": 1},
]

cart = []

@payment_bp.route('/cart', methods=['GET', 'POST'])
def cart_page():
    global cart

    if request.method == 'POST':
        # Add activity to cart
        activity_id = int(request.form.get('activity_id'))
        quantity = int(request.form.get('quantity', 1))
        activity = next((a for a in dummy_activities if a['id'] == activity_id), None)

        if activity:
            activity_in_cart = next((c for c in cart if c['id'] == activity_id), None)
            if activity_in_cart:
                activity_in_cart['quantity'] += quantity
            else:
                cart.append({**activity, "quantity": quantity})

        return redirect(url_for('payment.cart_page'))

    return render_template('customer/customer_cart.html', cart=cart)

@payment_bp.route('/checkout', methods=['GET', 'POST'])
def customer_checkout():
    global cart

    if not cart:
        flash("Your cart is empty!", "warning")
        return redirect(url_for('payment.cart_page'))

    if request.method == 'POST':
        return redirect(url_for('payment.customer_payment'))

    return render_template('customer/customer_checkout.html', cart=cart)

@payment_bp.route('/', methods=['GET', 'POST'])
def customer_payment():
    global cart
    errors = {}  # Initialize errors
    form_data = request.form if request.method == 'POST' else None

    if request.method == 'POST':
        # Process form inputs
        card_number = request.form.get('card_number', '').replace(' ', '')  # Remove spaces
        expiry_date = request.form.get('expiry_date', '')
        cvv = request.form.get('cvv', '')
        name = request.form.get('name', '')
        email = request.form.get('email', '')

        # Validate Card Number (16 digits)
        if len(card_number) != 16 or not card_number.isdigit():
            errors['card_number'] = "Card number must be exactly 16 digits."

        # Validate Expiry Date (MM/YY format)
        if not expiry_date or len(expiry_date) != 5 or not expiry_date[:2].isdigit() or not expiry_date[3:].isdigit() or expiry_date[2] != '/':
            errors['expiry_date'] = "Expiration date must be in MM/YY format."

        # Validate CVV (3 digits)
        if len(cvv) != 3 or not cvv.isdigit():
            errors['cvv'] = "CVV must be exactly 3 digits."

        # Validate Name (minimum 2 characters)
        if not name or len(name) < 2:
            errors['name'] = "Name must be at least 2 characters long."

        # Validate Email
        if '@' not in email or '.' not in email:
            errors['email'] = "Enter a valid email address."

        # If errors exist, re-render the form
        if errors:
            return render_template('customer/customer_payment.html', errors=errors, form_data=request.form, cart=cart)

        # Save valid data to the database
        try:
            with shelve.open('payments.db', writeback=True) as db:
                payments = db.get('payments', [])
                payment_id = len(payments) + 1
                total_price = sum(item['price'] * item['quantity'] for item in cart)
                payments.append({
                    'id': payment_id,
                    'card_number': card_number,
                    'expiry_date': expiry_date,
                    'cvv': cvv,
                    'name': name,
                    'email': email,
                    'cart': cart,
                    'total_price': total_price
                })
                db['payments'] = payments  # Save updated list

            cart = []  # Clear cart after payment
            flash("Payment successfully submitted!")
            return redirect(url_for('payment.invoice', payment_id=payment_id))
        except Exception as e:
            flash(f"Error saving payment: {str(e)}", "danger")
            return render_template('customer/customer_payment.html', errors={}, form_data=request.form, cart=cart)

    return render_template('customer/customer_payment.html', errors=errors, form_data=form_data, cart=cart)

@payment_bp.route('/invoice/<int:payment_id>')
def invoice(payment_id):
    with shelve.open('payments.db') as db:
        payments = db.get('payments', [])
        payment = next((p for p in payments if p['id'] == payment_id), None)

        if not payment:
            flash("Invoice not found.")
            return redirect(url_for('payment.customer_payment'))

    return render_template('customer/customer_invoice.html', payment=payment)