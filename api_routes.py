from flask import Blueprint, jsonify, request
from http import HTTPStatus
from typing import Dict, List, Optional
from datetime import datetime
import shelve
import uuid

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

class PaymentAPI:
    def __init__(self, db_path: str = "database/payments.db"):
        self.db_path = db_path

    def get_all_payments(self) -> List[Dict]:
        """Retrieve all payments from database."""
        with shelve.open(self.db_path) as db:
            return db.get('payments', [])

    def get_payment(self, payment_id: str) -> Optional[Dict]:
        """Retrieve specific payment by ID."""
        with shelve.open(self.db_path) as db:
            payments = db.get('payments', [])
            return next((p for p in payments if p['id'] == payment_id), None)

    def create_payment(self, payment_data: Dict) -> Dict:
        """Create new payment record."""
        with shelve.open(self.db_path, writeback=True) as db:
            payments = db.get('payments', [])
            
            # Generate new payment record
            new_payment = {
                'id': str(uuid.uuid4()),
                'name': payment_data['name'],
                'email': payment_data['email'],
                'card_number': payment_data['card_number'][-4:],  # Store only last 4 digits
                'expiry_date': payment_data['expiry_date'],
                'cvv': '***',  # Mask CVV
                'activities': payment_data.get('activities', []),
                'total': payment_data.get('total', 0),
                'created_at': datetime.now().isoformat()
            }
            
            payments.append(new_payment)
            db['payments'] = payments
            return new_payment

    def update_payment(self, payment_id: str, update_data: Dict) -> Optional[Dict]:
        """Update existing payment record."""
        with shelve.open(self.db_path, writeback=True) as db:
            payments = db.get('payments', [])
            for i, payment in enumerate(payments):
                if payment['id'] == payment_id:
                    # Only update allowed fields
                    payments[i].update({
                        'name': update_data.get('name', payment['name']),
                        'email': update_data.get('email', payment['email']),
                        'updated_at': datetime.now().isoformat()
                    })
                    db['payments'] = payments
                    return payments[i]
            return None

    def delete_payment(self, payment_id: str) -> bool:
        """Delete payment record."""
        with shelve.open(self.db_path, writeback=True) as db:
            payments = db.get('payments', [])
            initial_length = len(payments)
            payments = [p for p in payments if p['id'] != payment_id]
            
            if len(payments) < initial_length:
                db['payments'] = payments
                return True
            return False

# Initialize API
payment_api = PaymentAPI()

# API Routes
@api_bp.route('/payments', methods=['GET'])
def get_payments():
    """Get all payments."""
    payments = payment_api.get_all_payments()
    return jsonify({
        'status': 'success',
        'data': payments,
        'count': len(payments)
    }), HTTPStatus.OK

@api_bp.route('/payments/<payment_id>', methods=['GET'])
def get_payment(payment_id: str):
    """Get specific payment by ID."""
    payment = payment_api.get_payment(payment_id)
    if not payment:
        return jsonify({
            'status': 'error',
            'message': 'Payment not found'
        }), HTTPStatus.NOT_FOUND
    
    return jsonify({
        'status': 'success',
        'data': payment
    }), HTTPStatus.OK

@api_bp.route('/payments', methods=['POST'])
def create_payment():
    """Create new payment."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'email', 'card_number', 'expiry_date', 'cvv']
    if not all(field in data for field in required_fields):
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields',
            'required_fields': required_fields
        }), HTTPStatus.BAD_REQUEST
    
    new_payment = payment_api.create_payment(data)
    return jsonify({
        'status': 'success',
        'message': 'Payment created successfully',
        'data': new_payment
    }), HTTPStatus.CREATED

@api_bp.route('/payments/<payment_id>', methods=['PUT'])
def update_payment(payment_id: str):
    """Update existing payment."""
    data = request.get_json()
    
    updated_payment = payment_api.update_payment(payment_id, data)
    if not updated_payment:
        return jsonify({
            'status': 'error',
            'message': 'Payment not found'
        }), HTTPStatus.NOT_FOUND
    
    return jsonify({
        'status': 'success',
        'message': 'Payment updated successfully',
        'data': updated_payment
    }), HTTPStatus.OK

@api_bp.route('/payments/<payment_id>', methods=['DELETE'])
def delete_payment(payment_id: str):
    """Delete payment."""
    if payment_api.delete_payment(payment_id):
        return jsonify({
            'status': 'success',
            'message': 'Payment deleted successfully'
        }), HTTPStatus.OK
    
    return jsonify({
        'status': 'error',
        'message': 'Payment not found'
    }), HTTPStatus.NOT_FOUND

# Error handlers
@api_bp.errorhandler(Exception)
def handle_error(error):
    """Global error handler for API."""
    return jsonify({
        'status': 'error',
        'message': str(error)
    }), HTTPStatus.INTERNAL_SERVER_ERROR