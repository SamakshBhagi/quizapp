from flask import *
from database.db import *
from flask_login import *
import matplotlib.pyplot as plotter
import io, base64

process = Blueprint("process", __name__)

#search functionality

@process.route('/find_quiz')
def dhoondo_quiz():
    s_id = request.args.get('s_id')
    c_id = request.args.get('c_id')
    kya = request.args.get('ise')
    s = Subject.query.get(s_id)
    c = Chapter.query.get(c_id)
    if not (c or s):
        return render_template('search_quiz.html', quizzes = [], chapter = c, subject=s )
    quizzes = Quiz.query.filter(Quiz.naam.ilike(f'%{kya}%'), Quiz.chapterid == c_id).all()
    return render_template('search_quiz.html', quizzes = quizzes, chapter = c, subject = s)
    

@process.route('/delete_user/<int:uid>', methods = ['GET'])
def delete_user(uid):
    if current_user.isadmin:
        u = User.query.get(uid)
        db.session.delete(u)
        db.session.commit()
        return redirect(url_for('authorize.admin_dash'))    

@process.route('/add_subject', methods = ["POST"])
def add_subject():
    s = request.form.get('s_name')
    if Subject.query.filter_by(naam = s).first():
        return redirect(url_for('authorize.admin_dash'))
    newsub = Subject(naam = s)
    db.session.add(newsub)
    db.session.commit()
    
    return redirect(url_for('authorize.admin_dash'))

@process.route('/add_chapter', methods= ["POST"])
def add_chapter():
    s_id = request.form.get('s_id')
    c = request.form.get('c_name')
    if Chapter.query.filter_by(naam= c).first():
        return redirect(url_for('authorize.admin_dash'))
    newchap = Chapter(naam = c, subjectid = s_id)
    db.session.add(newchap)
    db.session.commit()
    
    return redirect(url_for('authorize.admin_dash'))

@process.route('/add_quiz', methods= ["POST"])
def add_quiz():
    c_id = request.form.get('c_id')
    q = request.form.get('q_name')
    newqz = Quiz(naam = q, chapterid = c_id)
    db.session.add(newqz)
    db.session.commit()
    
    return redirect(url_for('authorize.admin_dash'))

#quiz manipulation
@process.route('/edit_subject/<int:s_id>', methods = ['GET', 'POST'])
def edit_subject(s_id):
    if request.method == 'GET':
        s = Subject.query.get(s_id)
        print(s.naam)
        return render_template('edit_subject.html', subject =s)
    else:
        newsubnaam = request.form.get('s_name')
        s = Subject.query.get(s_id)
        s.naam = newsubnaam
        db.session.commit()
        return redirect(url_for('authorize.admin_dash'))

@process.route('/delete_subject/<int:s_id>', methods = ['GET'])
def pop_subject(s_id):
    s = Subject.query.get(s_id)
    db.session.delete(s)
    db.session.commit()
    return redirect(url_for('authorize.admin_dash'))


@process.route('/edit_chapter/<int:c_id>', methods = ['GET', 'POST'])
def edit_chapter(c_id):
    if request.method == 'GET':
        c= Chapter.query.get(c_id)
        print(c.naam)
        return render_template('edit_chapter.html', chapter =c)
    else:
        newchapnaam = request.form.get('c_name')
        c = Chapter.query.get(c_id)
        c.naam = newchapnaam
        db.session.commit()
        return redirect(url_for('authorize.admin_dash'))

@process.route('/delete_chapter/<int:c_id>', methods = ['GET'])
def pop_chapter(c_id):
    c = Chapter.query.get(c_id)
    db.session.delete(c)
    db.session.commit()
    return redirect(url_for('authorize.admin_dash'))


@process.route('view_quizzes/<int:c_id>', methods = ['GET','POST,'])
def view_quizzes(c_id):
    chapter = Chapter.query.get_or_404(c_id)
    return render_template('quiz_list.html', chapter=chapter, quizzes=chapter.quizzes)

@process.route('/quiz_detail/<int:qz_id>', methods = ['GET','POST'])
def quiz_detail(qz_id):    
    q = Quiz.query.get(qz_id)
    return render_template('quiz_detail.html', quiz=q)

@process.route('/delete_quiz/<int:qz_id>', methods= ['GET', 'POST'])
def pop_quiz(qz_id):
    q = Quiz.query.get(qz_id)
    c = Chapter.query.filter_by(chapterid = q.chapterid).first()
    db.session.delete(q)
    db.session.commit()
    print(c.naam)
    return render_template('quiz_list.html', quiz = q, chapter= c)


# questions
@process.route('/append_page/<int:qz_id>', methods = ['GET','POST'])
def append_page(qz_id):
    q = Quiz.query.get(qz_id) 
    return render_template('append_quiz.html', quiz = q)

@process.route('/append_question/<int:qz_id>', methods = ['GET','POST'])
def append_question(qz_id):
    q = Quiz.query.get(qz_id)
    qtext = request.form.get('q_text')
    a=  request.form.get('opt_a')
    b=  request.form.get('opt_b')
    c=  request.form.get('opt_c')
    d=  request.form.get('opt_d')
    corr = request.form.get('correct_opt')
    
    qs = Question(quizid = qz_id, q_text=qtext,opt_a= a, opt_b = b,opt_c = c,opt_d = d, correct_opt = corr)
    db.session.add(qs)
    db.session.commit()
    
    return redirect(url_for('process.append_page', qz_id = qz_id))

@process.route('/pop_question/<int:qs_id>', methods = ['GET', 'POST'])
def pop_question(qs_id):
    qs = Question.query.get(qs_id)
    db.session.delete(qs)
    db.session.commit()
    return redirect(url_for('process.quiz_detail', qz_id = qs.quizid))

@process.route('/edit_page/<int:qs_id>', methods = ['GET'])
def edit_page(qs_id):
    qs = Question.query.get(qs_id)
    q = Quiz.query.get(qs.quizid)
    return render_template('edit_question.html', question = qs, quiz= q)

@process.route('/edit_question/<int:qs_id>', methods = ['GET','POST'])
def edit_question(qs_id):
    qs = Question.query.get(qs_id)
    qtext = request.form.get('q_text')
    a=  request.form.get('opt_a')
    b=  request.form.get('opt_b')
    c=  request.form.get('opt_c')
    d=  request.form.get('opt_d')
    corr = request.form.get('correct_opt')
    
    qs.q_text = qtext
    qs.opt_a = a
    qs.opt_b = b
    qs.opt_c = c
    qs.opt_d = d
    qs.correct_opt = corr
    db.session.commit()
    
    return redirect(url_for('process.quiz_detail', qz_id = qs.quizid ))

# attempt quiz

@process.route('/attempt_quiz/<int:qz_id>', methods = ['GET'])
def attempt_quiz(qz_id):
    q = Quiz.query.get(qz_id)
    return render_template('attempt_quiz.html', quiz = q, user= current_user)

@process.route('/score_calc/<int:qz_id>', methods = ['POST'])
def score_calc(qz_id):
    q = Quiz.query.get(qz_id)
    correct_answers = {question.questionid: question.correct_opt for question in q.questions}
    score = 0
    total_questions = len(correct_answers)
    
    for k, v in request.form.items():
        if k.startswith("answers["):
            questionid = int(k[8:-1])
            if correct_answers.get(questionid) == v:
                score += 1
    
    #create plot
    a,b = plotter.subplots()
    
    labels = 'Correct','Wrong'
    sizes = [score, total_questions- score]
    rang = ['green', 'red']
    explode = (0.1,0)
    
    b.pie(sizes, explode = explode, labels = labels, colors = rang, autopct ='%d%%', shadow = True)
    b.set_aspect('equal')
    
    img = io.BytesIO()
    plotter.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    if current_user.is_authenticated:
        user_id = current_user.userid
        oldcount = Score.query.filter_by(userid= user_id).order_by(Score.attemptno.desc()).first()
        newcount = (oldcount.attemptno + 1) if oldcount else 1
        
        
        total_score = Score(userid=current_user.userid, quizid=qz_id, score=score, attemptno = newcount)
        
        db.session.add(total_score)
        db.session.commit() 
        allscores = Score.query.filter_by(userid = user_id).order_by(Score.attemptno.asc()).all()


    return render_template('quiz_summary.html', score=score, total=total_questions,img_data = img_base64, scores = allscores,quiz=q)

@process.route('/dhoondo_user', methods = ['GET'])
def dhoondo_user():
    u_name = request.args.get('u_name')
    users = User.query.filter(User.naam.ilike(f'%{u_name}%')).all()
    return render_template('users_found.html', users = users)

@process.route('/user_tracking/<int:u_id>')
def user_tracking(u_id):
    u = User.query.get(u_id)
    
    netscores = Score.query.all()
    net = 0
    total = 0
    
    for score in netscores:
        net +=score.score
    netavg = net/len(netscores) if netscores else 0
    
    userscores = Score.query.filter_by(userid = u_id).all()
    for score in userscores:
        total+=score.score
    useravg = total/len(userscores) if userscores else 0
    
    #bar chart code
    '''fig,ax = plotter.subplots()
    x_label = ["Total Average Score", f"{u.naam}'s Average"]
    scores = [netavg,useravg]
    
    ax.bar(x_label, scores,  alpha = 0.7,color = ["red","blue"])
    
    ax.set_ylabel("Score")
    ax.legend()
    
    img = io.BytesIO()
    plotter.savefig(img, format = 'png')
    img_base64 =base64.b64encode(img.getvalue()).decode('utf-8')

    return render_template('user_tracked.html',avg = useravg, userid = u_id, netavg = netavg, img = img_base64,user = u)'''
    a,b = plotter.subplots()
    
    labels = 'Total Average Score','User Average'
    sizes = [netavg,useravg]
    rang = ['green', 'red']
    explode = (0.1,0)
    
    b.pie(sizes, explode = explode, labels = labels, colors = rang, autopct ='%d%%', shadow = True)
    b.set_aspect('equal')
    b.patch.set_facecolor('lightgreen')
    img = io.BytesIO()
    plotter.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    return render_template('user_tracked.html', avg = useravg, userid = u_id, netavg = netavg, img = img_base64,user = u)

    