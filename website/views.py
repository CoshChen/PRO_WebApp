from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Pro
from . import db

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    if current_user.role_id == 1:
        return render_template("patient_home.html", user=current_user)
    elif current_user.role_id == 2:
        return render_template("provider_home.html", user=current_user)
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