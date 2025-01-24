import uuid
import shelve


shelve_db = 'database/tour_data'

# Tour Class
class tour:
    def __init__(self, name, description):
        self.tour_id = None
        self.name = name
        self.description = description
        self.departures = []

    # def set_tourID(self, id):
    #     self.tour_id = id

    def generate_tourID(self):
        self.tour_id = uuid.uuid4()
        # print(f"Tour ID for {self.name} is generated. - {self.tour_id}")

    def get_tourID(self):
        return self.tour_id

    def add_departure(self, departure):
        self.departures.append(departure)

    def remove_departure(self, departure_id):
        self.departures = [d for d in self.departures if str(d.date) != str(departure_id)]

    def __str__(self):
        return f"Tour: {self.name}\nDescription: {self.description}\nDepartures: {len(self.departures)} available\nID:{self.tour_id}"


class departuredate:
    def __init__(self, date, price, availability):
        self.date = date
        self.price = price
        self.availability = availability

    def __str__(self):
        return f"Departure Date: {self.date}, Price: ${self.price}, Availability: {self.availability} seats"


# Save a single tour to shelve
def save_tour(tour_obj):
    with shelve.open(shelve_db) as db:
        db[str(tour_obj.tour_id)] = tour_obj


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


def create_event(name, desc):
    t = tour(name, desc)
    t.generate_tourID()
    save_tour(t)


def generateSampleTours():
    if not load_tours():  # Only generate samples if no tours exist
        create_event("Safari Adventure", "A thrilling safari experience.")
        create_event("Mountain Hike", "A challenging but rewarding hike in the mountains.")
        create_event("EcoVenture Tour", "Explore the best of Yishun.")
        create_event("Tokyo Highlights", "Explore the best of Tokyo in 7 days.")
        create_event("Kyoto Serenity", "Discover the tranquil temples of Kyoto.")
        create_event("Osaka Nightlife", "Experience the vibrant nightlife of Osaka.")

# def create_event(name,desc):
#     t = tour(name,desc)
#     t.generate_tourID()
#     tourlist.append(t)
#     save_tours()

# def delete_event(tour_id):
#   for i, tour in enumerate(tourlist):
#     if tour.tour_id == tour_id:
#       print(f"Tour with ID {tour_id} deleted.")
#       tourlist.pop(i)
#       save_tours()


# def generateSampleTours():
#     if not load_tours():
#         # create_event("EcoVenture Tour", "Explore the best of Yishun.")
#         create_event("Tokyo Highlights", "Explore the best of Tokyo in 7 days.")
#         create_event("Kyoto Serenity", "Discover the tranquil temples of Kyoto.")
#         create_event("Osaka Nightlife", "Experience the vibrant nightlife of Osaka.")

#         # Create a tour manually
#         test_tour = tour("EcoVenture Tour", "Explore the best of Yishun.")
#         test_tour.generate_tourID()
#         tourlist.append(test_tour)

#         # Create departures
#         departure1 = departuredate("2024-09-01", 1500, 10)
#         departure2 = departuredate("2024-09-15", 1600, 5)

#         # Add departures to the tour
#         test_tour.add_departure(departure1)
#         test_tour.add_departure(departure2)
#         save_tours()

        


