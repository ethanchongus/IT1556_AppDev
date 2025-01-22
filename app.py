from flask import Flask, flash, render_template, request, redirect, url_for
from activities import *
from purchase import *

app = Flask(__name__)
app.secret_key = 'ecoventures'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin_panel():
    return render_template('admin_panel.html')

# ACTIVITIES
@app.route('/tours')
def user_viewtours():
    tours = load_tours()
    return render_template('user_viewtours.html', tours=tours)


@app.route('/admin/activities/', methods=['GET', 'POST'])
def admin_events():
    tours = load_tours()

    if request.method == 'POST':
        if 'add_event' in request.form:
            name = request.form['event_name']
            desc = request.form['event_desc']
            create_event(name, desc)

        if "delete_tourid" in request.form:
            touridtodelete = uuid.UUID(request.form['delete_tourid'])
            delete_tour(touridtodelete)

        return redirect(url_for('admin_events'))

    return render_template('ADMIN_activities.html', tours=tours)


@app.route('/admin/activities/edit/<tour_id>', methods=['GET', 'POST'])
def edit_tour(tour_id):
    tour = get_tour(tour_id)

    if not tour:
        return "Tour not found", 404

    if request.method == 'POST':
        if 'basic_edit' in request.form:
            tour.name = request.form['name']
            tour.description = request.form['description']

        if 'add_departure' in request.form:
            departure_date = request.form['departure_date']
            departure_price = float(request.form['departure_price'])
            departure_availability = int(request.form['departure_availability'])
            tour.add_departure(departuredate(departure_date, departure_price, departure_availability))

        if 'delete_departure' in request.form:
            tour.remove_departure(request.form['delete_departure'])

        if 'edit_departure_date' in request.form:
            original_date = request.form['original_departure_date']
            for departure in tour.departures:
                if str(departure.date) == str(original_date):
                    departure.date = request.form['edit_departure_date']
                    departure.price = float(request.form['edit_departure_price'])
                    departure.availability = int(request.form['edit_departure_availability'])
                    break

        save_tour(tour)  # Save updated tour
        return redirect(url_for('edit_tour', tour_id=tour_id))

    return render_template('Admin_edittours.html', tour=tour)

@app.route('/purchase/<tour_id>', methods=['GET', 'POST'])
def purchase_tour(tour_id):
    tour = get_tour(tour_id)

    if not tour:
        return "Tour not found", 404

    if request.method == 'POST':
        departure_date = request.form['departure_date']
        user_name = request.form['user_name']
        user_email = request.form['user_email']
        seats = int(request.form['seats'])

        # Find the selected departure and decrease availability
        selected_departure = next((d for d in tour.departures if d.date == departure_date), None)
        if selected_departure and selected_departure.availability >= seats:
            selected_departure.availability -= seats
            save_tour(tour)

            # Create and save purchase
            purchase = Purchase(tour_id, departure_date, user_name, user_email, seats)
            save_purchase(purchase)

            flash("Purchase successful!")
            return redirect(url_for('user_viewtours'))
        else:
            flash("Not enough availability for the selected date.")

    return render_template('purchase_tour.html', tour=tour)

@app.route('/admin/activities/<tour_id>/customers/<departure_date>')
def view_customers(tour_id, departure_date):
    purchases = load_purchases()
    customers = [purchase for purchase in purchases if purchase.tour_id == tour_id and purchase.departure_date == departure_date]
    return render_template('admin_viewcustomers.html', customers=customers, tour_id=tour_id, departure_date=departure_date)

@app.route('/admin/activities/<tour_id>/customers/<departure_date>/remove', methods=['POST'])
def remove_customer(tour_id, departure_date):
    purchase_id = request.form.get('purchase_id')
    if purchase_id:
        with shelve.open(purchase_db) as db:
            if purchase_id in db:
                purchase = db[purchase_id]
                tour = get_tour(tour_id)

                # Increment the availability for the removed seats
                for departure in tour.departures:
                    if departure.date == departure_date:
                        departure.availability += purchase.seats
                        break

                # Delete the purchase from the database
                del db[purchase_id]

                # Save updated tour data
                save_tour(tour)

                flash("Customer removed successfully.")
            else:
                flash("Customer not found.")
    else:
        flash("Invalid request.")

    return redirect(url_for('view_customers', tour_id=tour_id, departure_date=departure_date))



if __name__ == '__main__':
    # generateSampleTours()
    app.run(debug=True)