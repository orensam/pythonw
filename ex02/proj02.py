"""
Python Workshop Project 2: Domino
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
