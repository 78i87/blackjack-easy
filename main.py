import random
from colorama import Fore, Style, init
import time
init()
def get_number_of_players():
    while True:
        try:
            number_player = int(input('Enter the number of boxes: '))
            if 1 <= number_player <= 4:
                return number_player
            else:
                print('The number needs to be between 1 and 4.')
        except ValueError:
            print("Please enter a valid integer.")



def get_start_chip():
    while True:
        try:
            start_chip = int(input('Starting chips amount: '))
            if start_chip % 50 == 0 and start_chip > 0:
                return start_chip
            else:
                print("Enter a positive amount divisible by 50 to make the program's life easier.")
        except ValueError:
            print("Please enter a valid integer.")



def create_deck():
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['♠','♣','♥','♦']
    deck = []
    for _ in range(6):
        one = [(value, suit) for value in values for suit in suits]
        deck.extend(one)
    random.shuffle(deck)
    return deck


def card_value(card):
    value , suit = card
    if value in ['J','Q','K']:
        return 10
    elif value == 'A':
        return 11
    else:
        return int(value)


def hit(deck, total_number):
    card = deck.pop()
    total_number += card_value(card)
    if card[0] == 'A'and total_number > 21:
        total_number -= 10
    return card, total_number

def double_down(deck, hand, total, bet, remaining_chips):
    if len(hand) == 2 and remaining_chips >= bet:
        card, total = hit(deck, total)
        hand.append(card)
        return hand, total, True
    else:
        print("Cannot double down.")
        return hand, total, False



def deal_initial_cards(deck, number_of_players):
    player_hands = {player: [] for player in range(1, number_of_players + 1)}
    dealer_hand = []
    for _ in range(2):
        for player in range(1, number_of_players + 1):
            card = deck.pop()
            player_hands[player].append(card)
        dealer_hand.append(deck.pop())
    return player_hands, dealer_hand



def display_initial_hands(player_hands, dealer_hand):
    for player, hand in player_hands.items():
        print(f"Player {player}'s hand: {hand}")
    print(f"{Fore.BLUE}Dealer's hand: [{dealer_hand[0]}, ('Hidden Card')]{Style.RESET_ALL}")


def basic_strategy(player_hand, dealer_up_card):
    dealer_value = card_value(dealer_up_card)
    player_total = sum(card_value(card) for card in player_hand)
    player_cards = [card[0] for card in player_hand]  # Extract card values (ignoring suits)

    # Adjust dealer's Ace to a value of 11 for comparison
    dealer_value = 11 if dealer_value == 'A' else dealer_value

    # If the hand has a pair, decide based on individual card values
    if len(player_hand) == 2 and player_cards[0] == player_cards[1]:
        pair_value = card_value(player_hand[0])  # Use card_value function to get the value

        # For pairs of 8s or Aces, which would normally be split, we hit if it's a hard 16 or soft 12
        if pair_value == 8:
            player_total = 16  # Treat a pair of 8s as a hard 16
        elif pair_value == 11:
            player_total = 12  # Treat a pair of Aces as a soft 12

    # Now follow the basic strategy as indicated on the card, replacing splits with hits/stands
    if player_total < 12:
        return 'h'
    elif player_total == 12:
        return 'h' if dealer_value in [2, 3, 7, 8, 9, 10, 11] else 's'
    elif 13 <= player_total <= 16:
        return 'h' if dealer_value >= 7 else 's'
    elif player_total == 17 and dealer_value == 11:
        return 'h'
    elif player_total in [18, 19, 20, 21]:
        return 's'
    elif player_total == 10 or player_total == 11:
        return 'd' if dealer_value < 10 else 'h'
    else:
        return 's'


def start_game(number_player, start_chip):
    deck = create_deck()
    minimum_bet = 5  # Set the minimum bet to 5
    remaining_chips = {player: start_chip for player in range(1, number_player + 1)}
    user_box = random.randint(1, number_player)
    print(f"You are assigned to Box {user_box}")

    reset = input('Do the deck get refreshed after every round (yes or no): ').lower()

    while True:
        if reset == 'yes':
            deck = create_deck()

        player_hands, dealer_hand = deal_initial_cards(deck, number_player)
        display_initial_hands(player_hands, dealer_hand)

        for player in range(1, number_player + 1):
            is_user = player == user_box
            while True:
                player_total = sum(card_value(card) for card in player_hands[player])
                if player_total > 21:
                    print(f"Box {player} busts with {player_total}!")
                    remaining_chips[player] -= minimum_bet
                    break

                if is_user: #user's turn
                    print(f"Your hand (Box {player}): {player_hands[player]}, Total: {player_total}")
                    valid_input = False
                    while not valid_input:
                        choice = input("Do you want to hit(h), stand(s), or double down(d)? ").lower()
                        if choice in ['h', 's', 'd']:
                            valid_input = True
                        else:
                            print("Invalid input. Please choose 'h', 's', or 'd'.")

                    if choice == 'h':
                        card, player_total = hit(deck, player_total)
                        player_hands[player].append(card)
                        print(f"You hit: {card}. New total: {player_total}")
                    elif choice == 's':
                        print(f"You stand. Total: {player_total}")
                        break
                    elif choice == 'd':
                        if remaining_chips[player] >= 2 * minimum_bet:
                            remaining_chips[player] -= minimum_bet
                            card, player_total = hit(deck, player_total)
                            player_hands[player].append(card)
                            print(f"You doubled down. New card: {card}, New total: {player_total}, Remaining chips: {remaining_chips[player]}")
                            break
                        else:
                            print("You don't have enough chips to double down.")

                else:  # AI player's turns
                    dealer_up_card = dealer_hand[0]
                    decision = basic_strategy(player_hands[player], dealer_up_card)
                    if decision == 'h':
                        card, player_total = hit(deck, player_total)
                        player_hands[player].append(card)
                        print(f"Box {player} hits: {card}. New total: {player_total}")
                    elif decision == 's':
                        print(f"Box {player} stands. Total: {player_total}")
                        break

        dealer_total = sum(card_value(card) for card in dealer_hand)
        while dealer_total < 17:
            card, dealer_total = hit(deck, dealer_total)
            dealer_hand.append(card)
        print(f"Dealer's hand: {dealer_hand}, Total: {dealer_total}")

        for player in range(1, number_player + 1):
            player_total = sum(card_value(card) for card in player_hands[player])
            if player_total > 21:
                print(f"Box {player} busts with {player_total}!")
            elif dealer_total > 21 or player_total > dealer_total:
                print(f"Box {player} wins with {player_total}!")
                remaining_chips[player] += minimum_bet
            elif player_total == dealer_total:
                print(f"Box {player} pushes with {player_total}.")
            else:
                print(f"Box {player} loses with {player_total}.")
                remaining_chips[player] -= minimum_bet

            if remaining_chips[player] <= 0:
                print(f"Box {player} is out of chips!")

        print(f"{Fore.GREEN}Your remaining chips (Box {user_box}): {remaining_chips[user_box]}{Style.RESET_ALL}")

        if all(chips <= 0 for chips in remaining_chips.values()):
            print("All players are out of chips. Game over.")
            break

        time.sleep(1.5)


number_player = get_number_of_players()
start_chip = get_start_chip()
start_game(number_player, start_chip)
