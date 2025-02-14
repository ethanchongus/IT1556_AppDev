import shelve
purchase_db = 'database/purchase_data'

with shelve.open(purchase_db, 'r') as db:
    for key in db:
        purchase = db[key]
        print(f"Purchase ID: {purchase.get_purchase_id()}, User Email: {purchase.get_user_email()}, Tour: {purchase.get_tour_name()}, Seats: {purchase.get_seats()}")
