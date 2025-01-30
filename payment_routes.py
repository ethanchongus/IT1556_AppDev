from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import shelve
import uuid

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

# Ensure session cart exists
def get_cart():
    return session.get('cart', [])

def save_cart(cart):
    session['cart'] = cart

# Route for adding activity to cart
@payment_bp.route('/add_to_cart/<activity_id>', methods=['POST'])
def add_to_cart(activity_id):
    activity_name = request.form.get('activity_name')
    price = float(request.form.get('price'))
    departure_date = request.form.get('departure_date')
    seats = int(request.form.get('seats'))

    cart = get_cart()
    cart.append({
        'id': str(uuid.uuid4()),  # Generate unique ID
        'activity_id': activity_id,
        'name': activity_name,
        'price': price * seats,  # Multiply by number of seats
        'departure_date': departure_date,
        'seats': seats
    })
    save_cart(cart)

    flash(f"{activity_name} added to cart.")
    return redirect(url_for('payment.view_cart'))

# Route to view cart
@payment_bp.route('/cart')
def view_cart():
    cart = get_cart()
    total_price = sum(item['price'] for item in cart)
    return render_template('customer/cart.html', cart=cart, total_price=total_price)

# Route to remove from cart
@payment_bp.route('/remove_from_cart/<cart_id>')
def remove_from_cart(cart_id):
    cart = get_cart()
    cart = [item for item in cart if item['id'] != cart_id]
    save_cart(cart)
    return redirect(url_for('payment.view_cart'))

# Checkout page
@payment_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = get_cart()
    total_price = sum(item['price'] for item in cart)

    if not cart:
        flash("Your cart is empty!")
        return redirect(url_for('payment.view_cart'))

    if request.method == 'POST':
        return redirect(url_for('payment.customer_payment'))

    return render_template('customer/checkout.html', cart=cart, total_price=total_price)

# Payment page
@payment_bp.route('/payment', methods=['GET', 'POST'])
def customer_payment():
    cart = get_cart()
    total_price = sum(item['price'] for item in cart)
    
    if not cart:
        flash("No activities selected!")
        return redirect(url_for('payment.view_cart'))

    errors = {}

    if request.method == 'POST':
        card_number = request.form.get('card_number', '').replace(' ', '')
        expiry_date = request.form.get('expiry_date', '')
        cvv = request.form.get('cvv', '')
        name = request.form.get('name', '')
        email = request.form.get('email', '')

        # Validate inputs
        if len(card_number) != 16 or not card_number.isdigit():
            errors['card_number'] = "Card number must be 16 digits."
        if not expiry_date or len(expiry_date) != 5 or not expiry_date[:2].isdigit() or expiry_date[2] != '/':
            errors['expiry_date'] = "Expiration date must be MM/YY."
        if len(cvv) != 3 or not cvv.isdigit():
            errors['cvv'] = "CVV must be 3 digits."
        if len(name) < 2:
            errors['name'] = "Name must be at least 2 characters."
        if '@' not in email or '.' not in email:
            errors['email'] = "Enter a valid email."

        if errors:
            return render_template('customer/customer_payment.html', errors=errors, cart=cart, total_price=total_price)

        # Save to database
        with shelve.open('payments.db', writeback=True) as db:
            payments = db.get('payments', [])
            payment_id = str(uuid.uuid4())
            payments.append({
                'id': payment_id,
                'name': name,
                'email': email,
                'activities': cart,
                'total': total_price
            })
            db['payments'] = payments
            session.pop('cart', None)  # Clear cart after payment

        return redirect(url_for('payment.invoice', payment_id=payment_id))

    return render_template('customer/customer_payment.html', cart=cart, total_price=total_price)

# Invoice
@payment_bp.route('/invoice/<payment_id>')
def invoice(payment_id):
    with shelve.open('payments.db') as db:
        payments = db.get('payments', [])
        payment = next((p for p in payments if p['id'] == payment_id), None)

        if not payment:
            flash("Invoice not found.")
            return redirect(url_for('payment.view_cart'))

    return render_template('customer/invoice.html', payment=payment)

# My Bookings
@payment_bp.route('/my_bookings')
def my_bookings():
    with shelve.open('payments.db') as db:
        payments = db.get('payments', [])
    return render_template('customer/my_bookings.html', payments=payments)