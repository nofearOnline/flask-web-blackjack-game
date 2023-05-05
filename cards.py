import json
import random


class Card:
    def __int__(self, rank, suit, visible = True, value=None):
        self.rank = rank
        self.suit = suit
        self.visible = visible
        self.value = value


    def __str__(self):
        return f"{self.rank} of {self.suit}. Value: {self.value}"
    

class Deck:
    ranks = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
    suits = ("♠", "♣", "♥", "♦")
    values = {}


    def __init__(self, game_name, shuffle=True):
        self.game_name = game_name
        self.values = self.get_card_values_from_json()

        if not self.values:
            raise NameError(f'{self.game_name} is not valid name!')
        
        self.cards = [Card(rank, suit, value=self.values.get(rank)) for rank in self.ranks for suit in self.suits]
        if shuffle:
            self.shuffle_deck()

    def get_card_values_from_json(self):
        with open('card_values_by_game.json', 'r') as file:
            values = json.load(file) 
            game_values = values.get(self.game_name)
        return game_values


    def shuffle_using_random(self):
        random.shuffle(self.cards)


    def deal(self):
        if self.cards:
            return self.cards.pop()
        return None

    # #user return card to package
    # def take_card_from_player(self, card_to_add):
    #     self.card.insert(0, card_to_add)


class Hand:
    def __init__(self, player_id):
        self.player_id = player_id
        self.cards = []
        self.score = 0 #at the begining

    def take_card(self, card:Card):
        if isinstance(card, Card):
            self.cards.append(card)

    def drop_card(self, idx:int) -> Card:
        if len(self.cards)> idx:
            return self.cards.pop(idx)
        else:
            raise ValueError(f'{idx} not in range of 0 - {len(self.cards) - 1}')


    def sum_score(self):
        total = 0
        try:
            for card in self.cards:
                total += card.value
        except (TypeError, AttributeError):
            return None
        else:
            self.score = total

    def hand_value_blackjack(self):
        hand_value = sum_score()
        if hand_value > 21 and any(card.rank == "A" for card in self.cards):
            hand_value -=10 #ace will become 1
        return hand_value



class Game:
    def __init__(self):
        self.deck = Deck()
        self.palyer_hand = Hand()
        self.dealer_hand = Hand()
        self.player_turn = True
        

    def deal_initial_cards(self):
        self.player_hand.add_card(self.deck.draw())
        self.dealer_hand.add_card(self.deck.draw())
        self.player_hand.add_card(self.deck.draw())
        self.dealer_hand.add_card(self.deck.draw())  


    def player_hit(self):
        self.player_hand.add_card(self.deck.draw())
        if self.player_hand.value()>21:
            self.player_turn = False

    def dealer_turn(self):
        while self.dealer_hand.value()<17:
            self.dealer_hand.add_card(self.deck.draw())


    def determine_winner(self):
        player_value = self.palyer_hand.value()
        dealer_value = self.dealer_hand.value() 
        if player_value > 21:
            return "Dealer wins!"
        elif dealer_value > 21:
            return "Player wins!"
        elif player_value > dealer_value:
            return"Player wins!"
        elif player_value < dealer_value:
            return"Dealer wins!"
        else:
            return "Tie!"
        
        def play(self):
            self.deck.shuffle()
            self.deal_initial_cards()
            while self.player_turn:
                if self.player_hand.value() == 21:
                    self.player_turn = False
                elif self.player_hand.value() > 21:
                    self.player_turn = False






if __name__ == '__main__':
    d=Deck("blackJack", shuffle = True)


    
