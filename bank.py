import resources
from cards import DevCardDeck
import copy

class Bank:
    def __init__(self):
        self.resources = dict.fromkeys(resources.resources, 19)
        self.dev_cards = DevCardDeck()

    def get_dev_card(self, player):
        dev_card = self.dev_cards.get_dev_card()
        self.pay("schaf", 1, player)
        self.pay("getreide", 1, player)
        self.pay("stein", 1, player)
        return dev_card

    def take(self, resource, amount, player):
        # in case the bank doesnt have enough of the resource
        if amount > self.resources[resource]:
            amount = self.resources[resource]
        player.resources[resource] += amount
        self.resources[resource] -= amount

    def pay(self, resource, amount, player):
        player.resources[resource] -= amount
        self.resources[resource] += amount

    def pay_for_road(self, player):
        self.pay("holz", 1, player)
        self.pay("lehm", 1, player)

    def pay_for_settlement(self, player):
        self.pay("holz", 1, player)
        self.pay("lehm", 1, player)
        self.pay("schaf", 1, player)
        self.pay("getreide", 1, player)

    def pay_for_city(self, player):
        self.pay("getreide", 2, player)
        self.pay("stein", 3, player)