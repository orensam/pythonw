class Tile:

    def __init__(self, right, left):
        self.left = left
        self.right = right

    def flip(self):
        self.left, self.right = self.right, self.left

    def str_reg(self):
        s = "[%d:%d]"
        if self.left < self.right:
            return s % (self.left, self.right)
        return s % (self.right, self.left)

    def str_lop(self):
        return "[%d:%d]" % (self.left, self.right)

class DoubleSix:

    def __init__(self, tiles):
        self._tiles = tiles[:]

    def empty(self):
        return len(self._tiles) == 0

    def draw(self):
        return self._tiles.pop(0)

class LOP:

    def __init__(self):
        self._tiles = []

    def get_start(self):
        if self._tiles:
            return self._tiles[0].left

    def get_end(self):
        if self._tiles:
            return self._tiles[-1].right

    def __str__(self):
        return ' '.join([t.str_lop() for t in self._tiles])

    def empty(self):
        return len(self._tiles) == 0

    def add_at_start(self, tile):
        if tile.right != self.get_start():
            tile.flip()
        self._tiles.insert(0, tile)

    def add_at_end(self, tile):
        if tile.left != self.get_end():
            tile.flip()
        self._tiles.insert(len(self._tiles), tile)