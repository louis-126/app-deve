from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from flask_mail import Mail, Message
from validation import *
from models import User
from itsdangerous import URLSafeTimedSerializer
import shelve,qns
from forms import ContactForm, FAQ, SearchBar

app = Flask(__name__)
app.config['SECRET_KEY'] = '7711d8a9e5973bcda814c99dbafcd7d6'

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = "flaskapptest123@gmail.com"
app.config["MAIL_PASSWORD"] = "flaskapp123"
app.config["DEFAULT_MAIL_SENDER"] = "flaskapptest123@gmail.com"

login_manager = LoginManager()
login_manager.init_app(app)

mail = Mail(app)


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECRET_KEY'])


def confirm_token(token, expiration=300):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECRET_KEY'],
            max_age=expiration
        )
    except:
        return False
    return email


# Checks that the database is present and creates one if it is missing
db = shelve.open('storage.db', flag='c', writeback=True)
# Create doctor and admin accounts
db["users"] = {}
db["appointment"] = {}
db["applicant"] = {}
users_db = db["users"]
users_db["D001"] = {
    "first_name": "David",
    "last_name": "Tan",
    "gender": "M",
    "dob": "1976-06-05",
    "contact_number": "91234567",
    "email": "davidtan@gmail.com",
    "address": "514 Chai Chee Lane #06-03",
    "password": generate_password_hash("david"),
    "appointments": {
        "2021-01-02 2:20 PM": {"nric": "S9422476Z", "name": "Song Hao", "gender": "M", "dob": "1994-02-21"},
        "2021-01-02 3:20 PM": {"nric": "S7766747F", "name": "Yang Xuan", "gender": "F", "dob": "1977-15-09"}
    }
}
users_db["A001"] = {
    "first_name": "Chloe",
    "last_name": "Soh",
    "gender": "F",
    "dob": "1988-09-15",
    "contact_number": "89345565",
    "email": "chloesoh@gmail.com",
    "address": "71 Sultan Gate",
    "password": generate_password_hash("chloe")
}
users_db["T0392511G"] = {
    "first_name": "Daniel",
    "last_name": "Jack",
    "gender": "M",
    "dob": "1999-10-22",
    "contact_number": "90996565",
    "email": "xinmingsm11@gmail.com",
    "address": "71 Sultan Gate",
    "password": generate_password_hash("daniel")
}
db.close()


# Function required by flask-login to reload user from database, using their UID or NRIC
@login_manager.user_loader
def load_user(uid):
    with shelve.open('storage.db') as db:
        if uid not in db["users"]:
            return None
        else:
            info = db["users"][uid]
            user = User(uid, info["first_name"], info["last_name"], info["gender"], info["dob"],
                        info["contact_number"], info["email"], info["address"])
        return user


@app.route('/')
def home():
    return render_template("home.html")


#louis code from here
@app.route('/contactus',methods=['GET','POST'])
def contactus():
    form = ContactForm()
    if form.validate_on_submit():
        flash(f'You have successfully submitted the form. Please wait 2-3 working days for reply and also check your email.Thank you.','success')
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        enquiries = request.form['enquiries']
        msg = Message(subject,
                          sender=app.config.get("MAIL_USERNAME"),
                          recipients=[email],
                          body="Hi "+name+ ',\n\n Thanks a lot for getting in touch with us. \n \n This is an automatic email just to let you know that we have received your enquiries.\n\n'
                               'This is the message that you sent.\n'  +  enquiries )
        mail.send(msg)
        return redirect(url_for('contactus'))
    return render_template('contactus.html', title='Contact Us', form=form)

@app.route('/faq', methods=['GET', 'POST'])
def create_faq():
    create_faq = FAQ(request.form)
    if request.method == 'POST' and create_faq.validate():
        qn_dict = {}
        db = shelve.open('faqstorage.db', 'c')
        try:
            qn_dict = db['FAQ']
        except:
            print("Error in retrieving Questions from storage.db.")

        question = qns.FAQ(create_faq.question.data, create_faq.answer.data,
                         create_faq.date.data)
        qn_dict[question.get_qns_id()] = question
        db['FAQ'] = qn_dict

        db.close()

        return redirect(url_for('create_faq'))
    return render_template('faq.html', form=create_faq)

@app.route('/retrieveQns', methods=['GET','POST'])
def retrieve_qns():
    search = SearchBar(request.form)
    if request.method == 'POST':
        db = shelve.open('faqstorage.db', 'r')
        qns_dict = db['FAQ']
        db.close()

        qns_list = []
        for key in qns_dict:
            question = qns_dict.get(key)
            if search.search.data.lower() in question.get_question().lower():
                qns_list.append(question)


        return render_template('retrieveQns.html', count=len(qns_list), qn_list=qns_list, form=search)

    qn_dict = {}
    db = shelve.open('faqstorage.db', 'r')
    qn_dict = db['FAQ']
    db.close()

    qn_list = []
    for key in qn_dict:
        question = qn_dict.get(key)
        qn_list.append(question)

    return render_template('retrieveQns.html',count=len(qn_list),qn_list=qn_list, form=search)

@app.route('/updateQns/<int:id>/', methods=['GET', 'POST'])
def update_qns(id):
    update_faq_form = FAQ(request.form)
    if request.method == 'POST' and update_faq_form.validate():
        db = shelve.open('faqstorage.db', 'w')
        qn_dict = db['FAQ']

        question = qn_dict.get(id)
        question.set_question(update_faq_form.question.data)
        question.set_answer(update_faq_form.answer.data)
        question.set_date(update_faq_form.date.data)

        db['FAQ'] = qn_dict
        db.close()

        return redirect(url_for('retrieve_qns'))
    else:
        qn_dict = {}
        db = shelve.open('faqstorage.db', 'r')
        qn_dict = db['FAQ']
        db.close()

        question = qn_dict.get(id)
        update_faq_form.question.data = question.get_question()
        update_faq_form.answer.data = question.get_answer()
        update_faq_form.date.data = question.get_date()

        return render_template('updateQns.html', form=update_faq_form)

@app.route('/deleteQns/<int:id>', methods=['POST'])
def delete_qns(id):
    qn_dict = {}
    db = shelve.open('faqstorage.db', 'w')
    qn_dict = db['FAQ']

    qn_dict.pop(id)

    db['FAQ'] = qn_dict
    db.close()

    return redirect(url_for('retrieve_qns'))
#upto here

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        authenticated = True
        error = ""
        db = shelve.open('storage.db')
        user_db = db["users"]
        if not validate_nric(request.form["nric"]) and request.form["nric"] in user_db:
            error += "Invalid NRIC\n"
            authenticated = False
        db.close()

        if not validate_name(request.form["first_name"]) or not validate_name(request.form["last_name"]):
            error += "Invalid name\n"
            authenticated = False

        if request.form["gender"] not in ["M", "F"]:
            error += "Invalid gender\n"
            authenticated = False

        if not validate_email(request.form["email"]):
            error += "Invalid email\n"
            authenticated = False

        if not validate_contact_number(request.form["contact_number"]):
            error += "Invalid contact number\n"
            authenticated = False

        if not validate_text(request.form["address"]):
            error += "Invalid address"
            authenticated = False

        if not validate_password(request.form["password"], request.form["confirm_password"]):
            error += "Passwords do not match\n"
            authenticated = False

        if authenticated:
            db = shelve.open('storage.db', flag='w')
            user_db = db["users"]
            user_db[request.form["nric"]] = {
                "first_name": request.form["first_name"],
                "last_name": request.form["last_name"],
                "gender": request.form["gender"],
                "dob": request.form["dob"],
                "contact_number": request.form["contact_number"],
                "email": request.form["email"],
                "address": request.form["address"],
                "password": generate_password_hash(request.form["password"])
            }
            db.close()

            flash("Successful registration")

            user = load_user(request.form["nric"])
            login_user(user)

            return redirect(url_for("home"))

        flash(error, "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        db = shelve.open('storage.db')
        user_db = db["users"]
        print(db)
        error = ""
        authenticated = True
        if not validate_nric(request.form["nric"]) and request.form["nric"] not in user_db:
            error += "Invalid NRIC or no account associated with NRIC"
            authenticated = False
        else:
            pwdhash = user_db[request.form["nric"]]["password"]
            if not check_password_hash(pwdhash, request.form["password"]):
                error += "Incorrect password"
                authenticated = False
        db.close()

        if authenticated:
            user = load_user(request.form["nric"])
            login_user(user)
            return redirect(url_for('home'))

        flash(error, "error")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        authenticated = True
        error = ""
        if not validate_email(request.form["email"]):
            error += "Invalid email\n"
            authenticated = False
        if not validate_contact_number(request.form["contact_number"]):
            error += "Invalid date of birth\n"
            authenticated = False
        if not validate_text(request.form["address"]):
            error += "Invalid address\n"
            authenticated = False

        if authenticated:
            db = shelve.open('storage.db', flag="w", writeback=True)
            user_db = db["users"]
            user_db[current_user.get_id()]["email"] = request.form["email"]
            user_db[current_user.get_id()]["contact_number"] = request.form["contact_number"]
            user_db[current_user.get_id()]["address"] = request.form["address"]
            db.close()

            flash("Successfully updated profile")
            return render_template("profile.html")

        flash(error, "error")

    return render_template("profile.html")


@app.route('/change_password', methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        authenticated = True
        error = ""
        db = shelve.open('storage.db')
        user_db = db["users"]
        pwdhash = user_db[current_user.get_id()]["password"]
        db.close()
        if not check_password_hash(pwdhash, request.form["old_password"]):
            authenticated = False
            error += "Password Incorrect\n"

        if not validate_password(request.form["new_password"], request.form["confirm_password"]):
            authenticated = False
            error += "Passwords to not match"

        if authenticated:
            db = shelve.open("storage.db", flag="w", writeback=True)
            user_db = db["users"]
            duser_dbb[current_user.get_id()]["password"] = generate_password_hash(request.form["new_password"])
            db.close()

            flash("Successfully updated password")
            return redirect(url_for('home'))

        flash(error, "error")
    return render_template('change_password.html')


@app.route('/all_users')
@login_required
def admin_all_users():
    if current_user.is_admin():
        all_users = []
        db = shelve.open('storage.db')
        user_db = db["users"]
        all_uid = []
        for uid in user_db.keys():
            if uid != current_user.get_id():
                all_uid.append(uid)
        db.close()
        for uid in all_uid:
            temp = load_user(uid)
            all_users.append(temp)
        return render_template("all_users.html", all_users=all_users)

    flash("Access denied", "error")
    return redirect(url_for('home'))


@app.route('/appointments')
@login_required
def appointments():
    if current_user.is_doctor():
        db = shelve.open("storage.db")
        user_db = db["users"]
        appointments = user_db[current_user.get_id()]["appointments"]
        db.close()
        return render_template("appointments.html", appointments=appointments)
    flash("Access denied", "error")
    return redirect(url_for("home"))


@app.route('/admin_update/<uid>', methods=["GET", "POST"])
@login_required
def admin_update(uid):
    if current_user.is_admin():
        if request.method == "POST":
            db = shelve.open("storage.db", flag="w", writeback=True)
            user_db = db["users"]
            user_db[uid]["email"] = request.form["email"]
            user_db[uid]["contact_number"] = request.form["contact_number"]
            user_db[uid]["address"] = request.form["address"]
            if request.form["password"] != "":
                user_db[uid]["password"] = generate_password_hash(request.form["password"])
            db.close()
            flash("Successfully updated")

        user = load_user(uid)
        return render_template("admin_update.html", user=user)
    else:
        flash("Access denied", "error")
        return redirect(url_for("home"))


@app.route('/admin_delete/<uid>', methods=["GET"])
@login_required
def admin_delete(uid):
    if current_user.is_admin():
        db = shelve.open('storage.db')
        user_db = db["users"]
        del user_db[uid]
        db.close()
        flash("Successfully deleted user")
        return redirect(url_for('admin_all_users'))
    else:
        flash("Access denied", "error")
        return redirect(url_for('home'))


@app.route('/add_doctor', methods=["GET", "POST"])
@login_required
def add_doctor():
    if current_user.is_admin():
        if request.method == "POST":
            authenticated = True
            error = ""
            db = shelve.open('storage.db')
            user_db = db["users"]
            if not validate_nric(request.form["nric"]) and request.form["nric"] in user_db:
                error += "Invalid NRIC\n"
                authenticated = False
            db.close()

            if not validate_name(request.form["first_name"]) or not validate_name(request.form["last_name"]):
                error += "Invalid name\n"
                authenticated = False

            if request.form["gender"] not in ["M", "F"]:
                error += "Invalid gender\n"
                authenticated = False

            if not validate_email(request.form["email"]):
                error += "Invalid email\n"
                authenticated = False

            if not validate_contact_number(request.form["contact_number"]):
                error += "Invalid contact number\n"
                authenticated = False

            if not validate_text(request.form["address"]):
                error += "Invalid address"
                authenticated = False

            if not validate_password(request.form["password"], request.form["confirm_password"]):
                error += "Passwords do not match\n"
                authenticated = False

            if authenticated:
                db = shelve.open('storage.db', flag='w')
                user_db = db["users"]
                user_db[request.form["nric"]] = {
                    "first_name": request.form["first_name"],
                    "last_name": request.form["last_name"],
                    "gender": request.form["gender"],
                    "dob": request.form["dob"],
                    "contact_number": request.form["contact_number"],
                    "email": request.form["email"],
                    "address": request.form["address"],
                    "password": generate_password_hash(request.form["password"])
                }
                db.close()

                flash("Successful registration")

            if error:
                flash(error, "error")
        return render_template("add_doctor.html")
    else:
        flash("Access denied", "error")
        return redirect(url_for('home'))


@app.route('/reset_password', methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        authenticated = True
        error = ""
        if not validate_email(request.form["email"]):
            authenticated = False
            error += "Invalid email"

        if authenticated:
            db = shelve.open("storage.db")
            user_db = db["users"]
            for key, value in user_db.items():
                if request.form["email"] == value["email"]:
                    token = generate_confirmation_token(request.form["email"])
                    msg = Message(subject="Password reset", recipients=[request.form["email"]],
                                  body="Link to reset password : http://127.0.0.1:4444{}. Link valid for only 5 minutes"\
                                  .format(url_for("confirm_reset", token=token)), sender="flaskapptest123@gmail.com")
                    mail.send(msg)
                    break
            db.close()

            flash("Successfully entered email, if you have registered an account with us, a reset password email would"
                  " be sent to your email")

            return redirect(url_for("home"))

    return render_template("reset_password.html")


@app.route('/confirm_reset/<token>', methods=["GET", "POST"])
def confirm_reset(token):
    if request.method == "POST":
        if validate_password(request.form["password"], request.form["confirm_password"]):
            db = shelve.open("storage.db", flag="w", writeback=True)
            user_db = db["users"]
            for key, value in user_db.items():
                if value["email"] == session["reset_email"]:
                    value["password"] = generate_password_hash(request.form["password"])
                    flash("Successfully reset password")
                    return redirect(url_for("login"))

        flash("Invalid password")
        return render_template("new_password.html")

    else:
        email = confirm_token(token)
        if email:
            session["reset_email"] = email
            return render_template("new_password.html", token=token)
        else:
            flash("Token expired, please try again")
            return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True, port=4444)