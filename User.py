# User class
from flask_login import  UserMixin
class User(UserMixin):
    count_id = 0

    # initializer method
    def __init__(self, first_name, last_name, gender, membership, remarks , phone_number , email, password = None, is_admin=True):
        User.count_id += 1
        self.__user_id = User.count_id
        self.__first_name = first_name
        self.__last_name = last_name
        self.__gender = gender
        self.__membership = membership
        self.__remarks = remarks
        self.__phone_number = phone_number
        self.__email = email
        self.__password = password
        self.__is_admin = is_admin

    def get_name(self):
        """Returns full name (first and last name)"""
        return f"{self.__first_name} {self.__last_name}"


    # accessor methods
    def get_id(self):
        return str(self.__user_id)

    def get_password(self):
        return self.__password

    def is_admin(self):
        return self.__is_admin

    def get_user_id(self):
        return self.__user_id

    def get_first_name(self):
        return self.__first_name

    def get_last_name(self):
        return self.__last_name

    def get_gender(self):
        return self.__gender

    def get_membership(self):
        return self.__membership

    def get_remarks(self):
        return self.__remarks

    def get_phone_number(self):
        return self.__phone_number

    def get_email(self):
        return self.__email.lower()

    # mutator methods
    def set_user_id(self, user_id):
        self.__user_id = user_id

    def set_first_name(self, first_name):
        self.__first_name = first_name

    def set_last_name(self, last_name):
        self.__last_name = last_name

    def set_gender(self, gender):
        self.__gender = gender

    def set_membership(self, membership):
        self.__membership = membership

    def set_remarks(self, remarks):
        self.__remarks = remarks

    def set_phone_number(self,phone_number):
        self.__phone_number = phone_number

    def set_email(self,email):
        self.__email = email

    def set_password(self, password):
        self.__password = password

    def set_admin(self, is_admin):
        self.__is_admin = is_admin


    def set_password(self, password):
        self.__password = password

    def set_admin(self, is_admin):
        self.__is_admin = is_admin