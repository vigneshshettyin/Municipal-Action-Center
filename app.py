from flask import Flask, render_template,request, redirect, session, flash
# TODO: Flash message config & Session setup
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'f9bf78b9a18ce6d46a0cd2b0b86df9da'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///mac.db"
db = SQLAlchemy(app)


class Adminlogin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    lastlogin = db.Column(db.String(12), nullable=True)
    usertype = db.Column(db.String(12), nullable=True)
    gender = db.Column(db.String(12), nullable=True)
    dob = db.Column(db.String(500), nullable=False)
    wardno = db.Column(db.String(500), nullable=False)

class Dashboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(500), nullable=False)


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    subject = db.Column(db.String(80), nullable=False)
    details = db.Column(db.String(500), nullable=False)
    upvote = db.Column(db.Integer, nullable=True)
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
        entry = Adminlogin(phone=mobileno, lastlogin=datetime.now(), email=email, password=password, dob=dob, gender=gender, wardno=wardno, usertype="user")
        db.session.add(entry)
        db.session.commit()
        flash("Registration Successfull", "success")
    return render_template('signup.html')


@app.route('/login', methods = ['GET', 'POST'])
def loginPage():
    # TODO: Check for active session
    if ('logged_in' in session and session['logged_in'] == True):
        return redirect('/viewRequests')
    if (request.method == 'POST'):
        email = request.form.get('email')
        password = request.form.get('password')
        response = Adminlogin.query.filter_by(email=email).first()
        if((response != None) and ( response.email == email ) and ( sha256_crypt.verify(password, response.password )==1) and (response.usertype=="user")):
            updateloginTime = Adminlogin.query.filter_by(email=email).first()
            updateloginTime.lastlogin = datetime.now()
            # TODO:Invoke new session
            session['logged_in'] = True
            session['email'] = email
            session['wardno'] = updateloginTime.wardno
            session['usertype'] = "user"
            db.session.commit()
            return redirect('/viewRequests')
            # TODO:Add a invalid login credentials message using flash
        else:
            # if (response == None or (sha256_crypt.verify(password, response.password) != 1)):
            flash("Invalid Credentials!", "danger")
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/loginadmin', methods = ['GET', 'POST'])
def loginPageadmin():
    if ('logged_in' in session and session['logged_in'] == True):
        return redirect('/adminDashboard')
    if (request.method == 'POST'):
        email = request.form.get('email')
        password = request.form.get('password')
        response = Dashboard.query.filter_by(email=email).first()
        if((response != None) and ( response.email == email ) and ( sha256_crypt.verify(password, response.password )==1)):
            updateloginTime = Adminlogin.query.filter_by(email=email).first()
            updateloginTime.lastlogin = datetime.now()
            # TODO:Invoke new session
            session['logged_in'] = True
            db.session.commit()
            return redirect('/adminDashboard')
    return render_template('login2.html')



@app.route('/adminDashboard', methods = ['GET', 'POST'])
def adminDashboard():
    if ('logged_in' in session and session['logged_in'] == True):
        post = Department.query.filter_by().all()
        return render_template('admindash.html', post=post)
    return redirect('/login')

@app.route("/deleteIssue/<string:id>", methods = ['GET', 'POST'])
def deleteIssue(id):
    if ('logged_in' in session and session['logged_in'] == True):
        deleteIssue = Department.query.filter_by(id=id).first()
        db.session.delete(deleteIssue)
        db.session.commit()
        flash("Issue Deleted Successfully!", "success")
        return redirect('/loginadmin')
    else:
       return redirect('/loginadmin')

@app.route("/view/<string:id>", methods=['GET'])
def viewPage(id):
    if ('logged_in' in session and session['logged_in'] == True):
        post = Department.query.filter_by(id=id).first()
        return render_template('post.html',post=post)
    else:
        return redirect('/loginadmin')


@app.route("/edit/<string:id>", methods = ['GET', 'POST'])
def edit(id):
    if ('logged_in' in session and session['logged_in'] == True):
        if request.method == 'POST':
            statusmessage = request.form.get('editordata')
            post = Department.query.filter_by(id=id).first()
            post.statusmessage = statusmessage
            db.session.commit()
            flash("Post edited Successfully!", "success")
            return redirect('/edit/'+id)
        post = Department.query.filter_by(id=id).first()
        return render_template('edit.html', post=post, id=id)
    return redirect('/loginadmin')


@app.route("/upvote/<string:id>", methods = ['GET', 'POST'])
def upVote(id):
    if ('logged_in' in session and session['logged_in'] == True):
        post = Department.query.filter_by(id=id).first()
        post.upvote = post.upvote + 1
        db.session.commit()
        # flash("Post edited Successfully!", "success")
        return redirect('/login')
    return redirect('/login')


@app.route('/requestPost', methods = ['GET', 'POST'])
def requestPost():
    # TODO: Check for active session
    if ('logged_in' in session and session['logged_in'] == True and (session['usertype'] == "user")):
        response = Department.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html', response=response)
        # TODO:Get all form response from user
    else:
        return redirect('/login')

@app.route('/viewRequests', methods = ['GET', 'POST'])
def viewRequests():
    # TODO: Check for active session
    if ('logged_in' in session and session['logged_in'] == True and (session['usertype'] == "user")):
        post = Department.query.filter_by(wardno=session['wardno'])
        return render_template('upvote.html', post=post)
        # TODO:Get all form response from user
    else:
        return redirect('/login')


@app.route('/submitRequest', methods = ['GET', 'POST'])
def submitRequest():
    if (request.method == 'POST'):
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
        entry = Department(name=name, email=emaild, address=address, zip=zip, city=city, wardno=wardno, subject=subject,
                           details=editordata, statusmessage="Submitted", upvote = 0, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
    return redirect('/requestPost')

# TODO: Destroy session ( Logout Function)

@app.route("/logout")
def logout():
        session.pop('logged_in', None)
        flash("Logged Out Successfully!", "success")
        return redirect('/login')

if __name__ == '__main__':
    app.run()
