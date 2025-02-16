# IT1556_AppDev
### Sample Customer
User: john@email.com , jane@email.com
PW: password


### Sample Admin
User: admin@admin.com  
PW: password

### REST API
This API provides the following endpoints:

GET /api/payments - Get all payments
GET /api/payments/<payment_id> - Get a specific payment
POST /api/payments - Create a new payment
PUT /api/payments/<payment_id> - Update a payment
DELETE /api/payments/<payment_id> - Delete a payment
# Get all payments
curl http://localhost:5000/api/payments

# Get specific payment
curl http://localhost:5000/api/payments/123

# Create payment
curl -X POST http://localhost:5000/api/payments \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","card_number":"4111111111111111","expiry_date":"12/25","cvv":"123"}'

# Update payment
curl -X PUT http://localhost:5000/api/payments/123 \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Doe","email":"jane@example.com"}'

# Delete payment
curl -X DELETE http://localhost:5000/api/payments/123