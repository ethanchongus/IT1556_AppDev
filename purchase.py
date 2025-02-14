import uuid
import shelve

class Purchase:
    def __init__(self, tour_id, tour_name, departure_date, user_name, user_email, seats=1):
        self.__purchase_id = uuid.uuid4()
        self.__tour_id = tour_id
        self.__tour_name = tour_name
        self.__departure_date = departure_date
        self.__user_name = user_name
        self.__user_email = user_email
        self.__seats = seats

    # Getters
    def get_purchase_id(self):
        return self.__purchase_id

    def get_tour_id(self):
        return self.__tour_id

    def get_tour_name(self):
        return self.__tour_name

    def get_departure_date(self):
        return self.__departure_date

    def get_user_name(self):
        return self.__user_name

    def get_user_email(self):
        return self.__user_email

    def get_seats(self):
        return self.__seats

    # Setters
    def set_tour_id(self, tour_id):
        self.__tour_id = tour_id

    def set_tour_name(self, tour_name):
        self.__tour_name = tour_name

    def set_departure_date(self, departure_date):
        self.__departure_date = departure_date

    def set_user_name(self, user_name):
        self.__user_name = user_name

    def set_user_email(self, user_email):
        self.__user_email = user_email

    def set_seats(self, seats):
        self.__seats = seats

    def __str__(self):
        return f"Purchase by {self.__user_name} for {self.__tour_id} on {self.__departure_date} ({self.__seats} seats)"

purchase_db = 'database/purchase_data'

def save_purchase(purchase):
    with shelve.open(purchase_db) as db:
        db[str(purchase.get_purchase_id())] = purchase

def load_purchases():
    with shelve.open(purchase_db) as db:
        return [db[key] for key in db]
