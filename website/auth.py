import re
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from . import db, smart
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

from fhirclient.models.patient import Patient

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        pwd = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            if check_password_hash(user.password, pwd):
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password.', category='error')
        else:
            flash('Account does not exist.', category='error')
    
    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():
    
    def valid_identity(fname, lname, dob, pid):
        try:
            patient = Patient.read(pid, smart.server)
            """
            with open('testOutput.txt','w') as f:
                f.write("patient found")
            """
        except:
            """
            with open('testOutput.txt','w') as f:
                f.write("patient not found")
            """
            return False
        
        if patient.birthDate.isostring != dob:
            return False
        
        pat_name = patient.name[0].as_json()
        
        try:
            pat_lname = pat_name['family'].strip().capitalize()
            pat_fname = pat_name['given'][0].strip().capitalize()
        except:
            return False
        
        if pat_fname!=fname or pat_lname!=lname:
            return False
        return True
    
    
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        fname = request.form.get('firstName').strip().capitalize()
        lname = request.form.get('lastName').strip().capitalize()
        dob = request.form.get('birthday').strip()
        pid = request.form.get('ID').strip()
        pwd1 = request.form.get('password1')
        pwd2 = request.form.get('password2')
        
        if len(email) < 4:
            flash('Invalid email address.', category='error')
        elif len(fname)*len(lname)==0:
            flash('Invalid first name or last name.', category='error')
        elif not re.search("^\d{4}-\d{2}-\d{2}$",dob):
            flash('Date of birth must be in yyyy-mm-dd format.', category='error')
        elif not valid_identity(fname, lname, dob, pid):
            flash('We are unable to find your record. Please contact your healthcare facility.', category='error')
        elif pwd1 != pwd2:
            flash('Passwords do not match.', category='error')
        elif len(pwd1) < 8:
            flash('Password must be at least 8 characters.', category='error')
        else:
            new_patient = User(
                pid=pid,
                prov_id=None,
                email=email, 
                first_name=fname,
                last_name=lname,
                password=generate_password_hash(pwd1, method='sha256'),
                role_id = 1
            )
            db.session.add(new_patient)
            db.session.commit()
            flash('Account created!', category='success')
            login_user(new_patient, remember=True)
            return redirect(url_for('views.home'))
        
    return render_template("signUp.html", user=current_user)