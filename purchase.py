import uuid
import shelve
class Purchase:
    def __init__(self, tour_id, tour_name, departure_date, user_name, user_email, seats=1):
            self.purchase_id = uuid.uuid4()
            self.tour_id = tour_id
            self.tour_name = tour_name
            self.departure_date = departure_date
            self.user_name = user_name
            self.user_email = user_email
            self.seats = seats

    def __str__(self):
        return f"Purchase by {self.user_name} for {self.tour_id} on {self.departure_date} ({self.seats} seats)"

purchase_db = 'database/purchase_data'

def save_purchase(purchase):
    with shelve.open(purchase_db) as db:
        db[str(purchase.purchase_id)] = purchase

def load_purchases():
    with shelve.open(purchase_db) as db:
        return [db[key] for key in db]