import random

class DevCard:
    def __init__(self, content):
        self.content = content
        self.played = False
        self.play_protection = True

    def __repr__(self):
        return f"{self.content}({self.played * 1}, {self.play_protection * 1})"

class DevCardDeck:
    def __init__(self):
        self.dev_cards = self.create_card_deck()

    def get_dev_card(self):
        if len(self.dev_cards) == 0:
            return None
        return self.dev_cards.pop()

    def create_card_deck(self):
        dev_cards = self.make_dev_cards()
        random.shuffle(dev_cards)
        return dev_cards

    def make_dev_cards(self):
        dev_cards = []
        for _ in range(2):
            dev_cards.append(DevCard("monopol"))
        for _ in range(14):
            dev_cards.append(DevCard("ritter"))
        for _ in range(2):
            dev_cards.append(DevCard("straßenbau"))
        for _ in range(4):
            dev_cards.append(DevCard("siegpunkt"))
        for _ in range(2):
            dev_cards.append(DevCard("erfindung"))
        
        return dev_cards      