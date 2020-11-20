from flask import Flask, render_template,request, redirect, session, flash
# TODO: Flash message config & Session setup
from flask_sqlalchemy import SQLAlchemy
# from werkzeug.utils import secure_filename
from passlib.hash import sha256_crypt
from datetime import datetime
# import json
# import os


app = Flask(__name__)
app.secret_key = 'f9bf78b9a18ce6d46a0cd2b0b86df9da'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/bytecodevelocity"
db = SQLAlchemy(app)


class Adminlogin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    lastlogin = db.Column(db.String(12), nullable=True)
    userType = db.Column(db.String(12), nullable=True)
    gender = db.Column(db.String(12), nullable=True)
    dob = db.Column(db.String(500), nullable=False)
    wardno = db.Column(db.String(500), nullable=False)


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    subject = db.Column(db.String(80), nullable=False)
    details = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    wardno = db.Column(db.String(80), nullable=False)
    zip = db.Column(db.String(80), nullable=False)
    statusmessage = db.Column(db.String(150), nullable=False)
    date = db.Column(db.String(12), nullable=True)

# TODO: Register route to be written

@app.route('/')
def homePage():
    return render_template('index.html')


@app.route('/register', methods = ['GET', 'POST'])
def registerPage():
    # TODO: Check for active session
    if ('logged_in' in session and session['logged_in'] == True):
        return redirect('/requestPost')
    if(request.method=='POST'):
        email = request.form.get('emailid')
        password = sha256_crypt.encrypt(request.form.get('password'))
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        mobileno = request.form.get('mobileno')
        wardno = request.form.get('wardno')
        entry = Adminlogin(phone=mobileno, lastlogin=datetime.now(), email=email, password=password, dob=dob, gender=gender, wardno=wardno, userType="user")
        db.session.add(entry)
        db.session.commit()
        session['logged_in'] = True
        flash("Registration Successfull", "success")
    return render_template('signup.html')


@app.route('/login', methods = ['GET', 'POST'])
def loginPage():
    # TODO: Check for active session
    if ('logged_in' in session and session['logged_in'] == True):
        return redirect('/requestPost')
    if (request.method == 'POST'):
        email = request.form.get('email')
        password = request.form.get('password')
        response = Adminlogin.query.filter_by(email=email).first()
        if((response != None) and ( response.email == email ) and ( sha256_crypt.verify(password, response.password )==1)):
            updateloginTime = Adminlogin.query.filter_by(email=email).first()
            updateloginTime.lastlogin = datetime.now()
            # TODO:Invoke new session
            session['logged_in'] = True
            session['email'] = email
            db.session.commit()
            return redirect('/requestPost')
            # TODO:Add a invalid login credentials message using flash
        else:
            # if (response == None or (sha256_crypt.verify(password, response.password) != 1)):
            flash("Invalid Credentials!", "danger")
            return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/requestPost', methods = ['GET', 'POST'])
def requestPost():
    # TODO: Check for active session
    if('logged_in' in session and session['logged_in'] == True):
        response = Department.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html', response=response)
        # TODO:Get all form response from user
        response = Department.query.filter_by(email=session['email']).all()
        return render_template('dashboard.html', response=response)
    else:
        return redirect('/')

@app.route('/submitRequest', methods = ['GET', 'POST'])
def submitRequest():
    if(request.method == 'POST'):
        name = request.form.get('name')
        print(name)
        emaild = request.form.get('email')
        address = request.form.get('address')
        city = request.form.get('city')
        wardno = request.form.get('wardno')
        zip = request.form.get('zip')
        subject = request.form.get('subject')
        editordata = request.form.get('editordata')
        print(editordata)
        entry = Department(name=name, email=emaild, address=address, zip=zip, city=city, wardno=wardno, subject=subject, details=editordata, statusmessage="Submitted", date=datetime.now())
        db.session.add(entry)
        db.session.commit()
    return redirect('/requestPost')

@app.route("/logout")
def logout():
        session.pop('email')
        session.pop('logged_in')
        flash("Logged Out Successfully!", "success")
        return redirect('/login')

if __name__ == '__main__':
    app.run()
