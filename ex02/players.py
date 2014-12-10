CHOOSE_ACTION = "Choose action: Tile (t) or Draw (d): "
ILLEGAL_MOVE = "Error: Illegal move"

class Player(object):

    def __init__(self, pid, name, tiles, game):
        self.id = pid
        self.name = name
        self.tiles = tiles
        self.game = game

    def hand_str(self):
        return ' '.join([t.str_reg() for t in self.tiles])

    def draw_from_deck(self):
        tile = self.game.draw_from_deck()
        self.tiles.append(tile)

    def get_tile_tups(self):
        return [(t.left, t.right) for t in self.tiles]

    def put_tile(self, tile_number, lop_pos):
        self.game.add_tile_at_pos(self.tiles[tile_number - 1], lop_pos)
        self.tiles.pop(tile_number-1)

class HumanPlayer(Player):
    def __init__(self, pid, name, tiles, game):
        super(HumanPlayer, self).__init__(pid, name, tiles, game)

    def get_input(self):
        inp = raw_input("Choose tile (1-%d), and place (Start - s, End - e): " % len(self.tiles))
        return int(inp.split()[0]), inp.split()[1]

    def get_move(self):
        tile_number, lop_pos = self.get_input()
        tile = self.tiles[tile_number-1]
        while not self.game.can_put_tile_at_pos(tile, lop_pos):
            print ILLEGAL_MOVE
            tile_number, lop_pos = self.get_input()
            tile = self.tiles[tile_number-1]
        return tile_number, lop_pos

    def move(self):
        choice = raw_input(CHOOSE_ACTION)
        if choice in 'tT':
            tile_number, lop_pos = self.get_move()
            self.put_tile(tile_number, lop_pos)
        else: # choice is d or D
            self.draw_from_deck()

class CompPlayer(Player):
    def __init__(self, pid, name, tiles, game):
        super(CompPlayer, self).__init__(pid, name, tiles, game)

class CompPlayerEasy(CompPlayer):

    def __init__(self, pid, name, tiles, game):
        super(CompPlayerEasy, self).__init__(pid, name, tiles, game)

    def move(self):
        for i, t in enumerate(self.tiles):
            tile_number = i + 1
            low = min([t.right, t.left])
            high = max([t.right, t.left])
            if self.game.can_put_num_at_end(low):
                return self.put_tile(tile_number, 'e')
            elif self.game.can_put_num_at_start(low):
                return self.put_tile(tile_number, 's')
            elif self.game.can_put_num_at_end(high):
                return self.put_tile(tile_number, 'e')
            elif self.game.can_put_num_at_start(high):
                return self.put_tile(tile_number, 's')

        self.draw_from_deck()


class CompPlayerMedium(CompPlayer):
    def __init__(self, pid, name, tiles, game):
        super(CompPlayerMedium, self).__init__(pid, name, tiles, game)