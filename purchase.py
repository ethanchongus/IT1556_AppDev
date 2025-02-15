import uuid
import shelve

class Passenger:
    def __init__(self, name, age, passport_number, contact_number, email):
        self.__passenger_id = uuid.uuid4()
        self.__name = name
        self.__age = age
        self.__passport_number = passport_number
        self.__contact_number = contact_number
        self.__email = email

    # Getters
    def get_passenger_id(self):
        return self.__passenger_id

    def get_name(self):
        return self.__name

    def get_age(self):
        return self.__age

    def get_passport_number(self):
        return self.__passport_number

    def get_contact_number(self):
        return self.__contact_number

    def get_email(self):
        return self.__email

    # Setters
    def set_name(self, name):
        self.__name = name

    def set_age(self, age):
        self.__age = age

    def set_passport_number(self, passport_number):
        self.__passport_number = passport_number

    def set_contact_number(self, contact_number):
        self.__contact_number = contact_number

    def set_email(self, email):
        self.__email = email


class Purchase:
    def __init__(self, tour_id, tour_name, departure_date, user_name, user_email, seats=1):
        self.__purchase_id = uuid.uuid4()
        self.__tour_id = tour_id
        self.__tour_name = tour_name
        self.__departure_date = departure_date
        self.__user_name = user_name
        self.__user_email = user_email
        self.__seats = seats
        self.__passengers = []  # Store passenger info

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
    def get_passengers(self):
        return self.__passengers

   

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

    def add_passenger(self, passenger):
        self.__passengers.append(passenger)

    def set_passengers(self, passengers):
        self.__passengers = passengers

    def __str__(self):
        return f"Purchase by {self.__user_name} for {self.__tour_id} on {self.__departure_date} ({self.__seats} seats)"

purchase_db = 'database/purchase_data'

def save_purchase(purchase):
    with shelve.open(purchase_db) as db:
        db[str(purchase.get_purchase_id())] = purchase

def load_purchases():
    with shelve.open(purchase_db) as db:
        return [db[key] for key in db]
    
def delete_purchase(purchase_id):
    with shelve.open(purchase_db, writeback=True) as db:
        if purchase_id in db:
            del db[purchase_id]
