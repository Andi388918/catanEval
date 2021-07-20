
import math
import copy
from collections import defaultdict

def probability(number):
    x = 1 / 36 * min(number - 1, 13 - number)
    return x * 12 / 7

def calculate_expected_payoff(targets, income_per_round):
    expected_payoff = {}
    for target, value in targets.items():
        if value == 0:
            expected_payoff[target] = 0
        else:
            if target in income_per_round:
                expected_payoff[target] = value / income_per_round[target]
            else:
                expected_payoff[target] = math.inf

    return expected_payoff

def road_buildable(targets, roads_built_counter):
    return targets["lehm"] > 1 and targets["holz"] > 1 and roads_built_counter < 15

def try_trade(trades, resource, freed_resources, targets, roads_built_counter, incomes_per_round):
    trading_amount = 0
    if resource in trades:  trading_amount = 2
    elif "3:1" in trades:   trading_amount = 3
    else:   trading_amount = 4

    if freed_resources[resource] >= trading_amount and resource != "fisch":
        expected_payoff = calculate_expected_payoff(targets, incomes_per_round)
        max_expected_payoff = max(expected_payoff, key=expected_payoff.get)
        freed_resources[resource] -= trading_amount
        targets[max_expected_payoff] = max(0, targets[max(expected_payoff, key=expected_payoff.get)] - 1)
    
    if "fisch" in freed_resources:
        expected_payoff = calculate_expected_payoff(targets, incomes_per_round)
        max_expected_payoff = max(expected_payoff, key=expected_payoff.get)
        if freed_resources["fisch"] >= 5 and max_expected_payoff in ["holz", "lehm"] and road_buildable(targets, roads_built_counter):
            freed_resources["fisch"] -= 5
            targets["holz"] -= 1
            targets["lehm"] -= 1
            roads_built_counter += 1
        elif freed_resources["fisch"] >= 4:
            if not road_buildable(targets, roads_built_counter):
                freed_resources["fisch"] -= 4
                targets[max_expected_payoff] = max(0, targets[max(expected_payoff, key=expected_payoff.get)] - 1)

    return roads_built_counter

def evaluate(income, trades, targets = {"lehm": 20, "holz": 20, "getreide": 13, "schaf": 5, "stein": 12}, verbose = False):

    targets = copy.copy(targets)

    rounds = 0

    incomes_per_round = {}

    # calculate income per round

    for resource, numbers in income.items():
        value = 0
        for number in numbers:
            value += probability(number)
        incomes_per_round[resource] = value

    freed_resources = {}

    # move and recalculate fish

    if "fisch" in incomes_per_round:
        incomes_per_round["fisch"] *= 11 / 6
        freed_resources["fisch"] = 0

    roads_built_counter = 0

    while sum(targets.values()) > 0:

        rounds += 1

        for resource, value in freed_resources.items():
            freed_resources[resource] += incomes_per_round[resource]

            roads_built_counter = try_trade(trades, resource, freed_resources, targets, roads_built_counter, incomes_per_round)

        for target, value in targets.items():
            if value > 0:
                if target in incomes_per_round:
                    targets[target] = max(0, targets[target] - incomes_per_round[target])
                    if targets[target] == 0:
                        freed_resources[target] = 0

                        if verbose:
                            print(f"new free resource! {target}")

        if verbose:
            print(rounds, targets)
            print(f"exprected rounds: {calculate_expected_payoff(targets, incomes_per_round)}")
            print(f"freed: {freed_resources}")
            print("")

    return rounds

def join_evaluate(settlement_places):
    incomes = defaultdict(list)
    trades = []
    for settlement_place in settlement_places:
        income, trades_ = evaluation_lists(settlement_place)
        for resource in income:
            incomes[resource] += income[resource]
        trades += trades_
    return incomes, trades

def evaluation_lists(settlement_place):
    income = defaultdict(list)
    trades = []

    for hexagon in settlement_place.bordersOn:
        if hexagon.resource != "fisch":
            income[hexagon.resource].append(hexagon.number)
        else:
            for number in hexagon.number:
                income[hexagon.resource].append(number)

    if settlement_place.harbor and settlement_place.harbor.trade:
        if settlement_place.harbor.trade == "3:1":
            trades.append("3:1")
        else:
            trades.append(settlement_place.harbor.resource)

    if settlement_place.fish_piece:
        income["fisch"].append(settlement_place.fish_piece.number)

    return income, trades

# income = {"stein": [5], "schaf": [8, 3], "holz": [4]}
# trades = ["3:1", "schaf"]

# rounds = evaluate(income, trades)

# print(rounds)