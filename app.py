from activities import *
from purchase import *
from flask import Flask, render_template, request, redirect, url_for, flash, session
from payment_routes import payment_bp
from admin_routes import admin_bp
from Forms import *
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from User import User
from Customer import Customer
from Forms import EditProfileForm

app = Flask(__name__)
app.secret_key = 'ecoventures'
    



@app.route('/')
def index():
    return render_template('index.html')

# Flask route for handling 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_404_page.html'), 404

@app.route('/admin/')
@login_required
def admin_panel():
    if not current_user.is_authenticated or not hasattr(current_user, 'is_admin') or not current_user.is_admin():
        print("User not admin")
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for('index'))
    return render_template('admin_panel.html')

# ACTIVITIES
@app.route('/tours/')
def user_viewtours():
    tours = load_tours()
    return render_template('user_viewtours.html', tours=tours)


@app.route('/admin/activities/', methods=['GET', 'POST'])
@login_required
def admin_events():
    if not current_user.is_authenticated or not hasattr(current_user, 'is_admin') or not current_user.is_admin():
        print("User not admin")
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for('index'))
    tours = load_tours()
    add_form = AddTourForm()

    if add_form.validate_on_submit() and add_form.submit.data:
        try:
            name = add_form.event_name.data
            desc = add_form.event_desc.data
            create_event(name, desc)
            flash(f"Tour '{name}' has been successfully added.", "success")
        except Exception as e:
            flash("Failed to add tour. Please try again.", "danger")
            print(e)
        return redirect(url_for('admin_events'))
    elif add_form.is_submitted() and not add_form.validate():
        # Flash validation errors for the AddTourForm
        for field, errors in add_form.errors.items():
            for error in errors:
                flash(f"Error in {field.replace('_', ' ').title()}: {error}", "danger")


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
@login_required
def purchase_tour(tour_id):
    tour = get_tour(tour_id)
    if not tour:
        return "Tour not found", 404

    # Check for available departures
    available_departures = [
        (d.date, f"{d.date} - ${d.price} ({d.availability} seats available)")
        for d in tour.departures
        if d.availability > 0
    ]

    if not available_departures:
        flash("No available departure dates for this tour. Please check back later.", "warning")
        return redirect(url_for('user_viewtours'))

    # Create form and populate departure date choices
    form = TourPurchaseForm()
    form.departure_date.choices = available_departures

    # Pre-fill customer details if logged in
    if current_user.is_authenticated:
        form.user_name.data = current_user.get_name()
        form.user_email.data = current_user.get_email()

    if form.validate_on_submit():
        selected_departure = next(
            (d for d in tour.departures if d.date == form.departure_date.data),
            None
        )

        if selected_departure and selected_departure.availability >= form.seats.data:
            selected_departure.availability -= form.seats.data
            save_tour(tour)

            purchase = Purchase(
                tour_id=tour_id,
                tour_name=tour.name,  
                departure_date=form.departure_date.data,
                user_name=current_user.get_name(),
                user_email=current_user.get_email(),
                seats=form.seats.data
            )
            save_purchase(purchase)

            flash("Purchase successful!", "success")
            return redirect(url_for('user_viewtours'))
        else:
            flash("Not enough availability for the selected date.", "danger")

    return render_template('purchase_tour.html', form=form, tour=tour)


@app.route('/user/bookings/', methods=['GET'])
@login_required
def user_bookings():
    purchases = load_purchases()  # Load all purchases
    user_email = current_user.get_email()  # Get the logged-in user's email
    user_purchases = [purchase for purchase in purchases if purchase.user_email == user_email]  # Filter purchases by email
    
    return render_template('user_bookings.html', purchases=user_purchases)


@app.route('/admin/activities/<tour_id>/customers/<departure_date>')
@login_required
def view_customers(tour_id, departure_date):
    if not current_user.is_authenticated or not hasattr(current_user, 'is_admin') or not current_user.is_admin():
        print("User not admin")
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for('index'))
    purchases = load_purchases()
    customers = [purchase for purchase in purchases if purchase.tour_id == tour_id and purchase.departure_date == departure_date]
    return render_template('admin_viewcustomers.html', customers=customers, tour_id=tour_id, departure_date=departure_date)

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





# Register Blueprints
app.register_blueprint(payment_bp, url_prefix='/payment')
app.register_blueprint(admin_bp, url_prefix='/admin/payments')

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

create_defaultadmin()

if __name__ == '__main__':
    generateSampleTours()
    app.run(debug=True)


