from flask import Blueprint, render_template, request, redirect, url_for, flash
import shelve

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/', methods=['GET'])
def admin_payments():
    with shelve.open('database/payments.db') as db:
        payments = db.get('payments', [])

    for payment in payments:
        payment['activities'] = payment.get('activities', [])  # Ensure activities exist

    return render_template('admin/admin_payments.html', payments=payments)


@admin_bp.route('/edit/<int:payment_id>', methods=['GET', 'POST'])
def edit_payment(payment_id):
    errors = {}  # Initialize errors

    with shelve.open('database/payments.db', writeback=True) as db:
        payments = db.get('payments', [])
        payment = next((p for p in payments if p['id'] == payment_id), None)

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
            if len(payment['card_number']) != 16 or not payment['card_number'].isdigit():
                errors['card_number'] = "Card number must be exactly 16 digits."
            if not payment['expiry_date'] or len(payment['expiry_date']) != 5 or not payment['expiry_date'][:2].isdigit() or not payment['expiry_date'][3:].isdigit() or payment['expiry_date'][2] != '/':
                errors['expiry_date'] = "Expiration date must be in MM/YY format."
            if len(payment['cvv']) != 3 or not payment['cvv'].isdigit():
                errors['cvv'] = "CVV must be exactly 3 digits."
            if not payment['name'] or len(payment['name']) < 2:
                errors['name'] = "Name must be at least 2 characters long."
            if '@' not in payment['email'] or '.' not in payment['email']:
                errors['email'] = "Enter a valid email address."

            # If errors exist, re-render the form
            if errors:
                return render_template('customer/customer_payment.html', errors=errors, form_data=payment, editing=True)

            # Save changes to the database
            db['payments'] = payments  # Update shelve with modified data
            flash("Payment details updated successfully!")
            return redirect(url_for('admin.admin_payments'))

    # Render the edit form
    return render_template('customer/customer_payment.html', errors=errors, form_data=payment, editing=True)


@admin_bp.route('/delete/<int:payment_id>')
def delete_payment(payment_id):
    with shelve.open('database/payments.db', writeback=True) as db:
        payments = db.get('payments', [])
        archived_payments = db.get('archived_payments', [])
        
        deleted_payment = next((p for p in payments if p['id'] == payment_id), None)
        if deleted_payment:
            archived_payments.append(deleted_payment)
            db['archived_payments'] = archived_payments
        
        payments = [p for p in payments if p['id'] != payment_id]
        db['payments'] = payments

    flash("Payment deleted successfully!")
    return redirect(url_for('admin.admin_payments'))
