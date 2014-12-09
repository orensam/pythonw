class Tile:

    def __init__(self, right, left):
        self.left = left
        self.right = right

    def str_reg(self):
        s = "[%d:%d]"
        if self.left < self.right:
            return s % (self.left, self.right)
        return s % (self.right, self.left)

    def flip(self):
        self.left, self.right = self.right, self.left

    def str_lop(self):
        return "[%d:%d]" % (self.left, self.right)

class DoubleSix:

    def __init__(self, tiles):
        self._tiles = tiles[:]

    def is_empty(self):
        return not self._tiles

    def draw(self):
        return self._tiles.pop(0)

class LOP:

    CHAR_START = 'sS'
    CHAR_END = 'eE'

    def __init__(self):
        self._tiles = []

    def get_start(self):
        if self._tiles:
            return self._tiles[0].left

    def get_end(self):
        if self._tiles:
            return self._tiles[-1].right

    def get_side(self, c):
        if c in self.CHAR_START:
            return self.get_start()
        elif c in self.CHAR_END:
            return self.get_end()

    def __str__(self):
        return ' '.join([t.str_lop() for t in self._tiles])

    def can_put_at_pos(self, num, pos):
        if not self._tiles:
            return True
        pos_num = self.get_side(pos)
        if pos_num == num:
            return True
        return False

    def put_tile(self, tile, pos):
        if not self._tiles:
            self._tiles.append(tile)
        elif pos in self.CHAR_START:
            if tile.right != self.get_start():
                tile.flip()
            self._tiles.insert(0, tile)
        else:
            if tile.left != self.get_end():
                tile.flip()
            self._tiles.insert(len(self._tiles), tile)