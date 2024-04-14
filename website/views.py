from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import User, Pro
from sqlalchemy import func, and_, or_, case
from datetime import datetime, timedelta
from . import db, smart

from fhirclient.models.medicationrequest import MedicationRequest
from fhirclient.models.medicationstatement import MedicationStatement
from fhirclient.models.medication import Medication


def get_patient_list():
    latest_pro = (
        db.session.query(Pro.user_id, func.max(Pro.date).label('max_date')) \
            .group_by(Pro.user_id)\
            .subquery()
        )
    
    
    patient_list = db.session.query(User) \
        .filter_by(role_id=1) \
        .join(latest_pro, latest_pro.c.user_id == User.id, isouter=True) \
        .join(Pro, and_(
                Pro.user_id == User.id,
                Pro.date == latest_pro.c.max_date
            ), isouter=True) \
        .with_entities(
            User.id, 
            User.first_name, 
            User.last_name,
            Pro.date,
            case((or_(Pro.hrsn_1>0, Pro.hrsn_2>0), 'House'), else_='').label('sn1'),
            case((Pro.hrsn_3>0, 'Food'), else_='').label('sn2'),
            case((Pro.hrsn_4>0, 'Transportation'), else_='').label('sn3'),
            case((Pro.hrsn_5>0, 'Finance'), else_='').label('sn4'),
            case((Pro.hrsn_6>0, 'Support'), else_='').label('sn5'),
            (sum([Pro.med_1,Pro.med_2,Pro.med_3,Pro.med_4])*5).label('med')
        )
    
    return patient_list


def get_medications(pid):
    search = MedicationStatement.where(struct={'subject':'Patient/'+pid, 'status':'active'})
    med_resources = search.perform_resources(smart.server)
    
    if not med_resources:
        search = MedicationRequest.where(struct={'subject':'Patient/'+pid, 'status':'active'})
        med_resources = search.perform_resources(smart.server)
    
    med_list = set()
    
    for m in med_resources:
        medication = None
        try:
            med_ref = m.medicationReference.reference.split('/')[1]
            medication = Medication.read(med_ref, smart.server).code.coding[0].display
        except:
            pass
        
        if medication:
            med_list.add(medication)
            continue
        else:
            try:
                medication = m.medicationCodeableConcept.coding[0].display
            except:
                continue
        
        if medication:
            med_list.add(medication)
            
    return list(med_list)


views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    if current_user.role_id == 1:
        try:
            last_update = max([pro.date for pro in current_user.pros])
        except:
            last_update = ''
            
        return render_template("patient_home.html", 
                               user=current_user, 
                               last_update=last_update,
                               med_list = get_medications(current_user.pid))
    
    elif current_user.role_id == 2:
        return render_template("provider_home.html", user=current_user, patient_list=get_patient_list())
    
    return render_template("home.html", user=current_user)



@views.route('/prosurvey', methods=['GET','POST'])
@login_required
def pro_survey():
    if request.method == 'POST':
        pro_ans = [
            request.form.get('hrsnQ1'),
            request.form.getlist('hrsnQ2'),
            request.form.get('hrsnQ3'),
            request.form.get('hrsnQ4'),
            request.form.get('hrsnQ5'),
            request.form.get('hrsnQ6'),
            request.form.get('medQ1'),
            request.form.get('medQ2'),
            request.form.get('medQ3'),
            request.form.get('medQ4')
        ]
        
        flag = True
        for i in range(len(pro_ans)):
            if not pro_ans[i]:
                flash('Question '+str(i+1)+' is blank.', category='error')
                flag = False
                break
        
        if flag:
            new_pro_ans = Pro(
                hrsn_1 = int(pro_ans[0]),
                hrsn_2 = sum([int(r) for r in pro_ans[1]]),
                hrsn_3 = int(pro_ans[2]),
                hrsn_4 = int(pro_ans[3]),
                hrsn_5 = int(pro_ans[4]),
                hrsn_6 = int(pro_ans[5]),
                med_1 = int(pro_ans[6]),
                med_2 = int(pro_ans[7]),
                med_3 = int(pro_ans[8]),
                med_4 = int(pro_ans[9]),
                user_id = current_user.id
            )
            db.session.add(new_pro_ans)
            db.session.commit()
            flash('New PRO Survey submitted!', category='success')
            return redirect(url_for('views.home'))
        
    return render_template("proSurvey.html", user=current_user)


@views.route('/patient_info/<id>')
@login_required
def patient_info(id):
    patient = db.session.query(User) \
        .filter_by(id=id) \
        .with_entities(
            User.id, 
            User.first_name, 
            User.last_name,
            User.pid
        ).first()
        
    pro_start_dtm = datetime.today() - timedelta(days = 180)
    
    patient_pro = db.session.query(Pro) \
        .filter(Pro.user_id==id, Pro.date>=pro_start_dtm )\
        .with_entities(
            Pro.date,
            case((or_(Pro.hrsn_1>0, Pro.hrsn_2>0), 'House'), else_='').label('sn1'),
            case((Pro.hrsn_3>0, 'Food'), else_='').label('sn2'),
            case((Pro.hrsn_4>0, 'Transportation'), else_='').label('sn3'),
            case((Pro.hrsn_5>0, 'Finance'), else_='').label('sn4'),
            case((Pro.hrsn_6>0, 'Support'), else_='').label('sn5'),
            (sum([Pro.med_1,Pro.med_2,Pro.med_3,Pro.med_4])*5).label('med')
        )\
        .order_by(Pro.date)
        
    patient_data = {
            'info': patient,
            'medications': get_medications(patient.pid),
            'pro': patient_pro
        }
    
    return render_template('patient_info.html', user=current_user, patient_data = patient_data)