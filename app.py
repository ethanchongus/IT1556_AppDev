from flask import Flask, render_template, request, redirect, url_for, flash
from payment_routes import payment_bp
from admin_routes import admin_bp
from Forms import CreateUserForm, CreateCustomerForm, LoginForm
import shelve
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from User import User, Customer

# Initialize the Flask app
app = Flask(__name__)
# Set the secret key for the Flask app
app.secret_key = "secret"  # Replace with a strong, unique key

# Register Blueprints
app.register_blueprint(payment_bp, url_prefix='/payment')
app.register_blueprint(admin_bp, url_prefix='/admin/payments')

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/')
def admin():
    return render_template('admin_panel.html')

@app.route('/createUser', methods=['GET', 'POST'])
def create_user():
    create_user_form = CreateUserForm(request.form)
    if request.method == 'POST' and create_user_form.validate():
        users_dict = {}
        db = shelve.open('user.db', 'c')

        try:
            users_dict = db['Users']
        except:
            print("Error in retrieving Users from user.db.")

        user = User.User(create_user_form.first_name.data, create_user_form.last_name.data, create_user_form.gender.data, create_user_form.membership.data, create_user_form.remarks.data,create_user_form.number.data,create_user_form.email.data,create_user_form.password.data)
        users_dict[user.get_user_id()] = user
        db['Users'] = users_dict

        db.close()

        return redirect(url_for('retrieve_users'))
    return render_template('createUser.html', form=create_user_form)


@app.route('/retrieveUsers')
def retrieve_users():
    users_dict = {}
    db = shelve.open('user.db', 'r')
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
        db = shelve.open('user.db', 'w')
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
        db = shelve.open('user.db', 'r')
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
    db = shelve.open('user.db', 'w')
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
        db = shelve.open('customer.db', 'c')

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

        customer = Customer.Customer(
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

@login_manager.user_loader
def load_user(user_id):
    # First check customers
    db = shelve.open('customer.db', 'r')
    try:
        users_dict = db['Customers']
        user = users_dict.get(int(user_id))
        db.close()
        if user:
            return user
    except:
        db.close()

    # Then check admin users
    db = shelve.open('user.db', 'r')
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
        return redirect(url_for('index'))

    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        users_dict = {}
        db = shelve.open('customer.db', 'r')
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
            return redirect(url_for('index'))
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
        db = shelve.open('user.db', 'r')  # Open user database
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
            return redirect(url_for('admin'))
        else:
            flash('Invalid admin credentials. Please try again.', 'danger')

    return render_template('adminlogin.html', form=form)@app.route('/purchase/<tour_id>', methods=['GET', 'POST'])
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

