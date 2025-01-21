import uuid
import shelve
import os

# Open the shelve file to store tours persistently
shelve_db = 'tour_data'

# Load tours from shelve at the start
def load_tours():
    if not os.path.exists(shelve_db + '.db'):  # Ensure the shelve database exists
        return []
    try:
        with shelve.open(shelve_db) as db:
            return db.get('tours', [])
    except AttributeError as e:
        print(f"Error loading tours: {e}. Clearing shelve database...")
        os.remove(shelve_db + '.db')  # Clear the corrupted shelve database
        return []  # Return an empty list


# Save tours to shelve
def save_tours():
    with shelve.open(shelve_db) as db:
        db['tours'] = tourlist

tourlist = load_tours()



#Tour Class
class tour:
    def __init__(self, name, description):
        self.tour_id = None
        self.name = name
        self.description = description
        self.departures = []

    def set_tourID(self, id):
        self.tour_id = id
    def generate_tourID(self):
        self.tour_id = uuid.uuid4()
        print(f"Tour ID for {self.name} is generated. - {self.tour_id}")
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

def create_event(name,desc):
    t = tour(name,desc)
    t.generate_tourID()
    tourlist.append(t)
    save_tours()

def delete_event(tour_id):
  for i, tour in enumerate(tourlist):
    if tour.tour_id == tour_id:
      print(f"Tour with ID {tour_id} deleted.")
      tourlist.pop(i)
      save_tours()



def generateSampleTours():
    if not tourlist:
        # create_event("EcoVenture Tour", "Explore the best of Yishun.")
        create_event("Tokyo Highlights", "Explore the best of Tokyo in 7 days.")
        create_event("Kyoto Serenity", "Discover the tranquil temples of Kyoto.")
        create_event("Osaka Nightlife", "Experience the vibrant nightlife of Osaka.")

        # Create a tour manually
        test_tour = tour("EcoVenture Tour", "Explore the best of Yishun.")
        test_tour.generate_tourID()
        tourlist.append(test_tour)

        # Create departures
        departure1 = departuredate("2024-09-01", 1500, 10)
        departure2 = departuredate("2024-09-15", 1600, 5)

        # Add departures to the tour
        test_tour.add_departure(departure1)
        test_tour.add_departure(departure2)
        save_tours()

        


