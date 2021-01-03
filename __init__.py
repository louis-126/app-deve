from flask import Flask, render_template, request, url_for, flash, redirect
from forms import ContactForm
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfe280ba245'

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME":'',
    "MAIL_PASSWORD": ''
}

app.config.update(mail_settings)
mail = Mail(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

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

if __name__ == '__main__':
    app.run()

