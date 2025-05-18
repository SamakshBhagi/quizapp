from flask import *
from flask_sqlalchemy import SQLAlchemy
from database.db import db, User
from database.db import Quiz, Chapter, Subject
from flask_login import *
from collections import defaultdict
authorize = Blueprint('authorize', __name__)

def create_admin():
    with db.session.begin():
        admin = User.query.filter_by(enrollid = '01').all()
        if not admin:
            admin = User(enrollid = '01', naam = 'admin', pwd='admin01', isadmin = True)
            db.session.add(admin)
            db.session.commit()

@authorize.route('/register', methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        pickX = request.form.get('enrollid')
        pickY= request.form.get('naam')
        pickZ = request.form.get('pwd')
        
        if User.query.filter_by(enrollid =pickX).all():
            return redirect(url_for('authorize.logger'))
        else:
            nuser = User(enrollid = pickX, naam = pickY, pwd = pickZ)
            db.session.add(nuser)
            db.session.commit()
            login_user(nuser)
            
            return redirect(url_for('authorize.user_dash', user = nuser))
    return render_template('register.html')

@authorize.route('/login', methods =['GET', 'POST'])
def logger():
    if request.method == 'POST':
        pickX = request.form.get('enrollid')
        pickY = request.form.get('pwd')
        user = User.query.filter_by(enrollid = pickX).first()
        
        if user and user.pwd == pickY:
            login_user(user)
            if user.isadmin:
                return redirect(url_for('authorize.admin_dash', naam = user.naam))
            return redirect(url_for('authorize.user_dash', naam = user.naam, user = user))
        return render_template('logger.html')
    return render_template('logger.html')

@authorize.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authorize.logger'))

@authorize.route('/user_dashboard', methods = ["GET"])
@login_required
def user_dash():
    if current_user.is_authenticated:
        
        quizzes = Quiz.query.all()
        chapters = Chapter.query.all()
        subjects = Subject.query.all()
        
        c_list = {c.chapterid: c for c in chapters}
        s_list = defaultdict(lambda:defaultdict(list))
        
        for q in quizzes:
            c = c_list.get(q.chapterid)
            if c:
                s_list[c.subjectid][c].append(q)
        
        s_names = {s.subjectid: s.naam for s in subjects}
        return render_template('user_dash.html', user = current_user, s_list = s_list, s_names = s_names)       
    
@authorize.route('/admin_dash', methods = [ 'GET', 'POST'])
@login_required
def admin_dash():
    s = Subject.query.all()
    c = Chapter.query.all()
    q = Quiz.query.all()
    u = User.query.all()
    return render_template('admin_dash.html',users = u,subjects=s, chapters=c, quizzes=q, user = current_user)

