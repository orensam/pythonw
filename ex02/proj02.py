"""
Python Workshop Project 2: Domino
Name: Oren Samuel
Login: orensam
ID: 200170694

Main file - entry point to the game.
Creates the game and starts it.
"""

from game import Game


def main():
    game = Game()
    game.setup()
    game.play()


if __name__ == "__main__":
    main()
