from flask import Flask, render_template, request, url_for, flash, redirect
from forms import ContactForm, FAQ, SearchBar
from flask_mail import Mail, Message

import shelve,qns

app = Flask(__name__)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfe280ba245'

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME":'louisgoh239@gmail.com',
    "MAIL_PASSWORD": ''
}

app.config.update(mail_settings)
mail = Mail(app)

@app.route('/')
def home():
    return render_template('home.html')

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
        db = shelve.open('storage.db', 'c')
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
        db = shelve.open('storage.db', 'r')
        qns_dict = db['FAQ']
        db.close()

        qns_list = []
        start_qns_list = []
        contain_qns_list = []
        for key in qns_dict:
            question = qns_dict.get(key)
            if search.search.data.lower() in question.get_question().lower():
                print('yes')
                qns_list.append(question)


        return render_template('retrieveQns.html', count=len(qns_list), qn_list=qns_list, form=search)

    qn_dict = {}
    db = shelve.open('storage.db', 'r')
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
        db = shelve.open('storage.db', 'w')
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
        db = shelve.open('storage.db', 'r')
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
    db = shelve.open('storage.db', 'w')
    qn_dict = db['FAQ']

    qn_dict.pop(id)

    db['FAQ'] = qn_dict
    db.close()

    return redirect(url_for('retrieve_qns'))

if __name__ == '__main__':
    app.run()

