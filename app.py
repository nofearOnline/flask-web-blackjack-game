
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from uuid import uuid4

# Creating the flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.String(128), primary_key=True)
    name = db.Column(db.String(128))

class Room(db.Model):
    id = db.Column(db.String(128), primary_key=True)
    name = db.Column(db.String(128))


@app.route('/room', methods=['POST'])
def create_room():
    # CONNECT DATABASE, create new room
    # create new room in the database
    # return room id
    new_room_id = uuid4()
    new_room = Room(id=str(new_room_id), name=f"room-{new_room_id}")
    db.session.add(new_room)
    db.session.commit()
    return str(new_room_id)





@app.route('/')
def index():
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    # return status code 200
    return "OK"


# @app.route('/signup', methods=['POST', 'GET'])
# def signup():
#     if request.form == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         email = request.form.get('email')
#         print(username, password,email)

#         #will be none if not in database, else exists
#         user_result = db.session.query(User).filter_by(usenmae=username).first()
#         email_result = db.session.query(User).filter_by(email=email).first()


#         if user_result:
#             return "User already registered"
#         elif email_result:
#             return "Email already registered"
        
#         hashed_password = hashlib.sha256(password.encode()).hexdigest()
#         user_name = User(username=username, password=hashed_password, email=email)
#         db.session.add(new_user)
#         db.session.commit()

#         return "OK"



#     return render_template('signup.html')


# @app.route('/login', methods=['POST', 'GET'])
# def signup():
#     return render_template('login.html')



# if __name__ == '__main__':
#     app.run(debug=True)
#     # users = db.session.query(User).all()
#     #user_to_delete = users[0]
#     #session.delete(user_to_delete)
#     #db.session.commit()
