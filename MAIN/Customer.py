class Customer:
    count_id = 0

    def __init__(self, name, email, password, confirm_password, number):
        if password != confirm_password:
            raise ValueError("Password and confirm password do not match")

        Customer.count_id += 1
        self.__customer_id = Customer.count_id
        self.__name = name
        self.__email = email
        self.__password = password
        self.__number = number

    def get_customer_id(self):
        return self.__customer_id

    def get_name(self):
        return self.__name

    def get_email(self):
        return self.__email

    def get_password(self):
        return self.__password

    def get_number(self):
        return self.__number

    def set_name(self, name):
        self.__name = name

    def set_email(self, email):
        self.__email = email

    def set_password(self, password, confirm_password):
        if password != confirm_password:
            raise ValueError("Password and confirm password do not match")
        self.__password = password

    def set_number(self, number):
        self.__number = number

    def set_customer_id(self, customer_id):
        self.__customer_id = customer_id