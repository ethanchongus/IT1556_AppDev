from flask import Blueprint, session, request, render_template, redirect, url_for, send_file
from reportlab.pdfgen import canvas
from io import BytesIO
import uuid

transaction_bp = Blueprint('transaction', __name__)

# Route to display the transaction page
@transaction_bp.route('/')
def transaction():
    cart = session.get('cart', [])
    return render_template('customer_transaction.html', cart=cart)

# Route to process the transaction
@transaction_bp.route('/process', methods=['POST'])
def process_transaction():
    cart = session.get('cart', [])
    cardholder_name = request.form.get('cardholder_name')
    card_number = request.form.get('card_number')
    expiration_date = request.form.get('expiration_date')
    cvv = request.form.get('cvv')

    invoice_id = str(uuid.uuid4())[:8]

    session['transaction'] = {
        "cart": cart,
        "cardholder_name": cardholder_name,
        "card_number": card_number,
        "expiration_date": expiration_date,
        "cvv": cvv,
        "invoice_id": invoice_id,
    }

    return redirect(url_for('transaction.order_confirmation'))

# Route to display order confirmation
@transaction_bp.route('/order-confirmation', methods=['GET'])
def order_confirmation():
    transaction = session.get('transaction', {})
    return render_template('customer_order_confirmation.html', transaction=transaction)

# Route to download invoice
@transaction_bp.route('/invoice/download', methods=['GET'])
def download_invoice():
    transaction = session.get('transaction', {})

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    pdf.drawString(100, 750, "Invoice ID: " + transaction.get('invoice_id', ''))
    pdf.drawString(100, 730, "Cardholder Name: " + transaction.get('cardholder_name', ''))
    pdf.drawString(100, 710, "Items:")

    y = 690
    for item in transaction.get('cart', []):
        pdf.drawString(120, y, f"- {item['activity_name']} ({item['destination']}) - SGD {item['price']}")
        y -= 20

    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="invoice.pdf", mimetype='application/pdf')