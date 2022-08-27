import os
import re
import copy
import random
import signal
import sys

from collections import namedtuple


SUN = "sun"
MOON = "moon"
KEY = "key"
DOOR = "door"
NIGHTMARE = "nightmare"

RED = "red"
BLUE = "blue"
GREEN = "green"
BROWN = "brown"
BLACK = "black"

VICTORY_MESSAGE = "Victory"
DEFEAT_MESSAGE = "Defeat"
CLEAR_SCREEN = "clear"

Action = namedtuple("Card", "symbol, color")

deck = []
player_hand = []
labyrinth = []
limbo = []
discard = []
labyrinth_stack_counter = 0
labyrinth_stack_color = BLACK
doors = {RED: 0, BLUE: 0, GREEN: 0, BROWN: 0}


def signal_handler(signal, frame):
    """Signal handler for CTRL+C to clear the screen and exit"""
    os.system(CLEAR_SCREEN)
    sys.exit(0)


def new_game():
    """Here starts the new game"""
    red_suns = [copy.copy(Action(symbol=SUN, color=RED)) for _ in range(9)]
    red_moons = [copy.copy(Action(symbol=MOON, color=RED)) for _ in range(4)]
    red_keys = [copy.copy(Action(symbol=KEY, color=RED)) for _ in range(3)]
    red_doors = [copy.copy(Action(symbol=DOOR, color=RED)) for _ in range(2)]
    red_cards = red_suns + red_moons + red_keys + red_doors

    blue_suns = [copy.copy(Action(symbol=SUN, color=BLUE)) for _ in range(8)]
    blue_moons = [copy.copy(Action(symbol=MOON, color=BLUE)) for _ in range(4)]
    blue_keys = [copy.copy(Action(symbol=KEY, color=BLUE)) for _ in range(3)]
    blue_doors = [copy.copy(Action(symbol=DOOR, color=BLUE)) for _ in range(2)]
    blue_cards = blue_suns + blue_moons + blue_keys + blue_doors

    green_suns = [copy.copy(Action(symbol=SUN, color=GREEN)) for _ in range(7)]
    green_moons = [copy.copy(Action(symbol=MOON, color=GREEN)) for _ in range(4)]
    green_keys = [copy.copy(Action(symbol=KEY, color=GREEN)) for _ in range(3)]
    green_doors = [copy.copy(Action(symbol=DOOR, color=GREEN)) for _ in range(2)]
    green_cards = green_suns + green_moons + green_keys + green_doors

    brown_suns = [copy.copy(Action(symbol=SUN, color=BROWN)) for _ in range(6)]
    brown_moons = [copy.copy(Action(symbol=MOON, color=BROWN)) for _ in range(4)]
    brown_keys = [copy.copy(Action(symbol=KEY, color=BROWN)) for _ in range(3)]
    brown_doors = [copy.copy(Action(symbol=DOOR, color=BROWN)) for _ in range(2)]
    brown_cards = brown_suns + brown_moons + brown_keys + brown_doors

    nightmares = [copy.copy(Action(symbol=NIGHTMARE, color=BLACK)) for _ in range(10)]

    deck.extend(red_cards + blue_cards + green_cards + brown_cards)
    random.shuffle(deck)
    fill_hand_setup()
    add_limbo_cards_to_deck()
    deck.extend(nightmares)
    random.shuffle(deck)

    while not endgame():
        try:
            print_doors()
            print_labyrinth()
            print_hand()

            play_or_discard()
            fill_hand()
        except Exception as e:
            import traceback
            traceback.print_tb(e.__traceback__)
            break

    if all_doors_discovered():
        print(VICTORY_MESSAGE)
    else:
        print(DEFEAT_MESSAGE)


def print_deck(d):
    print(d)


def print_rules():
    """Prints the rules"""
    pass


def not_valid_initial_choice(choice):
    """Checks that the initial choice is new game (G) or read the rules (R)"""
    if choice.upper() == "G" or choice.upper() == "R":
        return False
    return True


def fill_hand_setup():
    """Fills the player's hand with 5 cards. 
    Doors and nightmares go to the limbo to be added later to the deck"""
    while len(player_hand) < 5:
        card = deck.pop()
        if card.symbol == DOOR or card.symbol == NIGHTMARE:
            limbo.append(card)
        else:
            player_hand.append(card)


def fill_hand():
    """Fill the player's hand (that is, take cards until the player's hand is 5 cards).
    If a door is drawed, it goes to the limbo to be added later to the deck.
    If a nightmare is drawed, it is resolved immediately
    """
    while len(player_hand) < 5:
        card = deck.pop()
        if card.symbol == DOOR:
            limbo.append(card)
        elif card.symbol == NIGHTMARE:
            resolve_nightmare()
        else:
            player_hand.append(card)
    add_limbo_cards_to_deck()
    random.shuffle(deck)


def resolve_nightmare():
    """A nightmare was drawed"""
    print("Nightmare!")
    while True:
        if key_in_hand():
            if has_doors():
                print("Discard a key (K), discard your hand (H), discard 5 cards (C) or discard a door (D)")
                k, h, c, d = True, True, True, True
            else:
                print("Discard a key (K), discard your hand (H), discard 5 cards (C)")
                k, h, c, d = True, True, True, False
        else:
            if has_doors():
                print("Discard your hand (H), discard 5 cards (C) or discard a door (D)")
                k, h, c, d = False, True, True, True
            else:
                print("Discard your hand (H), discard 5 cards (C)")
                k, h, c, d = False, True, True, False
        
        choice = input()
        if is_choice_valid(choice, k, h, c, d):
            execute_nightmare_choice(choice)
            break


def execute_nightmare_choice(choice):
    """"Does what the user wants to do with the nightmare"""
    if choice == "K":
        choose_key_to_discard()
    elif choice == "H":
        discard_hand()
    elif choice == "C":
        discard_5_cards()
    else:
        choose_door_to_discard()


def discard_5_cards():
    """Discard 5 cards from the deck, not counting doors and nightmares.
    If the card to be discarded is a door or nightmare it goes to the limbo to be later added to the deck."""
    counter = 0
    while counter < 5:
        # discard
        try:
            card = deck.pop()
            if card.symbol == DOOR:
                limbo.append(card)
                continue
            if card.symbol == NIGHTMARE:
                resolve_nightmare()
                continue
            counter = counter + 1
        except IndexError:
            print("No more cards")
            raise


def choose_key_to_discard():
    """Chooses which key from the player's hand should be discarded"""
    indexes = []
    for index, card in enumerate(player_hand):
        if card.symbol == KEY:
            indexes.append(index)
    for i in indexes:
        print("{index}: {color} key", i + 1, player_hand[i].color)
    key_index = input("Select key to discard: ")
    while True:
        if valid_key_index(int(key_index)):
            remove_key(int(key_index))
            break


def valid_key_index(key_index):
    if player_hand[key_index - 1].symbol == KEY:
        return True
    return False


def remove_key(key_index):
    player_hand.pop(key_index - 1)


def choose_door_to_discard():
    print("Select door to discard:")
    if doors.get(RED) > 0:
        print("1: Red door")
    if doors.get(BLUE) > 0:
        print("2: Blue door")
    if doors.get(GREEN) > 0:
        print("3: Green door")
    if doors.get(BROWN) > 0:
        print("4: Brown door")
    while True:
        choice = input("Door: ")
        if valid_door_to_discard(choice):
            discard_door(choice)
            break


def discard_door(door_choice):
    if door_choice == 1:
        doors[RED] = doors[RED] - 1
    if door_choice == 2:
        doors[RED] = doors[BLUE] - 1
    if door_choice == 3:
        doors[RED] = doors[GREEN] - 1
    if door_choice == 4:
        doors[RED] = doors[BROWN] - 1


def valid_door_to_discard(door_number):
    if door_number == 1 and doors.get(RED) > 0:
        return True
    if door_number == 2 and doors.get(BLUE) > 0:
        return True
    if door_number == 3 and doors.get(GREEN) > 0:
        return True
    if door_number == 4 and doors.get(BROWN) > 0:
        return True
    return False


def discard_hand():
    player_hand.clear()
    while len(player_hand) < 5:
        card = deck.pop()
        if card.symbol == DOOR or card.symbol == NIGHTMARE:
            limbo.append(card)
        else:
            player_hand.append(card)
    add_limbo_cards_to_deck()
    random.shuffle(deck)


def is_choice_valid(choice, k=False, h=False, c=False, d=False):
    if choice == "K" and k:
        return True
    if choice == "H" and h:
        return True
    if choice == "C" and c:
        return True
    if choice == "D" and d:
        return True
    return False


def has_doors():
    for _, value in doors.items():
        if value > 0:
            return True
    return False


def key_in_hand():
    for card in player_hand:
        if card.symbol == KEY:
            return True
    return False


def key_in_hand_of_color(color):
    for card in player_hand:
        if card.symbol == KEY and card.color == color:
            return True


def add_limbo_cards_to_deck():
    while limbo:
        deck.append(limbo.pop())


def endgame():
    if all_doors_discovered():
        return True
    if len(deck) == 0:
        return True
    return False


def all_doors_discovered():
    for key, value in doors.items():
        if value < 2:
            return False
    return True


def print_doors():
    print("Doors:")
    for color, count in doors.items():
        print(color + ": " + str(count), end="  ")
    print()
    print()


def print_labyrinth():
    if labyrinth:
        print("Labyrinth:")
        print("".join("" + card.symbol + "(" + card.color + ") " for card in labyrinth))
        print()
    else:
        print("The labyrinth is empty.")
        print()


def print_hand():
    print("Your hand:")
    for i in range(len(player_hand)):
        print(str(i+1) + ": " + player_hand[i].symbol + " (" + player_hand[i].color + ")")
    print()


def is_key(selected_card):
    return player_hand[int(selected_card) - 1].symbol == KEY


def play_is_valid(selected_card):
    try:
        card_number = int(selected_card)
    except ValueError:
        return False

    if card_number > 5 or card_number < 1:
        return False
    if not labyrinth or labyrinth[-1].symbol != player_hand[card_number - 1].symbol:
        return True
    return False


def valid_discard_selection(selected_card):
    try:
        card_number = int(selected_card)
    except ValueError:
        return False

    if card_number > 5 or card_number < 1:
        return False
    return True


def discard_card(selected_card):
    discard.append(player_hand[int(selected_card) - 1])
    player_hand.pop(int(selected_card) - 1)


def prophecy():

    print("Prophecy")
    prophecy_cards = [deck.pop() for _ in range(5)]
    #prophecy_cards = []
    #prophecy_cards.append(deck.pop())
    #prophecy_cards.append(deck.pop())
    #prophecy_cards.append(deck.pop())
    #prophecy_cards.append(deck.pop())
    #prophecy_cards.append(deck.pop())
    valid = False
    card_order = ""
    
    while not valid:
        print_prophecy_cards(prophecy_cards)
        card_order = input("Order the cards, put the card number separated by comma. The last card will be discarded: ")
        valid = valid_card_order(card_order)
    
    cards = card_order.split(",")
    index_to_be_discarded = int(cards[-1]) - 1
    discard.append(prophecy_cards[index_to_be_discarded])
    for card in list(reversed(cards[:-1])):
        deck.append(prophecy_cards[int(card) - 1])


def print_prophecy_cards(prophecy_cards):
    for i in range(len(prophecy_cards)):
        print(str(i+1) + ": " + prophecy_cards[i].symbol + "(" + prophecy_cards[i].color + ")")


def valid_card_order(card_order):
    card_numbers = card_order.split(",")
    reg = re.compile("[1-5]")
    for card_number in card_numbers:
        if not reg.match(card_number.strip()):
            return False
    return True


def gain_door_of_color(color):
    if doors[color] > 1:
        return
    print("got door of color " + color)
    doors[color] += 1
    remove_door_from_deck(color)
    input()


def remove_door_from_deck(color):
    card_pos = 0
    for card in deck:
        if card.color == color and card.symbol == DOOR:
            del deck[card_pos]
            break
        card_pos = card_pos + 1


def play_or_discard():
    global labyrinth_stack_counter
    global labyrinth_stack_color

    while True:
        action = input("Play a card (P) or discard a card (D): ").upper()

        if action == "P":
            while True:
                selected_card = input("Enter the card number to play: ")
                if play_is_valid(selected_card):
                    played_card = player_hand.pop(int(selected_card) - 1)
                    if not labyrinth or labyrinth[-1].color != played_card.color:
                        labyrinth_stack_counter = 1
                        labyrinth_stack_color = played_card.color
                    else:
                        labyrinth_stack_counter += 1
                    labyrinth.append(played_card)
                    if labyrinth_stack_counter == 3:
                        labyrinth_stack_counter = 0
                        labyrinth_stack_color = BLACK
                        gain_door_of_color(played_card.color)
             
                    break
            break
        elif action == "D":
            while True:
                selected_card = input("Enter the card number to discard: ")
                if valid_discard_selection(selected_card):
                    if is_key(selected_card):
                        prophecy()
                    discard_card(selected_card)
                    break
            break


def main():
    signal.signal(signal.SIGINT, signal_handler)

    choice = input("New Game (G) or Read the Rules (R): ")
    while not_valid_initial_choice(choice):
        input()
    if choice.upper() == "G":
        new_game()
    else:
        print_rules()


if __name__ == "__main__":
    main()
