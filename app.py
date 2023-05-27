
import json
import hashlib
from uuid import uuid4
from functools import wraps

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Column
from sqlalchemy.types import String, JSON, Boolean
from typing import List


from game_logic import Game, Deck, Hand, Card, PlayerType, GameStatus


# Creating the flask app
app = Flask(__name__,
            static_url_path='/static',
            static_folder='assets',)
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

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


migrate = Migrate(app, db)


def authenticated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("here")
        # Check if the Authorization header is present in the request
        token = request.headers.get('Authorization')
        print(f"{type(token)}")
        print(f"{token=}")
        if token:
            db_user: DBUser = db.session.query(
                DBUser).filter_by(token=token).first()

            print(f"{db_user=}")
            if db_user:
                # If the token is valid, pass the user id to the decorated function
                kwargs['user_id'] = db_user.username
                return func(*args, **kwargs)
        # If the token is missing or invalid, return a 401 Unauthorized response
        return jsonify({
            "error": "Unauthorized"
        }), 401

    return wrapper


@app.route('/room/<room_id>', methods=['GET'])
def waiting_room(room_id):
    return render_template('room.html', room_id=room_id)


@app.route('/api/room', methods=['POST'])
@authenticated
def create_room(user_id):
    # CONNECT DATABASE, create new room
    # create new room in the database
    # return room id
    new_room_id = uuid4()
    new_room = DBRoom(id=str(new_room_id),
                      name=f"room-{new_room_id}", dealer=user_id)
    db.session.add(new_room)
    db.session.commit()
    return jsonify({"room_id": str(new_room_id)}), 201


@app.route('/api/room/<room_id>', methods=['GET'])
@authenticated
def waiting_room_data(room_id, user_id):
    # CONNECT DATABASE, get the game
    # return the game
    if room_id is None:
        return jsonify({
            "error": "Room not found"
        }), 404
    db_room: DBRoom = db.session.query(DBRoom).filter_by(id=room_id).first()
    if db_room is None:
        return jsonify({
            "error": "Room not found"
        }), 404
    if user_id not in [db_room.dealer, db_room.player]:
        return jsonify({
            "error": "You are not part of this room"
        }), 400

    return jsonify({
        "room_id": room_id,
        "dealer_id": db_room.dealer,
        "player_id": db_room.player,
        "user_id": user_id
    }), 200


@app.route('/api/room/status/<room_id>', methods=['GET'])
@authenticated
def waiting_room_status(room_id, user_id):
    # Check if there is a game in this room
    db_game: DBGame = db.session.query(
        DBGame).filter_by(room=room_id).first()
    if db_game is None:
        return jsonify({
            "status": "Game not started"
        }), 200
    else:
        return jsonify({
            "status": "Game started"
        }), 200


@app.route('/api/join/<room_id>', methods=['POST'])
@authenticated
def join_player_to_room(room_id, user_id):
    # CONNECT DATABASE, create new room
    # create new room in the database
    # return room id
    room: DBRoom = db.session.query(DBRoom).filter_by(id=room_id).first()
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


@app.route('/api/start/<room_id>', methods=['POST'])
@authenticated
def start_game(room_id, user_id):
    # Check if the user is the dealer of this room by quering the db
    room: DBRoom = db.session.query(DBRoom).filter_by(id=room_id).first()
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
        DBGame).filter_by(room=room_id).first()
    if db_game is not None:
        return jsonify({
            "error": "Game is already in progress"
        }), 400

    # Create a new game in the database
    game = Game(str(uuid4()), Deck())

    game.start()
    status = game.check_status()

    # store the game in the database
    new_db_game = DBGame(id=str(game.game_id), room=room_id,
                         game_data=json.dumps(game.to_json()))
    db.session.add(new_db_game)
    db.session.commit()

    return status.name


def get_player_type_from_id_and_room(user_id, db_room: DBRoom):
    return PlayerType.DEALER if db_room.dealer == user_id else PlayerType.PLAYER


@app.route('/game/<room_id>', methods=['GET'])
def game(room_id):
    return render_template('game.html', room_id=room_id)


@app.route('/api/game/status/<room_id>', methods=['GET'])
@authenticated
def get_game_status(room_id, user_id):
    """This function should return the player who quried it the following things:
    1. The current player turn/ if the game is over it should return the winner.
    2. Current hands of both players.
    Note: If the game didn't finish yet: if the player is the player then he should not get the first card of the dealer

    Keyword arguments:
    room_id -- the room number

    Return: the table state
    """

    # Check if the room exists
    room: DBRoom = db.session.query(DBRoom).filter_by(id=room_id).first()
    if room is None:
        return jsonify({
            "error": "Room does not exist"
        }), 400

    # Check if the user is the dealer of this room by quering the db
    db_room: DBRoom = db.session.query(
        DBRoom).filter_by(id=room_id).first()
    if user_id not in [db_room.dealer, db_room.player]:
        return jsonify({
            "error": "You are not part of this room"
        }), 400

    # Check if there is already a game in this room
    db_game: DBGame = db.session.query(
        DBGame).filter_by(room=room_id).first()
    if db_game is None:
        return jsonify({
            "error": "No game in progress"
        }), 400

    current_player_type = get_player_type_from_id_and_room(user_id, db_room)

    game: Game = Game.from_json(json.loads(db_game.game_data))
    status: GameStatus = game.check_status()

    response = {
        "this_player": user_id,
        "other_player": db_room.player if user_id == db_room.dealer else db_room.dealer,
        "status": status.name
    }

    if status == GameStatus.PLAYING:
        if user_id == db_room.player:
            return jsonify({
                **response,
                "this_player_hand": game.player_hand.to_json(),
                "other_player_hand": game.dealer_hand.get_visable_cards(),
            })
        else:
            return jsonify({
                **response,
                "this_player_hand": game.dealer_hand.to_json(),
                "other_player_hand": game.player_hand.to_json(),
            })
    else:
        return jsonify({
            "dealer_hand": game.dealer_hand.to_json(),
            "player_hand": game.player_hand.to_json(),
        })


@app.route('/api/turn/<room_id>', methods=['POST'])
@authenticated
def make_turn(room_id, user_id):
    """This function should make a turn for the player who quried it.
    Parameters:
    action - Can be one of: HIT/STAND.


    Keyword arguments:
    room_id -- The room number of the game.
    Return: 
    Success/Failure message.
    """

    # Check if the room exists
    db_room: DBRoom = db.session.query(
        DBRoom).filter_by(id=room_id).first()
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
        DBGame).filter_by(room=room_id).first()
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


# region admin

# Shold be deleted
@app.route('/admin/flip_turn/<room_id>', methods=['POST'])
def flip_turn(room_id):
    # load the game from the database
    db_game: DBGame = db.session.query(
        DBGame).filter_by(room=room_id).first()
    game = Game.from_json(json.loads(db_game.game_data))

    game.current_player = PlayerType.PLAYER if game.current_player == PlayerType.DEALER else PlayerType.DEALER

    # store the game in the database
    db_game.game_data = json.dumps(game.to_json())
    db.session.commit()

    return "OK"

# Should be deleted
# Return all of the games and their data


@app.route('/admin/games', methods=['GET'])
def get_games():
    db_games: List[DBGame] = db.session.query(DBGame).all()
    return jsonify([db_game.as_dict() for db_game in db_games])


@app.route('/admin/add-token/<user_id>', methods=['GET'])
def add_token(user_id):
    token = 3 * str(uuid4())
    db_user: DBUser = db.session.query(DBUser).filter_by(id=user_id).first()
    db_user.token = token
    db.session.commit()
    return jsonify({
        "token": token
    })


@app.route('/admin/<test>')
def index(test):
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    print(test)
    # return status code 200
    return test

# endregion admin


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
                "error": "This username is already taken"
            }), 409
        elif email_result:
            return jsonify({
                "error": "This email is already exists"
            }), 409

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        token = 3 * str(uuid4())
        new_user = DBUser(id=str(uuid4()), username=username,
                          hashed_password=hashed_password, email=email, token=token)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "token": token
        }), 201

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']

        # will be none if not in database, else exists
        user_result: DBUser = db.session.query(
            DBUser).filter_by(username=username).first()

        if user_result is None:
            return jsonify({
                "error": "This username does not exist"
            }), 400

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user_result.hashed_password != hashed_password:
            return jsonify({
                "error": "Wrong password"
            }), 400

        return jsonify({
            "token": user_result.token
        }), 200

    return render_template('login.html')


@app.route('/api/user', methods=['GET'])
def get_user():
    headers = request.headers
    token = headers.get('Authorization')

    if token is None:
        return jsonify({
            "error": "No token, please login"
        }), 400
    else:
        user = db.session.query(DBUser).filter_by(token=token).first()
        if user is None:
            return jsonify({
                "error": "Invalid token"
            }), 400
        else:
            return jsonify({
                "username": user.username,
                "email": user.email
            }), 200


@app.route('/', methods=['GET'])
def home_page():
    return render_template('home.html')

# @app.route('/login', methods=['POST', 'GET'])
# def signup():
#     return render_template('login.html')
