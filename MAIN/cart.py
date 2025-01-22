from flask import Blueprint, request, session, render_template, redirect, url_for, flash

cart_bp = Blueprint('cart', __name__)

# Route to view the cart
@cart_bp.route('/')
def view_cart():
    cart = session.get('cart', [])
    return render_template('customer_cart.html', cart=cart)

# Route to add an item to the cart
@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    activity_name = request.form.get('activity_name')
    price = float(request.form.get('price'))
    destination = request.form.get('destination')

    item = {
        "activity_name": activity_name,
        "price": price,
        "destination": destination,
    }

    # Add item to the session cart
    cart = session.get('cart', [])
    cart.append(item)
    session['cart'] = cart

    flash(f"{activity_name} added to your cart!", "success")
    return redirect(url_for('activities'))