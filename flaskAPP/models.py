from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, uid, first_name, last_name, gender, dob, contact_number, email, address):
        self.__uid = uid
        self.__first_name = first_name
        self.__last_name = last_name
        self.__gender = gender
        self.__dob = dob
        self.__contact_number = contact_number
        self.__email = email
        self.__address = address
        self.__specialisation=''

    def get_id(self):
        return self.__uid

    def get_name(self):
        return self.__first_name + " " + self.__last_name

    def get_gender(self):
        return self.__gender

    def get_dob(self):
        return self.__dob

    def get_contact_number(self):
        return self.__contact_number

    def get_email(self):
        return self.__email

    def get_address(self):
        return self.__address

    def get_specialisation(self):
        return self.__specialisation

    def is_doctor(self):
        return self.__uid.startswith("D") and len(self.__uid) == 4

    def is_admin(self):
        return self.__uid.startswith("A") and len(self.__uid) == 4
