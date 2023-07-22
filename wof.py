import json
import random
import os
from datetime import datetime
import atexit

# Load the wheel configuration from a JSON file
with open('wheel.json', 'r') as f:
    WHEEL = json.load(f)

# Load the categories and phrases from a JSON file
with open('phrases.json', 'r') as f:
    PHRASES = json.load(f)

CATEGORIES = list(PHRASES.keys())  # Extract the categories from the phrases

VOWELS = 'AEIOU'  # Define vowels
CONSONANTS = 'BCDFGHJKLMNPQRSTVWXYZ'  # Define consonants
VOWEL_COST = 250  # Set the cost of buying a vowel

# Player class
class Player:
    def __init__(self, name):
        self.name = name  # Set the name of the player
        self.score = 0  # Initialize the score to zero

# Function to simulate spinning the wheel
def spinWheel():
    return random.choice(WHEEL)

# Function to select a random category and phrase
def getRandomCategoryAndPhrase():
    category = random.choice(CATEGORIES)
    phrase = random.choice(PHRASES[category])
    return category, phrase

# Function to hide letters in the phrase that have not been guessed
def obscurePhrase(phrase, guessed):
    return ' '.join('_' if letter not in guessed else letter for letter in phrase)

# Function to get a consonant guess from the player
def getGuess():
    while True:
        guess = input("Enter your guess: ").upper()
        if len(guess) == 1 and guess in CONSONANTS:
            return guess
        else:
            print("Invalid guess. Please enter a consonant.")

# Function to buy a vowel
def buyVowel(player):
    while True:
        vowel = input("Enter a vowel: ").upper()
        if len(vowel) == 1 and vowel in VOWELS:
            player.score -= VOWEL_COST  # Subtract vowel cost from player's score
            return vowel
        else:
            print("Invalid input. Please enter a vowel.")

# Function to update game history and write to the log file
def updateGameHistory(player, action, result, log_file):
    # Load existing history if it exists
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                history = json.load(f)
        else:
            history = []

        # Add the new gameplay event
        event = {
            "player": player.name,
            "action": action,
            "result": result,
            "score": player.score
        }
        history.append(event)

        # Save the updated game history
        with open(log_file, 'w') as f:
            json.dump(history, f)
    except Exception as e:
        print(f"Error updating game history: {e}")

# Function to determine the winner based on score
def getWinner(players):
    return max(players, key=lambda player: player.score)

# Function to write the scores to the log file at the end of the game
def writeScores(players, log_file):
    scores = {player.name: player.score for player in players}
    try:
        with open(log_file, 'a') as f:
            f.write("\nCurrent scores:\n")
            for name, score in scores.items():
                f.write(f"{name}: {score}\n")
    except Exception as e:
        print(f"Error writing scores: {e}")

# Function to print game instructions
def printHelp():
    print("""
    Welcome to Wheel of Fortune! Here are the rules:

    - The game is played with a number of turns. On each turn, a player has three options:
        1) Spin the wheel: The wheel has a number of segments, offering various amounts of money, bankrupt, or lose a turn.
        2) Buy a vowel: For a fixed cost of 250 points, you can guess a vowel that might be in the phrase.
        3) Solve the puzzle: If you think you know what the phrase is, you can try to solve. If you're correct, you win!

    - When you spin the wheel, if you land on a money amount, you can guess a consonant. If the consonant is in the phrase, you win the amount times the number of appearances of the consonant. If it's not in the phrase, your turn ends.

    - If you have enough money, you can choose to buy a vowel instead of spinning the wheel. This costs a flat 250 points. If the vowel is in the phrase, you get to keep your turn. If it's not, your turn ends.

    - If at any time you think you know the phrase, you can try to solve the puzzle. If you're correct, you win the game. If you're not correct, your turn ends.

    - The game ends when a player successfully solves the puzzle. The player who solves the puzzle is the winner.

    Now, let's get back to the game!
    """)

def main():
    # Define the players
    players = [Player('ChatGPTv4 1'), Player('Google Bert(aka Bard) 2'), Player('LaMMA')]

    print('Welcome to Wheel of Fortune!')

    # Select a random category and phrase
    category, phrase = getRandomCategoryAndPhrase()
    guessed = set()  # Set of guessed letters
    print(f"The category is: {category}")

    # Generate a timestamp and create a unique log file for this game
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    log_file = f"log_{timestamp}.json"

    # Log the chosen category and phrase before game start
    initial_log = {"category": category, "phrase": phrase}
    with open(log_file, 'w') as f:
        json.dump([initial_log], f)

    # Register a function to be executed upon termination
    atexit.register(writeScores, players, log_file)

    playerIndex = 0  # Index of the current player
    while True:
        player = players[playerIndex]
        print(f"It's {player.name}'s turn. You have {player.score} points.")
        print(obscurePhrase(phrase, guessed))

        if player.score >= VOWEL_COST:
            action = input("What do you want to do? (1- Spin the wheel, 2- Buy a vowel, 3- Solve the puzzle, 4- Help): ")
        else:
            action = input("What do you want to do? (1- Spin the wheel, 3- Solve the puzzle, 4- Help): ")

        # Handle the player's action
        if action == '1':
            spin = spinWheel()
            print("You spun: ", spin['text'])
            if spin['type'] == 'bankrupt':
                player.score = 0
                updateGameHistory(player, "spin", "bankrupt", log_file)
            elif spin['type'] == 'lose_a_turn':
                pass
            else:
                guess = getGuess()
                if guess in phrase:
                    player.score += spin['value'] * phrase.count(guess)
                    guessed.add(guess)
                    updateGameHistory(player, "guess", "success", log_file)
                else:
                    updateGameHistory(player, "guess", "failure", log_file)
        elif action == '2' and player.score >= VOWEL_COST:
            vowel = buyVowel(player)
            if vowel in phrase:
                guessed.add(vowel)
                updateGameHistory(player, "buy_vowel", "success", log_file)
            else:
                updateGameHistory(player, "buy_vowel", "failure", log_file)
        elif action == '3':
            guess = input("Enter your solution: ")
            if guess.upper() == phrase.upper():
                print("Congratulations, you solved the puzzle!")
                player.score += 500  # Bonus for solving the puzzle
                updateGameHistory(player, "solve", "success", log_file)
                break
            else:
                print("Sorry, that's not correct.")
                updateGameHistory(player, "solve", "failure", log_file)
        elif action == '4':
            printHelp()

        # Switch to the next player
        playerIndex = (playerIndex + 1) % len(players)

    # Game over, print the winner
    winner = getWinner(players)
    print(f"The winner is: {winner.name} with {winner.score} points.")

if __name__ == "__main__":
    main()
