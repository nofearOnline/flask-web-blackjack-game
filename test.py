from game_logic import Game, Deck

game = Game("123", Deck())
game.start()

# load game fron json
game_json = game.to_json()
game2 = Game.from_json(game_json)

print(game2.to_json())
