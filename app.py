
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Column
from sqlalchemy.types import String, JSON, Boolean

from uuid import uuid4

# Creating the flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = Column(String(128), primary_key=True)
    name = Column(String(128))

class Room(db.Model):
    id = Column(String(128), primary_key=True)
    name = Column(String(128))
    dealer = Column(String(128))
    player = Column(String(128))

class Game(db.Model):
    id = Column(String(128), primary_key=True)
    room = Column(String(128))

    # Status can be one of some options - playing, dealer_won, player_won, tie
    status = Column(String(128))

    # deck of cards, json list containing cards in this fomat: [{suit: "hearts", value: "A"}, ...]
    deck_json = Column(JSON) 
    dealer_hand_json = Column(JSON)
    player_hand_json = Column(JSON)
    current_turn = Column(String(128))

migrate = Migrate(app, db)


@app.route('/room', methods=['POST'])
def create_room():
    # CONNECT DATABASE, create new room
    # create new room in the database
    # return room id
    user_id = 123
    new_room_id = uuid4()
    new_room = Room(id=str(new_room_id), name=f"room-{new_room_id}", dealer=user_id)
    db.session.add(new_room)
    db.session.commit()
    return str(new_room_id)


@app.route('/join/<room_number>', methods=['POST'])
def join_player_to_room(room_number):
    # CONNECT DATABASE, create new room
    # create new room in the database
    # return room id
    user_id = "123"
    room = db.session.query(Room).filter_by(id=room_number).first()
    if room.player is not None:
        return "Room is full", 400
    if room.dealer == user_id:
        return "You are the dealer, you can not join your own room", 400
    room.player = user_id
    db.session.commit()
    return "OK"


@app.route('/start/<room_number>', methods=['POST'])
def start_game(room_number):
    user_id = 123
    # Check if the user is the dealer of this room - TODO: Lilach should implement this

    # Check if the room is full - TODO: Lilach should implement this


    # In case both checks passed, create a new game in the database
    
    room = db.session.query(Room).filter_by(id=room_number).first()
    if room.dealer != user_id:
        return "You are not the dealer", 400
    if room.player is None:
        return "Room is empty", 400
    return "OK"


@app.route('/<test>')
def index(test):
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    print(test)
    # return status code 200
    return test


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


