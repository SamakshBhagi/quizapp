# here I've built the ORM for database. Total 6 Models - 
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from flask_login import UserMixin   

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    userid = db.Column(db.Integer,primary_key = True, autoincrement = True)
    enrollid= db.Column(db.String(10), unique = True)
    naam = db.Column(db.String(45))
    pwd = db.Column(db.String(20))
    isadmin = db.Column(db.Boolean, default = False)
    scores = db.relationship('Score', back_populates='user', cascade= "all,delete-orphan", lazy=True)
    def get_id(self):
        return str(self.userid) # worked well with flask_login to get the user 

class Subject(db.Model):
    __tablename__ = 'subjects'
    subjectid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    naam = db.Column(db.String(100))
    chapters = db.relationship('Chapter', cascade="all, delete-orphan", back_populates='subject')

class Chapter(db.Model):
    __tablename__ = 'chapters'
    chapterid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject  = db.relationship('Subject', back_populates='chapters')
    quizzes = db.relationship('Quiz', back_populates='chapter', cascade="all, delete-orphan")  
    naam = db.Column(db.String(100))
    subjectid = db.Column(db.Integer, db.ForeignKey('subjects.subjectid', ondelete="CASCADE"))

class Quiz(db.Model):
    __tablename__ = 'quiz'  
    quizid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    naam = db.Column(db.String(100))
    scores = db.relationship('Score', back_populates = 'quiz',cascade ="all,delete-orphan", lazy=True)
    chapter = db.relationship('Chapter', back_populates='quizzes')  
    questions = db.relationship('Question', back_populates='quiz', cascade="all, delete-orphan")
    chapterid = db.Column(db.Integer, db.ForeignKey('chapters.chapterid', ondelete="CASCADE"))
    

class Question(db.Model):
    __tablename__ = 'questions'
    questionid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quizid = db.Column(db.Integer, db.ForeignKey('quiz.quizid', ondelete="CASCADE"), nullable=False)  
    q_text = db.Column(db.String(255))
    opt_a = db.Column(db.String(100))
    opt_b = db.Column(db.String(100))
    opt_c = db.Column(db.String(100))
    opt_d = db.Column(db.String(100))
    correct_opt = db.Column(db.String(1))

    quiz = db.relationship('Quiz', back_populates='questions')


class Score(db.Model):
    __tablename__ = 'scores'
    #one primary key, rest needed to relate and connect things :)
    scoreid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.userid', ondelete="CASCADE"), nullable=False)
    quizid = db.Column(db.Integer, db.ForeignKey('quiz.quizid', ondelete="CASCADE"), nullable=False)
    score = db.Column(db.Integer)
    user = db.relationship('User', back_populates='scores')
    attemptno = db.Column(db.Integer, nullable = False, default =1)
    quiz = db.relationship('Quiz', back_populates='scores')
