from flask import Blueprint, render_template, request, redirect, url_for, flash
import shelve

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

@payment_bp.route('/', methods=['GET', 'POST'])
def customer_payment():
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
            return render_template('customer_payment.html', errors=errors, form_data=request.form)

        # Save valid data to the database
        with shelve.open('payments.db', writeback=True) as db:
            payments = db.get('payments', [])
            payment_id = len(payments) + 1
            payments.append({
                'id': payment_id,
                'card_number': card_number,
                'expiry_date': expiry_date,
                'cvv': cvv,
                'name': name,
                'email': email
            })
            db['payments'] = payments  # Save updated list

        flash("Payment successfully submitted!")
        return redirect(url_for('payment.customer_payment'))

    return render_template('customer_payment.html', errors=errors, form_data=form_data)