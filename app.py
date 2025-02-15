from activities import *
from purchase import *
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from payment_routes import *
from admin_routes import admin_bp
from Forms import *
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from User import User
from Customer import Customer
from Forms import EditProfileForm
from api_routes import api_bp

import requests


app = Flask(__name__)
app.secret_key = 'ecoventures'
    
# Register Blueprints
app.register_blueprint(payment_bp, url_prefix='/payment')
app.register_blueprint(admin_bp, url_prefix='/admin/payments')
app.register_blueprint(api_bp)


@app.route('/')
def index():
    form = SearchTourForm()
    return render_template('index.html', form=form)


OLLAMA_URL = "http://ollama.ethanos.xyz/api/generate" #crazy cybersecurity, too lz to do env

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    
    # Prepare the request for Ollama
    data = {
        "model": "ecoventure1",  # Replace with your preferred model
        "prompt": user_message,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=data)
        response.raise_for_status()
        assistant_response = response.json()['response']
        return jsonify({'message': assistant_response})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500


# Flask route for handling 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_404_page.html'), 404

@app.route('/admin/', methods=['GET'])
@login_required
def admin_panel():
    if not current_user.is_authenticated or not hasattr(current_user, 'is_admin') or not current_user.is_admin():
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for('index'))

    tours = load_tours()
    purchases = load_purchases()

    # Tour Statistics
    total_tours = len(tours)
    total_departures = sum(len(tour.get_departures()) for tour in tours)
    tour_countries = set(tour.get_country() for tour in tours)
    country_distribution = {country: sum(1 for tour in tours if tour.get_country() == country) for country in tour_countries}

    # Customer Statistics
    with shelve.open('database/customer.db', 'r') as db:
        customers = db.get('Customers', {})
    total_customers = len(customers)

    # Booking Statistics
    total_bookings = len(purchases)
    bookings_per_tour = {}
    for purchase in purchases:
        tour_name = purchase.get_tour_name()
        bookings_per_tour[tour_name] = bookings_per_tour.get(tour_name, 0) + 1

    return render_template('admin_dashboard.html',
                           total_tours=total_tours,
                           total_departures=total_departures,
                           country_distribution=country_distribution,
                           total_customers=total_customers,
                           total_bookings=total_bookings,
                           bookings_per_tour=bookings_per_tour)


# ACTIVITIES
@app.route('/tours/', methods=['GET'])
def user_viewtours():
    tours = load_tours()  # Load all tours
    selected_countries = request.args.getlist('country')  # Get selected checkboxes

    if 'all' not in selected_countries and selected_countries:
        tours = [tour for tour in tours if tour.get_country() in selected_countries]

    # Get unique country list for filtering
    unique_countries = set(tour.get_country() for tour in load_tours())

    return render_template(
        'user_viewtours.html',
        tours=tours,
        countries=unique_countries,
        selected_countries=selected_countries
    )



@app.route('/admin/activities/', methods=['GET', 'POST'])
@login_required
def admin_events():
    if not current_user.is_authenticated or not hasattr(current_user, 'is_admin') or not current_user.is_admin():
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for('index'))

    tours = load_tours()
    add_form = AddTourForm()

    if add_form.validate_on_submit() and add_form.submit.data:
        try:
            name = add_form.event_name.data
            desc = add_form.event_desc.data
            country = add_form.country.data.capitalize()  # Capture country input
            create_event(name, desc, country)  # Pass country to the event
            flash(f"Tour '{name}' added.", "success")
        except Exception as e:
            flash("Failed to add tour.", "danger")
            print(e)
        return redirect(url_for('admin_events'))
    # elif add_form.is_submitted() and not add_form.validate():
    #     # Flash validation errors for the AddTourForm
    #     for field, errors in add_form.errors.items():
    #         for error in errors:
    #             flash(f"Error in {field.replace('_', ' ').title()}: {error}", "danger")


    if request.method == 'POST':
        # if 'add_event' in request.form:
        #     name = request.form['event_name']
        #     desc = request.form['event_desc']
        #     create_event(name, desc)

        if "delete_tourid" in request.form:
            touridtodelete = uuid.UUID(request.form['delete_tourid'])
            delete_tour(touridtodelete)

        return redirect(url_for('admin_events'))

    return render_template('ADMIN_activities.html', tours=tours,add_form=add_form,)


@app.route('/admin/activities/edit/<tour_id>', methods=['GET', 'POST'])
@login_required
def edit_tour(tour_id):
    if not current_user.is_authenticated or not hasattr(current_user, 'is_admin') or not current_user.is_admin():
        print("User not admin")
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for('index'))
    tour = get_tour(tour_id)

    if not tour:
        return "Tour not found", 404

    if request.method == 'POST':
        if 'basic_edit' in request.form:
            tour.set_name(request.form['name'])
            tour.set_description(request.form['description'])
            tour.set_country(request.form['country'])

        if 'add_departure' in request.form:
            departure_date = request.form['departure_date']
            departure_price = float(request.form['departure_price'])
            departure_availability = int(request.form['departure_availability'])
            tour.add_departure(departuredate(departure_date, departure_price, departure_availability))

        if 'delete_departure' in request.form:
            tour.remove_departure(request.form['delete_departure'])

        if 'edit_departure_date' in request.form:
            original_date = request.form['original_departure_date']
            for departure in tour.get_departures():
                if str(departure.get_date()) == str(original_date):
                    departure.set_date(request.form['edit_departure_date'])
                    departure.set_price(float(request.form['edit_departure_price']))
                    departure.set_availability(int(request.form['edit_departure_availability']))
                    break

        save_tour(tour)  # Save updated tour
        return redirect(url_for('edit_tour', tour_id=tour_id))

    return render_template('Admin_edittours.html', tour=tour)

@app.route('/add/<tour_id>', methods=['GET', 'POST'])
@login_required
def prepurchase_tour(tour_id):
    cart = Cart(session)
    tour = get_tour(tour_id)

    if not tour:
        flash("Tour not found.", "danger")
        return redirect(url_for('user_viewtours'))

    # Check for available departures
    available_departures = [
        (d.get_date(), f"{d.get_date()} - ${d.get_price()} ({d.get_availability()} seats available)")
        for d in tour.get_departures()
        if d.get_availability() > 0
    ]

    if not available_departures:
        flash("No available departure dates for this tour.", "warning")
        return redirect(url_for('user_viewtours'))

    # Create form and populate departure date choices
    form = TourPrePurchaseForm()
    form.departure_date.choices = available_departures

    # Pre-fill user details if logged in
    if current_user.is_authenticated:
        form.user_name.data = current_user.get_name()
        form.user_email.data = current_user.get_email()

    if form.validate_on_submit():
        selected_departure = next(
            (d for d in tour.get_departures() if d.get_date() == form.departure_date.data),
            None
        )

        if selected_departure and selected_departure.get_availability() >= form.seats.data:
            item = cart.add_item(
                activity_id=tour_id,
                name=tour.get_name(),
                price=selected_departure.get_price(),
                departure_date=form.departure_date.data,
                seats=form.seats.data
            )
            cart.save()

            flash(f"{tour.get_name()} added to cart. Proceed to checkout.", "success")
            return redirect(url_for('payment.view_cart'))
        else:
            flash("Not enough availability for the selected date.", "danger")

    return render_template('prepurchase_tour.html', form=form, tour=tour)



@app.route('/user/bookings/', methods=['GET', 'POST'])
@login_required
def user_bookings():
    purchases = load_purchases()
    user_email = current_user.get_email()
    user_purchases = [purchase for purchase in purchases if purchase.get_user_email() == user_email]

    passenger_form = PassengerForm()

    if request.method == 'POST' and passenger_form.validate_on_submit():
        purchase_id = request.form.get("purchase_id")
        seat_number = int(request.form.get("seat_number"))

        if not purchase_id:
            flash("Invalid purchase ID.", "danger")
            return redirect(url_for('user_bookings'))

        with shelve.open(purchase_db, writeback=True) as db:
            if purchase_id in db:
                purchase = db[purchase_id]
                
                new_passenger = Passenger(
                    passenger_form.name.data,
                    passenger_form.age.data,
                    passenger_form.passport_number.data,
                    passenger_form.contact_number.data,
                    passenger_form.email.data
                )

                # If seat already has a passenger, update it; otherwise, add a new passenger
                if seat_number < len(purchase.get_passengers()):
                    purchase.get_passengers()[seat_number] = new_passenger
                else:
                    purchase.get_passengers().append(new_passenger)

                db[purchase_id] = purchase
                flash("Passenger details updated successfully!", "success")
            else:
                flash("Purchase not found!", "danger")

        return redirect(url_for('user_bookings'))

    return render_template('user_bookings.html', purchases=user_purchases, passenger_form=passenger_form)




@app.route('/admin/activities/<tour_id>/customers/<departure_date>')
@login_required
def view_customers(tour_id, departure_date):
    if not current_user.is_authenticated or not hasattr(current_user, 'is_admin') or not current_user.is_admin():
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for('index'))
    tour = get_tour(tour_id)
    tourname = tour.get_name() 
    departure_date = departure_date
    purchases = load_purchases()
    customers = [purchase for purchase in purchases if purchase.get_tour_id() == tour_id and purchase.get_departure_date() == departure_date]

    return render_template('admin_viewcustomers.html', customers=customers, departure_date = departure_date, tourname=tourname)



@app.route('/admin/activities/<tour_id>/customers/<departure_date>/remove', methods=['POST'])
@login_required
def remove_customer(tour_id, departure_date):
    if not current_user.is_authenticated or not hasattr(current_user, 'is_admin') or not current_user.is_admin():
        print("User not admin")
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for('index'))
    purchase_id = request.form.get('purchase_id')
    if purchase_id:
        with shelve.open(purchase_db) as db:
            if purchase_id in db:
                purchase = db[purchase_id]
                tour = get_tour(tour_id)

                # Increment the availability for the removed seats
                for departure in tour.get_departures():
                    if departure.get_date() == departure_date:
                        departure.set_availability(departure.get_availability() + purchase.get_seats())
                        break

                # Delete the purchase from the database
                del db[purchase_id]

                # Save updated tour data
                save_tour(tour)

                flash("Customer removed successfully.","info")
            else:
                flash("Customer not found.","warning")
    else:
        flash("Invalid request.","danger")

    return redirect(url_for('view_customers', tour_id=tour_id, departure_date=departure_date))






# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.route('/createUser', methods=['GET', 'POST'])
def create_user():
    create_user_form = CreateUserForm(request.form)
    if request.method == 'POST' and create_user_form.validate():
        users_dict = {}
        db = shelve.open('database/user.db', 'c')

        try:
            users_dict = db['Users']
        except:
            print("Error in retrieving Users from user.db.")

        user = User(create_user_form.first_name.data, create_user_form.last_name.data, create_user_form.gender.data, create_user_form.membership.data, create_user_form.remarks.data,create_user_form.number.data,create_user_form.email.data,create_user_form.password.data)
        users_dict[user.get_user_id()] = user
        db['Users'] = users_dict

        db.close()

        return redirect(url_for('retrieve_users'))
    return render_template('createUser.html', form=create_user_form)


@app.route('/retrieveUsers')
def retrieve_users():
    users_dict = {}
    db = shelve.open('database/user.db', 'r')
    users_dict = db['Users']
    db.close()

    users_list = []
    for key in users_dict:
        user = users_dict.get(key)
        users_list.append(user)

    return render_template('retrieveUser.html', count=len(users_list), users_list=users_list)


@app.route('/updateUser/<int:id>/', methods=['GET', 'POST'])
def update_user(id):
    update_user_form = CreateUserForm(request.form)
    if request.method == 'POST' and update_user_form.validate():
        users_dict = {}
        db = shelve.open('database/user.db', 'w')
        users_dict = db['Users']

        user = users_dict.get(id)
        user.set_first_name(update_user_form.first_name.data)
        user.set_last_name(update_user_form.last_name.data)
        user.set_gender(update_user_form.gender.data)
        user.set_membership(update_user_form.membership.data)
        user.set_remarks(update_user_form.remarks.data)
        user.set_phone_number(update_user_form.number.data)
        user.set_email(update_user_form.email.data)

        db['Users'] = users_dict
        db.close()

        return redirect(url_for('retrieve_users'))
    else:
        users_dict = {}
        db = shelve.open('database/user.db', 'r')
        users_dict = db['Users']
        db.close()

        user = users_dict.get(id)
        update_user_form.first_name.data = user.get_first_name()
        update_user_form.last_name.data = user.get_last_name()
        update_user_form.gender.data = user.get_gender()
        update_user_form.membership.data = user.get_membership()
        update_user_form.remarks.data = user.get_remarks()
        update_user_form.number.data = user.get_phone_number()
        update_user_form.email.data = user.get_email()

        return render_template('updateUser.html', form=update_user_form)


@app.route('/deleteUser/<int:id>', methods=['POST'])
def delete_user(id):
    users_dict = {}
    db = shelve.open('database/user.db', 'w')
    users_dict = db['Users']

    users_dict.pop(id)

    db['Users'] = users_dict
    db.close()

    return redirect(url_for('retrieve_users'))


@app.route('/register', methods=['GET', 'POST'])
def register_customer():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    create_customer_form = CreateCustomerForm(request.form)
    if request.method == 'POST' and create_customer_form.validate():
        customers_dict = {}
        db = shelve.open('database/customer.db', 'c')

        try:
            customers_dict = db['Customers']
        except:
            print("Error in retrieving Customers from customer.db.")
            customers_dict = {}

        # Check if email already exists
        for user in customers_dict.values():
            if user.get_email() == create_customer_form.email.data:
                flash('Email already registered', 'danger')
                return render_template('register.html', form=create_customer_form)

        customer = Customer(
            create_customer_form.name.data,
            create_customer_form.email.data,
            create_customer_form.password.data,
            create_customer_form.confirm_password.data,
            create_customer_form.number.data
        )
        customers_dict[customer.get_customer_id()] = customer
        db['Customers'] = customers_dict
        db.close()

        login_user(customer)
        flash('Registration successful!', 'success')
        return redirect(url_for('index'))

    return render_template('register.html', form=create_customer_form)


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    customers_dict = {}
    db = shelve.open('database/customer.db', 'r')
    try:
        customers_dict = db['Customers']
    except:
        print("Error in retrieving Customers from customer.db.")
    db.close()

    # Get the current user's ID and use it to find the customer
    customer_id = int(current_user.get_id())
    customer = customers_dict.get(customer_id)

    if customer:
        return render_template('profile.html', customer=customer)
    else:
        flash("Customer not found.", "danger")
        return redirect(url_for('index'))

@app.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
def edit_profile(id):
    form = EditProfileForm()

    # Open the shelve database
    db = shelve.open('database/customer.db', 'c')
    customers_dict = db.get('Customers', {})

    # Get the customer by ID
    customer = customers_dict.get(id)
    if not customer:
        db.close()
        return "Customer not found", 404

    # Pre-fill the form fields with the current customer details
    if request.method == 'GET':
        form.name.data = customer.get_name()
        form.email.data = customer.get_email()
        form.number.data = customer.get_number()

    # Update customer details when form is submitted
    if form.validate_on_submit():
        customer.set_name(form.name.data)
        customer.set_email(form.email.data)
        customer.set_number(form.number.data)
        customers_dict[id] = customer
        db['Customers'] = customers_dict
        db.close()
        return redirect(url_for('profile', id=id))

    db.close()
    return render_template('edit_profile.html', form=form, customer=customer)





@login_manager.user_loader
def load_user(user_id):
    # First check customers
    db = shelve.open('database/customer.db', 'r')
    try:
        users_dict = db['Customers']
        user = users_dict.get(int(user_id))
        db.close()
        if user:
            return user
    except:
        db.close()

    # Then check admin users
    db = shelve.open('database/user.db', 'r')
    try:
        users_dict = db['Users']
        user = users_dict.get(int(user_id))
        db.close()
        return user
    except:
        db.close()
        return None

@login_manager.unauthorized_handler
def unauthorized():
    flash("Kindly log in to access this page.", "warning")
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect to the stored URL or the homepage if already logged in
        next_url = session.pop('next', None)
        return redirect(next_url or url_for('index'))

    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        users_dict = {}
        db = shelve.open('database/customer.db', 'r')
        try:
            users_dict = db['Customers']
        except:
            db.close()
            flash('Error accessing user database', 'danger')
            return redirect(url_for('login'))

        # Find user by email
        user = None
        for u in users_dict.values():
            if u.get_email() == form.email.data:
                user = u
                break

        db.close()

        if user and user.get_password() == form.password.data:
            login_user(user)
            flash('Logged in successfully.', 'success')
            
            # Retrieve the next URL stored in the session
            next_url = session.pop('next', None)
            
            return redirect(next_url or url_for('index'))  # Redirect to the stored URL or homepage
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        users_dict = {}
        db = shelve.open('database/user.db', 'r')  # Open user database
        try:
            users_dict = db['Users']
        except:
            db.close()
            flash('Error accessing user database', 'danger')
            return redirect(url_for('admin_login'))

        # Find admin user by email
        admin_user = None
        for u in users_dict.values():
            if u.get_email() == form.email.data and u.is_admin():  # Check email and admin status
                admin_user = u
                break

        db.close()

        # Validate credentials
        if admin_user and admin_user.get_password() == form.password.data:
            login_user(admin_user)
            flash('Admin logged in successfully.', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid admin credentials. Please try again.', 'danger')

    return render_template('adminlogin.html', form=form)


def create_defaultadmin():
    users_dict = {}
    db = shelve.open('database/user.db', 'c')

    try:
        users_dict = db['Users']
    except:
        print("Error in retrieving Users from user.db.")

    user = User("admin", "tan", "Male", "nil","nil","nil","admin@email.com","password",True)
    users_dict[user.get_user_id()] = user
    db['Users'] = users_dict

    db.close()

# create_defaultadmin()

if __name__ == '__main__':
    generateSampleTours()
    app.run(debug=True)


