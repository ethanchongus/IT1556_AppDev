from flask import Blueprint, render_template, request, redirect, url_for, flash
import shelve

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

# Retrieve activities from the database
def get_activities():
    with shelve.open('activities.db') as db:
        return db.get('activities', [])

@payment_bp.route('/checkout', methods=['GET', 'POST'])
def customer_checkout():
    activities = get_activities()
    with shelve.open('cart.db', writeback=True) as db:
        cart = db.get('cart', [])
        if request.method == 'POST':
            activity_id = int(request.form['activity_id'])
            selected_activity = next((a for a in activities if a['id'] == activity_id), None)
            if selected_activity:
                cart.append(selected_activity)
                db['cart'] = cart
                flash(f"Added {selected_activity['name']} to cart!", "success")
        total_price = sum(item['price'] for item in cart)
    return render_template('customer/customer_checkout.html', activities=activities, cart=cart, total_price=total_price)

@payment_bp.route('/checkout/remove/<int:activity_id>', methods=['POST'])
def remove_from_cart(activity_id):
    with shelve.open('cart.db', writeback=True) as db:
        cart = db.get('cart', [])
        cart = [item for item in cart if item['id'] != activity_id]
        db['cart'] = cart
    flash("Activity removed from cart.", "info")
    return redirect(url_for('payment.customer_checkout'))

@payment_bp.route('/', methods=['GET', 'POST'])
def customer_payment():
    with shelve.open('cart.db') as db:
        cart = db.get('cart', [])
        total_price = sum(item['price'] for item in cart)

    errors = {}
    form_data = request.form if request.method == 'POST' else None

    if request.method == 'POST':
        card_number = request.form.get('card_number', '').replace(' ', '')
        expiry_date = request.form.get('expiry_date', '')
        cvv = request.form.get('cvv', '')
        name = request.form.get('name', '')
        email = request.form.get('email', '')

        if len(card_number) != 16 or not card_number.isdigit():
            errors['card_number'] = "Card number must be exactly 16 digits."
        if not expiry_date or len(expiry_date) != 5 or not expiry_date[:2].isdigit() or not expiry_date[3:].isdigit() or expiry_date[2] != '/':
            errors['expiry_date'] = "Expiration date must be in MM/YY format."
        if len(cvv) != 3 or not cvv.isdigit():
            errors['cvv'] = "CVV must be exactly 3 digits."
        if not name or len(name) < 2:
            errors['name'] = "Name must be at least 2 characters long."
        if '@' not in email or '.' not in email:
            errors['email'] = "Enter a valid email address."

        if errors:
            return render_template('customer/customer_payment.html', errors=errors, form_data=request.form, cart=cart, total_price=total_price)

        with shelve.open('payments.db', writeback=True) as payments_db:
            payments = payments_db.get('payments', [])
            payment_id = len(payments) + 1
            payments.append({
                'id': payment_id,
                'cart': cart,
                'total': total_price,
                'name': name,
                'email': email,
            })
            payments_db['payments'] = payments

        with shelve.open('cart.db', writeback=True) as db:
            db['cart'] = []

        flash("Payment successfully submitted!")
        return redirect(url_for('payment.invoice', payment_id=payment_id))

    return render_template('customer/customer_payment.html', errors=errors, form_data=form_data, cart=cart, total_price=total_price)

@payment_bp.route('/invoice/<int:payment_id>')
def invoice(payment_id):
    with shelve.open('payments.db') as db:
        payments = db.get('payments', [])
        payment = next((p for p in payments if p['id'] == payment_id), None)

        if not payment:
            flash("Invoice not found.")
            return redirect(url_for('payment.customer_payment'))

    return render_template('customer/customer_invoice.html', payment=payment)