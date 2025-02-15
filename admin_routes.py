from flask import Blueprint, render_template, request, redirect, url_for, flash
import shelve

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

class PaymentManager:
    def __init__(self, db_path="database/payments.db"):
        """Initialize with database path."""
        self.db_path = db_path

    def get_all_payments(self):
        """Retrieve all payments from the database."""
        with shelve.open(self.db_path) as db:
            payments = db.get('payments', [])

        for payment in payments:
            payment['activities'] = payment.get('activities', [])  # Ensure activities exist

        return payments

    def get_payment_by_id(self, payment_id):
        """Retrieve a specific payment by ID."""
        with shelve.open(self.db_path, writeback=True) as db:
            payments = db.get('payments', [])
            return next((p for p in payments if p['id'] == payment_id), None)

    def update_payment(self, payment_id, updated_data):
        """Update a payment's details."""
        with shelve.open(self.db_path, writeback=True) as db:
            payments = db.get('payments', [])
            for i, payment in enumerate(payments):
                if payment['id'] == payment_id:
                    payments[i].update(updated_data)
                    db['payments'] = payments  # Save changes
                    return True
        return False

    def delete_payment(self, payment_id):
        """Delete a payment and archive it."""
        with shelve.open(self.db_path, writeback=True) as db:
            payments = db.get('payments', [])
            archived_payments = db.get('archived_payments', [])

            deleted_payment = next((p for p in payments if p['id'] == payment_id), None)
            if deleted_payment:
                archived_payments.append(deleted_payment)
                db['archived_payments'] = archived_payments  # Store archived payments

                payments = [p for p in payments if p['id'] != payment_id]
                db['payments'] = payments  # Save changes

                return True
        return False

payment_manager = PaymentManager()

@admin_bp.route('/', methods=['GET'])
def admin_payments():
    """Display all payments in the admin panel."""
    payments = payment_manager.get_all_payments()
    return render_template('admin/admin_payments.html', payments=payments)

@admin_bp.route('/edit/<int:payment_id>', methods=['GET', 'POST'])
def edit_payment(payment_id):
    """Edit a payment's details."""
    errors = {}  # Initialize errors
    payment = payment_manager.get_payment_by_id(payment_id)

    if not payment:
        flash("Payment record not found.")
        return redirect(url_for('admin.admin_payments'))

    if request.method == 'POST':
        updated_payment = {
            'id': payment_id,
            'card_number': request.form.get('card_number', '').replace(' ', ''),
            'expiry_date': request.form.get('expiry_date', ''),
            'cvv': request.form.get('cvv', ''),
            'name': request.form.get('name', ''),
            'email': request.form.get('email', ''),
            'activities': payment.get('activities', []),  # Keep activities
            'total': payment.get('total', 0)  # Keep total price
        }

        # Validate inputs
        if len(updated_payment['card_number']) != 16 or not updated_payment['card_number'].isdigit():
            errors['card_number'] = "Card number must be exactly 16 digits."
        if (not updated_payment['expiry_date'] or len(updated_payment['expiry_date']) != 5 or 
            not updated_payment['expiry_date'][:2].isdigit() or not updated_payment['expiry_date'][3:].isdigit() or 
            updated_payment['expiry_date'][2] != '/'):
            errors['expiry_date'] = "Expiration date must be in MM/YY format."
        if len(updated_payment['cvv']) != 3 or not updated_payment['cvv'].isdigit():
            errors['cvv'] = "CVV must be exactly 3 digits."
        if not updated_payment['name'] or len(updated_payment['name']) < 2:
            errors['name'] = "Name must be at least 2 characters long."
        if '@' not in updated_payment['email'] or '.' not in updated_payment['email']:
            errors['email'] = "Enter a valid email address."

        # If errors exist, re-render the form
        if errors:
            return render_template('customer/customer_payment.html', errors=errors, form_data=updated_payment, editing=True)

        # Update payment in database
        if payment_manager.update_payment(payment_id, updated_payment):
            flash("Payment details updated successfully!")
        else:
            flash("Failed to update payment details.", "danger")

        return redirect(url_for('admin.admin_payments'))

    # Render the edit form
    return render_template('customer/customer_payment.html', errors=errors, form_data=payment, editing=True)

@admin_bp.route('/delete/<int:payment_id>')
def delete_payment(payment_id):
    """Delete a payment and archive it."""
    if payment_manager.delete_payment(payment_id):
        flash("Payment deleted successfully!")
    else:
        flash("Failed to delete payment.", "danger")

    return redirect(url_for('admin.admin_payments'))