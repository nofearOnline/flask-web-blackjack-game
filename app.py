
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Column
from sqlalchemy.types import String, JSON, Boolean
import json

from game_logic import Game, Deck, Hand, Card, PlayerType, GameStatus

from uuid import uuid4

# Creating the flask app
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class DBUser(db.Model):
    id = Column(String(128), primary_key=True)
    name = Column(String(128))


class DBRoom(db.Model):
    id = Column(String(128), primary_key=True)
    name = Column(String(128))
    dealer = Column(String(128))
    player = Column(String(128))


class DBGame(db.Model):
    id = Column(String(128), primary_key=True)
    room = Column(String(128))
    game_data = Column(JSON)


migrate = Migrate(app, db)


@app.route('/room', methods=['POST'])
def create_room():
    # CONNECT DATABASE, create new room
    # create new room in the database
    # return room id
    user_id = "123"
    new_room_id = uuid4()
    new_room = DBRoom(id=str(new_room_id),
                      name=f"room-{new_room_id}", dealer=user_id)
    db.session.add(new_room)
    db.session.commit()
    return str(new_room_id)


@app.route('/join/<room_number>', methods=['POST'])
def join_player_to_room(room_number):
    # CONNECT DATABASE, create new room
    # create new room in the database
    # return room id
    user_id = "234"
    room: DBRoom = db.session.query(DBRoom).filter_by(id=room_number).first()
    if room.player is not None:
        return "Room is full", 400
    if room.dealer == user_id:
        return "You are the dealer, you can not join your own room", 400
    room.player = user_id
    db.session.commit()
    return "OK"

# This function should start a new game in the room. Should return
# 1. If the game is over it should return the winner.
# Should store the new game in the database


@app.route('/start/<room_number>', methods=['POST'])
def start_game(room_number):
    user_id = "123"
    # Check if the user is the dealer of this room by quering the db
    room: DBRoom = db.session.query(DBRoom).filter_by(id=room_number).first()
    if room.dealer != user_id:
        return "You are not the dealer", 400

    # Check if the room is full
    if room.player is None:
        return "Room does not contain two players, please invite someone else", 400

    # Check if there is already a game in this room
    db_game: DBGame = db.session.query(
        DBGame).filter_by(room=room_number).first()
    if db_game is not None:
        return "Game is already in progress", 400

    # Create a new game in the database
    game = Game(str(uuid4()), Deck())

    game.start()
    status = game.check_status()

    # store the game in the database
    new_db_game = DBGame(id=str(game.game_id), room=room_number,
                         game_data=json.dumps(game.to_json()))
    db.session.add(new_db_game)
    db.session.commit()

    return status

# This function should return the player who quried it the following things:
# 1. The current player turn/ if the game is over it should return the winner.
# 2. Current hands of both players.
# Note: If the game didn't finish yet: if the player is the player then he should not get the first card of the dealer


@app.route('/status/<room_number>', methods=['GET'])
def get_game_status(room_number):
    user_id = "123"

    # Check if the room exists
    room: DBRoom = db.session.query(DBRoom).filter_by(id=room_number).first()
    if room is None:
        return "Room does not exist", 400

    # Check if the user is the dealer of this room by quering the db
    db_room: DBRoom = db.session.query(
        DBRoom).filter_by(id=room_number).first()
    if user_id not in [db_room.dealer, db_room.player]:
        return "You are not part of this room", 400

    # Check if there is already a game in this room
    db_game: DBGame = db.session.query(
        DBGame).filter_by(room=room_number).first()
    if db_game is None:
        return "No game in progress", 400

    current_player_type = PlayerType.DEALER if db_room.dealer == user_id else PlayerType.PLAYER

    game: Game = Game.from_json(json.loads(db_game.game_data))
    status: GameStatus = game.check_status()

    if status == GameStatus.PLAYING:
        return jsonify({
            "current_player": game.current_player.name,
            "dealer_hand": game.dealer_hand.get_visable_cards() if current_player_type == PlayerType.PLAYER else game.dealer_hand.to_json(),
            "player_hand": game.player_hand.to_json(),
            "status": status.name
        })
    else:
        return jsonify({
            "dealer_hand": game.dealer_hand.to_json(),
            "player_hand": game.player_hand.to_json(),
            "status": status.name
        })


@app.route('/test/<test>')
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
