# main script to start the server

from flask import *
from database.db import *
from database.authorize import authorize, create_admin
from database.routes import *
from flask_login import *
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "supersecret"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "authorize.logger"  

# Will return --None-- if invalid IDR
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) # id is pkey of user

db.init_app(app)

@app.route('/')
def landing():
    return render_template("landing_page.html")

# import and setup other python scripts
from database.authorize import authorize
app.register_blueprint(authorize, url_prefix="/authorize")

from database.routes import process
app.register_blueprint(process, url_prefix="/route")


#reset 
@app.route('/reset', methods = ['GET'])
def reset():
    db.drop_all()
    db.create_all()
    create_admin()
    return redirect(url_for('authorize.admin_dash'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
        create_admin()   
    app.run(debug=True)