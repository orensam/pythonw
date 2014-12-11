"""
Python Workshop Project 2: Domino
Name: Oren Samuel
Login: orensam
ID: 200170694

Tile module for the Domino game.
Contains objects that involve tile handling.
"""


class Tile:
    """
    Represents a single tile.
    """

    def __init__(self, right, left):
        """
        Initializes the tile with the given left and right values.
        """
        self.left = left
        self.right = right

    def flip(self):
        """
        Flips the tile left<->right.
        """
        self.left, self.right = self.right, self.left

    def str_reg(self):
        """
        Returns the regular string representation of the tile.
        """
        s = "[%d:%d]"
        if self.left < self.right:
            return s % (self.left, self.right)
        return s % (self.right, self.left)

    def str_lop(self):
        """
        Returns the LOP-oriented string representation of the tile.
        """
        return "[%d:%d]" % (self.left, self.right)


class DoubleSix:
    """
    Represents the Double-Six deck.
    """

    def __init__(self, tiles):
        """
        Initializes the deck with the given tiles.
        """
        self._tiles = tiles[:]

    def empty(self):
        """
        Returns True iff the deck is empty.
        """
        return len(self._tiles) == 0

    def draw(self):
        """
        Draws the first tile from the deck and returns it.
        """
        return self._tiles.pop(0)


class LOP:
    """
    Represents the Line-of-Play, i.e tiles on the table.
    """

    def __init__(self):
        """
        Initializes an empty LOP.
        """
        self._tiles = []

    def get_start(self):
        """
        Returns the number at the start of the LOP.
        """
        if self._tiles:
            return self._tiles[0].left

    def get_end(self):
        """
        Returns the number at the end of the LOP.
        """
        if self._tiles:
            return self._tiles[-1].right

    def __str__(self):
        """
        Returns the LOP's string representation.
        :return:
        """
        return ' '.join([t.str_lop() for t in self._tiles])

    def empty(self):
        """
        Returns True iff the LOP is empty.
        """
        return len(self._tiles) == 0

    def get_size(self):
        """
        Returns the LOP's length.
        """
        return len(self._tiles)

    def get_stats(self):
        """
        Returns the 'statistics' of the LOP -
        A dictionary with keys 0..6, and the value of key k
        is the number of tiles in the LOP in which k appears.
        """
        stats = {i: 0 for i in range(7)}
        for t in self._tiles:
            stats[t.left] += 1
            if t.right != t.left:
                stats[t.right] += 1
        return stats

    def add_at_start(self, tile):
        """
        Adds given tile at the start of the LOP, matching the tile's
        orientation if needed.
        """
        if tile.right != self.get_start():
            tile.flip()
        self._tiles.insert(0, tile)

    def add_at_end(self, tile):
        """
        Adds given tile at the start of the LOP, matching the tile's
        orientation if needed.
        """
        if tile.left != self.get_end():
            tile.flip()
        self._tiles.insert(len(self._tiles), tile)
