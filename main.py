import os
from games import dice_battle
from games import hangman  # YE WALI LINE MISSING THI

# main.py
from games import dice, hangman, runner

def main_menu():
    print("Welcome to Mini Arcade Pro!")
    print("1. Dice Battle")
    print("2. Hangman")
    print("3. Block Blaster Runner")
    print("4. Exit")
    choice = input("Choose a game: ")
    return choice

def main():
    while True:
        choice = main_menu()
        if choice == "1":
            dice.play()
        elif choice == "2":
            hangman.play()
        elif choice == "3":
            runner.play()
        elif choice == "4":
            print("Thanks for playing! Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()