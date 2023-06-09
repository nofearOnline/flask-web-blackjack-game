import json
import random
import enum
from typing import List


class PlayerType(enum.Enum):
    DEALER = 0
    PLAYER = 1


def toggle_player_type(player_type):
    if player_type == PlayerType.DEALER:
        return PlayerType.PLAYER
    return PlayerType.DEALER


class GameStatus(enum.Enum):
    PLAYING = 0
    FORMAL_END = 1
    PLAYER_WON = 2
    DEALER_WON = 3
    TIE = 4


class HandStatus(enum.Enum):
    NOT_STAND = 0
    STAND = 1


class Action(enum.Enum):
    HIT = 0
    STAND = 1


class Card:
    def __init__(self, rank, suit, visible_for_player=True, value=None):
        self.rank = rank
        self.suit = suit
        self.visible_for_player = visible_for_player

    @classmethod
    def from_json(cls, json_dict):
        return cls(json_dict['rank'], json_dict['suit'], json_dict['visible_for_player'])

    def __str__(self):
        return f"{self.rank} of {self.suit}."

    def to_json(self):
        return {"rank": self.rank, "suit": self.suit, "visible_for_player": self.visible_for_player}

    def __repr__(self):
        return self.to_json()


class Deck:
    ranks = ("1", "2", "3", "4", "5", "6", "7", "8",
             "9", "10", "jack", "queen", "king")
    suits = ("spade", "club", "heart", "diamond")

    def __init__(self, shuffle=True):
        self.cards = [Card(rank, suit)
                      for rank in self.ranks for suit in self.suits]
        if shuffle:
            self.shuffle_deck()

    @classmethod
    def from_json(cls, json_dict):
        deck = Deck(shuffle=False)
        deck.cards = [Card.from_json(card_json) for card_json in json_dict]
        return deck

    def shuffle_deck(self):
        random.shuffle(self.cards)

    def deal(self, visible_for_player=True):
        if self.cards:
            card = self.cards.pop()
            card.visible_for_player = visible_for_player
            return card
        return None

    def to_json(self):
        return [card.to_json() for card in self.cards]


class Hand:

    vaules = {
        "1": 11,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "10": 10,
        "jack": 10,
        "queen": 10,
        "king": 10,
    }

    def __init__(self, cards: List[Card], status=HandStatus.NOT_STAND):
        self.cards = cards
        self.status = status

    @classmethod
    def from_json(cls, hand_dict):
        hand = cls([Card.from_json(card_json)
                   for card_json in hand_dict["cards"]], HandStatus(hand_dict['status']))
        return hand

    def add_card(self, card):
        self.cards.append(card)

    def sum_score(self):
        total = 0
        ace_count = sum(card.rank == "1" for card in self.cards)
        for card in self.cards:
            total += self.vaules[card.rank]

        while total > 21 and ace_count > 0:
            total -= 10
            ace_count -= 1
        return total

    def get_visable_cards(self):
        return {"cards": [card.to_json() if card.visible_for_player else Card("hidden", "").to_json() for card in self.cards], "status": self.status.value}

    def to_json(self):
        return {"cards": [card.to_json() for card in self.cards], "status": self.status.value}


class Game:
    def __init__(self, game_id, deck):
        self.game_id: str = game_id
        self.deck: Deck = deck
        self.player_hand: Hand = Hand([])
        self.dealer_hand: Hand = Hand([])
        self.status: GameStatus = GameStatus.PLAYING
        self.current_player: PlayerType = PlayerType.DEALER

    # Load game from a json string
    @classmethod
    def from_json(cls, json_dict):
        deck = Deck.from_json(json_dict['deck'])
        game = cls(json_dict['id'], deck)
        game.player_hand = Hand.from_json(json_dict['player_hand'])
        game.dealer_hand = Hand.from_json(json_dict['dealer_hand'])
        game.status = GameStatus(json_dict['status'])
        game.current_player = PlayerType(json_dict['current_player'])
        return game

    def start(self):
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal(visible_for_player=False))
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())

    def turn(self, current_player_type, action):
        """This function is the logic of a turn in the game
        There are a lot of cases and in each case the function should do different things:

        # TODO Lilach: add all of the possible cases

        Keyword arguments:
        current_player_type -- The current player who is playing
        action -- The action that the player wants to do
        Return: Error/None
        """

        turn_moved = True
        # Check if it is the player's turn
        if self.current_player != current_player_type:
            return "Not your turn"

        if action == Action.HIT.name:
            if current_player_type == PlayerType.PLAYER:
                if self.player_hand.status == HandStatus.STAND:
                    return "You standed so you can't hit"
                if self.dealer_hand.status == HandStatus.STAND:
                    turn_moved = False
                self.player_hand.add_card(self.deck.deal())
            else:
                if self.dealer_hand.status == HandStatus.STAND:
                    return "You standed so you can't hit"
                if self.player_hand.status == HandStatus.STAND:
                    turn_moved = False
                self.dealer_hand.add_card(self.deck.deal())
        elif action == Action.STAND.name:
            if current_player_type == PlayerType.PLAYER:
                self.player_hand.status = HandStatus.STAND
            else:
                self.dealer_hand.status = HandStatus.STAND

        if self.player_hand.status == HandStatus.STAND and self.dealer_hand.status == HandStatus.STAND:
            self.status = GameStatus.FORMAL_END

        if turn_moved:
            self.current_player = toggle_player_type(self.current_player)

    # This function checks if the game is over, only in case
    def check_status(self) -> GameStatus:
        if self.player_hand.sum_score() > 21:
            self.status = GameStatus.DEALER_WON
        elif self.dealer_hand.sum_score() > 21:
            self.status = GameStatus.PLAYER_WON
        elif self.status == GameStatus.FORMAL_END:
            self.status = self.check_who_won()
        return self.status

    def check_who_won(self) -> GameStatus:
        player_score = self.player_hand.sum_score()
        dealer_score = self.dealer_hand.sum_score()

        # Only one player can get more score than 21 each round
        if player_score > 21:
            return GameStatus.DEALER_WON
        elif dealer_score > 21:
            return GameStatus.PLAYER_WON
        elif player_score > dealer_score:
            return GameStatus.PLAYER_WON
        elif player_score < dealer_score:
            return GameStatus.DEALER_WON
        else:
            return GameStatus.TIE

    def to_json(self):
        return {"id": self.game_id, "deck": self.deck.to_json(), "player_hand": self.player_hand.to_json(), "dealer_hand": self.dealer_hand.to_json(), "status": self.status.value, "current_player": self.current_player.value}
