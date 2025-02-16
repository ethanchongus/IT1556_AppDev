import uuid
import shelve

shelve_db = 'database/tour_data'

# Tour Class
class tour:
    def __init__(self, name, description,country):
        self.__tour_id = None
        self.__name = name
        self.__description = description
        self.__country = country
        self.__departures = []

    def generate_tourID(self):
        self.__tour_id = uuid.uuid4()

    def get_tourID(self):
        return self.__tour_id

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    def get_description(self):
        return self.__description

    def set_description(self, description):
        self.__description = description

    def get_departures(self):
        return self.__departures

    def add_departure(self, departure):
        self.__departures.append(departure)

    def remove_departure(self, departure_id):
        self.__departures = [d for d in self.__departures if str(d.get_date()) != str(departure_id)]

    def get_country(self):
        return self.__country  

    def set_country(self, country):
        self.__country = country  

    def __str__(self):
        return f"Tour: {self.__name}\nDescription: {self.__description}\nDepartures: {len(self.__departures)} available\nID:{self.__tour_id}"


class departuredate:
    def __init__(self, date, price, availability):
        self.__date = date
        self.__price = price
        self.__availability = availability

    def get_date(self):
        return self.__date

    def set_date(self, date):
        self.__date = date

    def get_price(self):
        return self.__price

    def set_price(self, price):
        self.__price = price

    def get_availability(self):
        return self.__availability

    def set_availability(self, availability):
        self.__availability = availability

    def __str__(self):
        return f"Departure Date: {self.__date}, Price: ${self.__price}, Availability: {self.__availability} seats"


# Save a single tour to shelve
def save_tour(tour_obj):
    with shelve.open(shelve_db) as db:
        db[str(tour_obj.get_tourID())] = tour_obj


# Delete a single tour from shelve
def delete_tour(tour_id):
    with shelve.open(shelve_db) as db:
        if str(tour_id) in db:
            del db[str(tour_id)]


# Load all tours from shelve
def load_tours():
    with shelve.open(shelve_db) as db:
        return [db[key] for key in db]


# Get a specific tour by ID
def get_tour(tour_id):
    with shelve.open(shelve_db) as db:
        return db.get(str(tour_id), None)


def create_event(name, desc, country):
    t = tour(name, desc, country)  # Include country
    t.generate_tourID()
    save_tour(t)


def generateSampleTours():
    if not load_tours():  # Only generate samples if no tours exist
        create_event("Safari Adventure", "A thrilling safari experience.", "Indog")
        create_event("Mountain Hike", "A challenging but rewarding hike in the mountains.", "Indog")
        create_event("EcoVenture Tour", "Explore the best of Yishun.", "Singapore")
        create_event("Tokyo Highlights", "Explore the best of Tokyo in 7 days.", "Japan")
        create_event("Kyoto Serenity", "Discover the tranquil temples of Kyoto.", "Japan")
        create_event("Osaka Nightlife", "Experience the vibrant nightlife of Osaka.", "Japan")