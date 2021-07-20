from infrastructure import Settlement, Road, City

resources = ['holz', 'lehm', 'schaf', 'getreide', 'stein']
all_resources = [None, 'holz', 'lehm', 'schaf', 'getreide', 'stein', 'wueste', 'alle']

types = [None, Settlement, Road, City]
trades = [None, '2:1', '3:1']

dev_cards = ["monopol", "ritter", "straßenbau", "siegpunkt", "erfindung"]
victory_cards = ["rittermacht", "längste handelsstraße"]

def p_dice(number):
    return 1 / 36 * min(number - 1, 13 - number)