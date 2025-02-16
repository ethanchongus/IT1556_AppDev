from flask import Blueprint, render_template, request, redirect, url_for, flash
from typing import Dict, List, Optional, Union
import shelve

class AdminPayment:
    def __init__(self, payment_data: Dict):
        self.id = payment_data['id']
        self.name = payment_data['name']
        self.email = payment_data['email']
        self.card_number = payment_data['card_number']
        self.expiry_date = payment_data['expiry_date']
        self.cvv = payment_data['cvv']
        self.activities = payment_data.get('activities', [])
        self.total = payment_data.get('total', 0)

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

    def update(self, updated_data: Dict) -> None:
        """Update payment attributes with new data."""
        self.name = updated_data.get('name', self.name)
        self.email = updated_data.get('email', self.email)
        self.card_number = updated_data.get('card_number', self.card_number)
        self.expiry_date = updated_data.get('expiry_date', self.expiry_date)
        self.cvv = updated_data.get('cvv', self.cvv)

class AdminPaymentManager:
    def __init__(self, db_path: str = "database/payments.db"):
        self.db_path = db_path

    def get_all_payments(self) -> List[AdminPayment]:
        """Retrieve all payments from the database."""
        with shelve.open(self.db_path) as db:
            payments = db.get('payments', [])
            return [AdminPayment(payment) for payment in payments]

    def get_payment_by_id(self, payment_id: str) -> Optional[AdminPayment]:
        """Retrieve a specific payment by ID."""
        with shelve.open(self.db_path) as db:
            payments = db.get('payments', [])
            payment_data = next((p for p in payments if p['id'] == payment_id), None)
            return AdminPayment(payment_data) if payment_data else None

    def update_payment(self, payment_id: str, updated_data: Dict) -> bool:
        """Update a payment's details."""
        with shelve.open(self.db_path, writeback=True) as db:
            payments = db.get('payments', [])
            for i, payment in enumerate(payments):
                if payment['id'] == payment_id:
                    # Only update name and email
                    payments[i].update({
                        'name': updated_data['name'],
                        'email': updated_data['email']
                    })
                    db['payments'] = payments
                    return True
        return False

    def delete_payment(self, payment_id: str) -> bool:
        """Delete a payment and archive it."""
        with shelve.open(self.db_path, writeback=True) as db:
            payments = db.get('payments', [])
            archived_payments = db.get('archived_payments', [])

            payment_to_archive = next((p for p in payments if p['id'] == payment_id), None)
            if payment_to_archive:
                archived_payments.append(payment_to_archive)
                db['archived_payments'] = archived_payments

                payments = [p for p in payments if p['id'] != payment_id]
                db['payments'] = payments
                return True
        return False

class AdminPaymentValidator:
    @staticmethod
    def validate_payment_update(data: Dict) -> Dict[str, str]:
        """Validate payment update data."""
        errors = {}

        # Card number validation
        card_number = data.get('card_number', '').replace(' ', '')
        if len(card_number) != 16 or not card_number.isdigit():
            errors['card_number'] = "Card number must be exactly 16 digits."

        # Expiry date validation
        expiry_date = data.get('expiry_date', '')
        if (not expiry_date or len(expiry_date) != 5 or 
            not expiry_date[:2].isdigit() or not expiry_date[3:].isdigit() or 
            expiry_date[2] != '/'):
            errors['expiry_date'] = "Expiration date must be in MM/YY format."

        # CVV validation
        cvv = data.get('cvv', '')
        if len(cvv) != 3 or not cvv.isdigit():
            errors['cvv'] = "CVV must be exactly 3 digits."

        # Name validation
        name = data.get('name', '')
        if not name or len(name) < 2:
            errors['name'] = "Name must be at least 2 characters long."

        # Email validation
        email = data.get('email', '')
        if '@' not in email or '.' not in email:
            errors['email'] = "Enter a valid email address."

        return errors

# Blueprint setup
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
admin_payment_manager = AdminPaymentManager()

@admin_bp.route('/', methods=['GET'])
def admin_payments():
    """Display all payments in the admin panel."""
    payments = admin_payment_manager.get_all_payments()
    return render_template('admin/admin_payments.html', 
                         payments=[payment.to_dict() for payment in payments])

@admin_bp.route('/edit/<payment_id>', methods=['GET', 'POST'])
def edit_payment(payment_id: str):
    """Edit a payment's details."""
    payment = admin_payment_manager.get_payment_by_id(payment_id)

    if not payment:
        flash("Payment record not found.")
        return redirect(url_for('admin.admin_payments'))

    if request.method == 'POST':
        updated_data = {
            'name': request.form.get('name', ''),
            'email': request.form.get('email', '')
        }

        # Validate only name and email
        errors = {}
        
        # Name validation
        if not updated_data['name'] or len(updated_data['name']) < 2:
            errors['name'] = "Name must be at least 2 characters long."
        
        # Email validation
        if '@' not in updated_data['email'] or '.' not in updated_data['email']:
            errors['email'] = "Enter a valid email address."

        if errors:
            return render_template('customer/customer_payment.html', 
                                errors=errors, 
                                form_data=payment.to_dict(), 
                                editing=True,
                                payment_id=payment_id)

        # Update payment in database
        if admin_payment_manager.update_payment(payment_id, updated_data):
            flash("Payment details updated successfully!")
        else:
            flash("Failed to update payment details.", "danger")

        return redirect(url_for('admin.admin_payments'))

    # Render the edit form
    return render_template('customer/customer_payment.html', 
                         errors={}, 
                         form_data=payment.to_dict(), 
                         editing=True,
                         payment_id=payment_id)

@admin_bp.route('/delete/<payment_id>')
def delete_payment(payment_id: str):
    """Delete a payment and archive it."""
    if admin_payment_manager.delete_payment(payment_id):
        flash("Payment deleted successfully!")
    else:
        flash("Failed to delete payment.", "danger")

    return redirect(url_for('admin.admin_payments'))