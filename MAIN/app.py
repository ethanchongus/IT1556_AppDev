from flask import Flask, flash, render_template, request, redirect, url_for

from activities import *

app = Flask(__name__)
app.secret_key = 'ecoventures'



@app.route('/')
def index():
    return render_template('index.html')


# ACTIVITIES (ETHAN)
@app.route('/tours')
def user_viewtours():

    return render_template('user_viewtours.html',tours=toursdict)

@app.route('/tours')
def user_viewtours():

    return render_template('user_viewtours.html',tours=tourlist)

@app.route('/admin/activities/', methods=['GET', 'POST'])
def admin_events():


    if request.method == 'POST':
        if 'add_event' in request.form:
            name = request.form['event_name']
            desc = request.form['event_desc']
            create_event(name,desc)
        
        if "delete_tourid" in request.form:
            touridtodelete = uuid.UUID(request.form['delete_tourid'])
            delete_event(touridtodelete)
       
        return redirect(url_for('admin_events'))

    return render_template('ADMIN_activities.html', tours=tourlist)

@app.route('/admin/activities/edit/<tour_id>', methods=['GET', 'POST'])
def edit_tour(tour_id):


    tour = None
    for t in tourlist:
        # print(f"checking {tour_id} against {t.tour_id}")
        if str(tour_id) == str(t.tour_id):
            tour = t
            print("Tour found!")
            break
    
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
                    print(f"Updated departure: {departure}")
                    break
        
        save_tours()
        return redirect(url_for('edit_tour', tour_id=tour_id))

    return render_template('Admin_edittours.html', tour=tour)

generateSampleTours()
generateSampleTours()




# ===============================================
# ???? 









if __name__ == '__main__':
    # generateSampleTours()
    app.run(debug=True)