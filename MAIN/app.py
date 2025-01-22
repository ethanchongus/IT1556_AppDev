from flask import Flask, render_template, request, redirect, url_for , flash
from Forms import CreateUserForm , CreateCustomerForm
import shelve, User , Customer
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from Forms import LoginForm

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for sessions
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

        user = User.User(create_user_form.first_name.data, create_user_form.last_name.data, create_user_form.gender.data, create_user_form.membership.data, create_user_form.remarks.data,create_user_form.number.data,create_user_form.email.data)
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

    return render_template('retrieveUsers.html', count=len(users_list), users_list=users_list)


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
    users_dict = {}
    db = shelve.open('customer.db', 'r')
    try:
        users_dict = db['Customers']
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



if __name__ == '__main__':
    app.run(debug=True)

