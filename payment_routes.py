from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import shelve
import uuid
from typing import List, Dict, Optional

class CartItem:
    def __init__(self, activity_id: str, name: str, price: float, departure_date: str, seats: int):
        self.id = str(uuid.uuid4())
        self.activity_id = activity_id
        self.name = name
        self.price = price * seats
        self.departure_date = departure_date
        self.seats = seats

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'activity_id': self.activity_id,
            'name': self.name,
            'price': self.price,
            'departure_date': self.departure_date,
            'seats': self.seats
        }

class Cart:
    def __init__(self, session):
        self.session = session
        self.items: List[CartItem] = []
        self._load_cart()

    def _load_cart(self):
        cart_data = self.session.get('cart', [])
        self.items = [CartItem(**item) for item in cart_data]

    def save(self):
        self.session['cart'] = [item.to_dict() for item in self.items]

    def add_item(self, activity_id: str, name: str, price: float, departure_date: str, seats: int):
        item = CartItem(activity_id, name, price, departure_date, seats)
        self.items.append(item)
        self.save()
        return item

    def remove_item(self, cart_id: str):
        self.items = [item for item in self.items if item.id != cart_id]
        self.save()

    def clear(self):
        self.items = []
        self.session.pop('cart', None)

    def get_total(self) -> float:
        return sum(item.price for item in self.items)

    def is_empty(self) -> bool:
        return len(self.items) == 0

class Payment:
    def __init__(self, name: str, email: str, card_number: str, expiry_date: str, cvv: str, cart_items: List[CartItem], total: float):
        self.id = str(uuid.uuid4())
        self.name = name
        self.email = email
        self.card_number = card_number[-4:]  # Store only last 4 digits
        self.expiry_date = expiry_date
        self.cvv = "***"  # Mask CVV
        self.activities = [item.to_dict() for item in cart_items]
        self.total = total

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'card_number': self.card_number,
            'expiry_date': self.expiry_date,
            'cvv': self.cvv,
            'activities': self.activities,
            'total': self.total
        }

class PaymentManager:
    def __init__(self, db_path: str = "database/payments.db"):
        self.db_path = db_path

    def save_payment(self, payment: Payment) -> str:
        with shelve.open(self.db_path, writeback=True) as db:
            payments = db.get('payments', [])
            payment_dict = payment.to_dict()
            payments.append(payment_dict)
            db['payments'] = payments
        return payment.id

    def get_payment(self, payment_id: str) -> Optional[Dict]:
        with shelve.open(self.db_path) as db:
            payments = db.get('payments', [])
            return next((p for p in payments if p['id'] == payment_id), None)

    def get_all_payments(self) -> List[Dict]:
        with shelve.open(self.db_path) as db:
            return db.get('payments', [])

class PaymentValidator:
    @staticmethod
    def validate_payment_data(data: Dict) -> Dict[str, str]:
        errors = {}
        
        if len(data['card_number']) != 16 or not data['card_number'].isdigit():
            errors['card_number'] = "Card number must be 16 digits."
        
        if not data['expiry_date'] or len(data['expiry_date']) != 5 or not data['expiry_date'][:2].isdigit() or data['expiry_date'][2] != '/':
            errors['expiry_date'] = "Expiration date must be MM/YY."
        
        if len(data['cvv']) != 3 or not data['cvv'].isdigit():
            errors['cvv'] = "CVV must be 3 digits."
        
        if not data['name'].replace(" ", "").isalpha() or len(data['name']) < 2:
            errors['name'] = "Name must only contain letters and be at least 2 characters long."
        
        if '@' not in data['email'] or '.' not in data['email']:
            errors['email'] = "Enter a valid email."
        
        return errors

# Blueprint setup
payment_bp = Blueprint('payment', __name__, url_prefix='/payment')
payment_manager = PaymentManager()

@payment_bp.route('/add_to_cart/<activity_id>', methods=['POST'])
def add_to_cart(activity_id):
    cart = Cart(session)
    
    item = cart.add_item(
        activity_id=activity_id,
        name=request.form.get('activity_name'),
        price=float(request.form.get('price')),
        departure_date=request.form.get('departure_date'),
        seats=int(request.form.get('seats'))
    )
    
    flash(f"{item.name} added to cart.")
    return redirect(url_for('payment.view_cart'))

@payment_bp.route('/cart')
def view_cart():
    cart = Cart(session)
    return render_template('customer/customer_cart.html', 
                         cart=cart.items, 
                         total_price=cart.get_total())

@payment_bp.route('/remove_from_cart/<cart_id>')
def remove_from_cart(cart_id):
    cart = Cart(session)
    cart.remove_item(cart_id)
    flash("Item removed from cart.")
    return redirect(url_for('payment.view_cart'))

@payment_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = Cart(session)
    
    if cart.is_empty():
        flash("Your cart is empty!")
        return redirect(url_for('payment.view_cart'))

    if request.method == 'POST':
        return redirect(url_for('payment.customer_payment'))

    return render_template('customer/checkout.html', 
                         cart=cart.items, 
                         total_price=cart.get_total())

@payment_bp.route('/customer_payment', methods=['GET', 'POST'])
def customer_payment():
    cart = Cart(session)
    
    if request.method == 'POST':
        payment_data = {
            'card_number': request.form.get('card_number', '').replace(' ', ''),
            'expiry_date': request.form.get('expiry_date', ''),
            'cvv': request.form.get('cvv', ''),
            'name': request.form.get('name', ''),
            'email': request.form.get('email', '')
        }
        
        errors = PaymentValidator.validate_payment_data(payment_data)
        
        if errors:
            return render_template('customer/customer_payment.html', 
                                errors=errors, 
                                cart=cart.items, 
                                total_price=cart.get_total())

        payment = Payment(
            name=payment_data['name'],
            email=payment_data['email'],
            card_number=payment_data['card_number'],
            expiry_date=payment_data['expiry_date'],
            cvv=payment_data['cvv'],
            cart_items=cart.items,
            total=cart.get_total()
        )
        
        payment_id = payment_manager.save_payment(payment)
        cart.clear()
        
        return redirect(url_for('payment.invoice', payment_id=payment_id))

    return render_template('customer/customer_payment.html', 
                         cart=cart.items, 
                         total_price=cart.get_total())

@payment_bp.route('/invoice/<payment_id>')
def invoice(payment_id):
    payment = payment_manager.get_payment(payment_id)
    
    if not payment:
        flash("Invoice not found.")
        return redirect(url_for('payment.view_cart'))

    return render_template('customer/customer_invoice.html', payment=payment)

@payment_bp.route('/my_bookings')
def my_bookings():
    payments = payment_manager.get_all_payments()
    return render_template('customer/my_bookings.html', payments=payments)

@payment_bp.route('/')
def payment_redirect():
    return redirect(url_for('payment.customer_payment'))