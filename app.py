
import json
import hashlib
from uuid import uuid4

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Column
from sqlalchemy.types import String, JSON, Boolean


from game_logic import Game, Deck, Hand, Card, PlayerType, GameStatus


# Creating the flask app
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class DBUser(db.Model):
    id = Column(String(128), primary_key=True)
    username = Column(String(128))
    hashed_password = Column(String(128))
    email = Column(String(128))
    token = Column(String(128))


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
    if room is None:
        return jsonify({
            "error": "Room not found"
        }), 404
    if room.player is not None:
        return jsonify({
            "error": "Room is full"
        }), 400
    if room.dealer == user_id:
        return jsonify({
            "error": "You are the dealer, you can not join your own room"
        }), 400
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
        return jsonify({
            "error": "You are not the dealer"
        }), 400

    # Check if the room is full
    if room.player is None:
        return jsonify({
            "error": "Room does not contain two players, please invite someone else"
        }), 400

    # Check if there is already a game in this room
    db_game: DBGame = db.session.query(
        DBGame).filter_by(room=room_number).first()
    if db_game is not None:
        return jsonify({
            "error": "Game is already in progress"
        }), 400

    # Create a new game in the database
    game = Game(str(uuid4()), Deck())

    game.start()
    status = game.check_status()

    # store the game in the database
    new_db_game = DBGame(id=str(game.game_id), room=room_number,
                         game_data=json.dumps(game.to_json()))
    db.session.add(new_db_game)
    db.session.commit()

    return status.name


def get_player_type_from_id_and_room(user_id, db_room: DBRoom):
    return PlayerType.DEALER if db_room.dealer == user_id else PlayerType.PLAYER


@app.route('/status/<room_number>', methods=['GET'])
def get_game_status(room_number):
    """This function should return the player who quried it the following things:
    1. The current player turn/ if the game is over it should return the winner.
    2. Current hands of both players.
    Note: If the game didn't finish yet: if the player is the player then he should not get the first card of the dealer

    Keyword arguments:
    room_number -- the room number

    Return: the table state
    """

    user_id = "123"

    # Check if the room exists
    room: DBRoom = db.session.query(DBRoom).filter_by(id=room_number).first()
    if room is None:
        return jsonify({
            "error": "Room does not exist"
        }), 400

    # Check if the user is the dealer of this room by quering the db
    db_room: DBRoom = db.session.query(
        DBRoom).filter_by(id=room_number).first()
    if user_id not in [db_room.dealer, db_room.player]:
        return jsonify({
            "error": "You are not part of this room"
        }), 400

    # Check if there is already a game in this room
    db_game: DBGame = db.session.query(
        DBGame).filter_by(room=room_number).first()
    if db_game is None:
        return jsonify({
            "error": "No game in progress"
        }), 400

    current_player_type = get_player_type_from_id_and_room(user_id, db_room)

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


@app.route('/turn/<room_number>', methods=['POST'])
def make_turn(room_number):
    """This function should make a turn for the player who quried it.
    Parameters:
    action - Can be one of: HIT/STAND.


    Keyword arguments:
    room_number -- The room number of the game.
    Return: 
    Success/Failure message.
    """
    user_id = "123"

    # Check if the room exists
    db_room: DBRoom = db.session.query(
        DBRoom).filter_by(id=room_number).first()
    if db_room is None:
        return jsonify({
            "error": "Room does not exist"
        }), 400

    # Check if the user is in the room
    if user_id not in [db_room.dealer, db_room.player]:
        return jsonify({
            "error": "You are not part of this room"
        }), 400

    # Check if there is a game in this room
    db_game: DBGame = db.session.query(
        DBGame).filter_by(room=room_number).first()
    if db_game is None:
        return jsonify({
            "error": "No game in progress"
        }), 400

    current_player_type = get_player_type_from_id_and_room(user_id, db_room)
    game = Game.from_json(json.loads(db_game.game_data))

    error = game.turn(current_player_type, json.loads(request.data)["action"])
    if error is not None:
        return jsonify({
            "error": error
        }), 400

    # Update the game in the database
    db_game.game_data = json.dumps(game.to_json())
    db.session.commit()

    return "OK"


# Shold be deleted
@app.route('/flip_turn/<room_number>', methods=['POST'])
def flip_turn(room_number):
    # load the game from the database
    db_game: DBGame = db.session.query(
        DBGame).filter_by(room=room_number).first()
    game = Game.from_json(json.loads(db_game.game_data))

    game.current_player = PlayerType.PLAYER if game.current_player == PlayerType.DEALER else PlayerType.DEALER

    # store the game in the database
    db_game.game_data = json.dumps(game.to_json())
    db.session.commit()

    return "OK"


@app.route('/test/<test>')
def index(test):
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    print(test)
    # return status code 200
    return test


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        print(username, password, email)

        # will be none if not in database, else exists
        user_result = db.session.query(
            DBUser).filter_by(username=username).first()
        email_result = db.session.query(DBUser).filter_by(email=email).first()

        if user_result:
            return jsonify({
                "error": "User already registered"
            }), 409
        elif email_result:
            return jsonify({
                "error": "Email already registered"
            }), 409

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        token = 3 * str(uuid4())
        new_user = DBUser(id=str(uuid4()), username=username,
                          hashed_password=hashed_password, email=email, token=token)
        db.session.add(new_user)
        db.session.commit()

        return token

    return render_template('signup.html')


@app.route('/', methods=['GET'])
def home_page():
    return render_template('home.html')

# @app.route('/login', methods=['POST', 'GET'])
# def signup():
#     return render_template('login.html')
