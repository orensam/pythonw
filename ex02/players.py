"""
Python Workshop Project 2: Domino
Name: Oren Samuel
Login: orensam
ID: 200170694

Players module for the Domino game.
Contains classes for human and computer players.
"""


class Player(object):
    """
    Generic player class - all common operations are done here.
    """

    def __init__(self, pid, name, tiles, game):
        """
        Initializes a new player with the given id, name, tiles and
        game reference.
        """
        self.id = pid
        self.name = name
        self.tiles = tiles
        self._game = game

    def hand_str(self):
        """
        Returns a string of the player's hand.
        """
        return ' '.join([t.str_reg() for t in self.tiles])

    def draw_from_deck(self):
        """
        Draws a tile from the deck and adds it to player's tiles.
        """
        tile = self._game.draw_from_deck()
        self.tiles.append(tile)

    def get_tile_tups(self):
        """
        Returns a tuples-variant of the player's tile list
        :return:
        """
        return [(t.left, t.right) for t in self.tiles]

    def put_tile(self, tile_number, lop_pos):
        """
        Adds the player's <tile_number>th tile to the LOP
        in the specified position.
        """
        self._game.add_tile_at_pos(self.tiles[tile_number - 1], lop_pos)
        self.tiles.pop(tile_number - 1)

    def first_move(self):
        """
        Performs a first move, i.e place the player's first tile on the LOP.
        """
        self._game.add_tile_at_pos(self.tiles[0], self._game.LOP_START)
        self.tiles.pop(0)


class HumanPlayer(Player):
    """
    Human player object. Inherits from the generic player.
    Handles moves by interacting with the user.
    """

    # Print strings
    CHOOSE_ACTION = "Choose action: Tile (t) or Draw (d): "
    ILLEGAL_MOVE = "Error: Illegal move"
    CHOOSE_TILE = "Choose tile (1-%d), and place (Start - s, End - e): "

    # Input chars
    TILE_CHAR = 't'
    DRAW_CHAR = 'd'

    def get_input(self):
        """
        Gets tile move input from the user.
        """
        inp = raw_input(self.CHOOSE_TILE % len(self.tiles))
        return int(inp.split()[0]), inp.split()[1].lower()

    def get_move(self, choice):
        """
        Gets the move from the user and returns True iff
        the move is legal. choice is t/d for tile/draw
        """
        if choice == self.TILE_CHAR:
            tile_number, lop_pos = self.get_input()
            tile = self.tiles[tile_number - 1]
            if not self._game.can_put_tile_at_pos(tile, lop_pos):
                # illegal move
                return False
            # move OK, do it
            self.put_tile(tile_number, lop_pos)
            return True

        # Deck draw move
        elif choice == self.DRAW_CHAR:
            self.draw_from_deck()
            return True

    def move(self):
        """
        Performs one move of the player.
        """
        choice = raw_input(self.CHOOSE_ACTION).lower()
        while not self.get_move(choice):
            print self.ILLEGAL_MOVE
            choice = raw_input(self.CHOOSE_ACTION).lower()


class CompPlayer(Player):
    """
    Generic Computer player class.
    No behavior is common to both computer player variants,
    so this class exists for order's sake.
    """
    pass


class CompPlayerEasy(CompPlayer):
    """
    Class for the easy computer player.
    Chooses moves according to the game specification.
    """

    def move(self):
        """
        Performs one move of the easy computer player.
        """
        for i, t in enumerate(self.tiles):
            tile_number = i + 1
            low = min([t.right, t.left])
            high = max([t.right, t.left])
            if self._game.can_put_num_at_pos(low, self._game.LOP_END):
                return self.put_tile(tile_number, self._game.LOP_END)
            elif self._game.can_put_num_at_pos(low, self._game.LOP_START):
                return self.put_tile(tile_number, self._game.LOP_START)
            elif self._game.can_put_num_at_pos(high, self._game.LOP_END):
                return self.put_tile(tile_number, self._game.LOP_END)
            elif self._game.can_put_num_at_pos(high, self._game.LOP_START):
                return self.put_tile(tile_number, self._game.LOP_START)

        self.draw_from_deck()


class CompPlayerMedium(CompPlayer):
    """
    Class for the medium computer player.
    Chooses moves according to the game specification.
    """

    # Scores
    ILLEGAL_MOVE_SCORE = 3
    DRAW_FROM_DECK_SCORE = 2

    def calc_move_score(self, tile, lop_num, lop_stats, lop_size,
                        match_high=False):
        """
        Calculates the score for matching the given tile to the LOP,
        where lop_num is the relevant value in the LOP to match.
        lop_stats is the number of tile-occurrences for each number in the LOP,
        lop_size is the length of the LOP.
        match_high is True iff the wanted move is to match the high value
        of the given tile. (Default behaviour is to match the low value).
        """
        # Choose which number is going to be exposed
        exposed_num, match_num = max([tile.right, tile.left]), \
                                 min([tile.right, tile.left])
        if match_high:
            exposed_num, match_num = match_num, exposed_num
        if lop_num != match_num:
            return self.ILLEGAL_MOVE_SCORE

        # Calculate numerator of score - possible number of tiles with
        # The same number as we're leaving exposed
        n_tiles_with_exposed_num = 7 - lop_stats[exposed_num] - \
                                   len([t for t in self.tiles if
                                        exposed_num in (t.right, t.left)])

        # Calculate denominator - total number of remaining tiles
        n_tiles_remaining = self._game.DECK_SIZE - lop_size - 1

        # Final score calculation
        return float(n_tiles_with_exposed_num) / n_tiles_remaining

    def move(self):
        """
        Perform one move of the medium computer.
        :return:
        """

        # Get LOP info
        lop_stats = self._game.get_lop_stats()
        lop_size = self._game.get_lop_size()
        lop_start = self._game.get_lop_start()
        lop_end = self._game.get_lop_end()

        # List will contain tuples: ((tile_num, pos), score)
        move_scores = []

        # Iterate possible moves, according to wanted order
        for i, tile in enumerate(self.tiles):
            tile_number = i + 1
            move = ((tile_number, self._game.LOP_END),
                    self.calc_move_score(tile, lop_end, lop_stats, lop_size))
            move_scores.append(move)
            move = ((tile_number, self._game.LOP_START),
                    self.calc_move_score(tile, lop_start, lop_stats, lop_size))
            move_scores.append(move)
            move = ((tile_number, self._game.LOP_END),
                    self.calc_move_score(tile, lop_end, lop_stats, lop_size,
                                         match_high=True))
            move_scores.append(move)
            move = ((tile_number, self._game.LOP_START),
                    self.calc_move_score(tile, lop_start, lop_stats, lop_size,
                                         match_high=True))
            move_scores.append(move)

        # Choose best move (lowest score).
        move_scores.sort(key=lambda x: x[1])  # keeps original order when tied
        best_move_score = move_scores[0][1]
        if best_move_score > self.DRAW_FROM_DECK_SCORE:
            # No good moves, draw from deck
            self.draw_from_deck()
            return

        # Perform move
        self.put_tile(*move_scores[0][0])
