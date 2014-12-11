CHOOSE_ACTION = "Choose action: Tile (t) or Draw (d): "
ILLEGAL_MOVE = "Error: Illegal move"
CHOOSE_TILE = "Choose tile (1-%d), and place (Start - s, End - e): "

ILLEGAL_MOVE_SCORE = 3

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

    def first_move(self):
        self.game.add_tile_at_end(self.tiles[0])
        self.tiles.pop(0)


class HumanPlayer(Player):

    TILE_CHAR = 't'
    DRAW_CHAR = 'd'

    def __init__(self, pid, name, tiles, game):
        super(HumanPlayer, self).__init__(pid, name, tiles, game)

    def get_input(self):
        inp = raw_input(CHOOSE_TILE % len(self.tiles))
        return int(inp.split()[0]), inp.split()[1].lower()

    def get_move(self):
        tile_number, lop_pos = self.get_input()
        tile = self.tiles[tile_number-1]
        while not self.game.can_put_tile_at_pos(tile, lop_pos):
            print ILLEGAL_MOVE
            tile_number, lop_pos = self.get_input()
            tile = self.tiles[tile_number-1]
        return tile_number, lop_pos

    def move(self):
        choice = raw_input(CHOOSE_ACTION).lower()
        if choice == self.TILE_CHAR:
            tile_number, lop_pos = self.get_move()
            self.put_tile(tile_number, lop_pos)
        elif choice == self.DRAW_CHAR:
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
            if self.game.can_put_num_at_pos(low, self.game.LOP_END):
                return self.put_tile(tile_number, self.game.LOP_END)
            elif self.game.can_put_num_at_pos(low, self.game.LOP_START):
                return self.put_tile(tile_number, self.game.LOP_START)
            elif self.game.can_put_num_at_pos(high, self.game.LOP_END):
                return self.put_tile(tile_number, self.game.LOP_END)
            elif self.game.can_put_num_at_pos(high, self.game.LOP_START):
                return self.put_tile_at(tile_number, self.game.LOP_START)

        self.draw_from_deck()


class CompPlayerMedium(CompPlayer):

    def __init__(self, pid, name, tiles, game):
        super(CompPlayerMedium, self).__init__(pid, name, tiles, game)

    def calc_move_score(self, tile, lop_num, lop_stats, lop_size, match_high = False):
        exposed_num, match_num = max([tile.right, tile.left]), min([tile.right, tile.left])
        if match_high:
            exposed_num, match_num = match_num, exposed_num
        if lop_num != match_num:
            return ILLEGAL_MOVE_SCORE

        n_tiles_with_exposed_num = 7 - lop_stats[exposed_num] - \
                                   len([t for t in self.tiles if exposed_num in (t.right, t.left)])

        n_tiles_remaining = self.game.DECK_SIZE - lop_size - 1

        return float(n_tiles_with_exposed_num) / n_tiles_remaining

    def move(self):
        lop_stats = self.game.get_lop_stats()
        lop_size = self.game.get_lop_size()
        lop_start = self.game.get_lop_start()
        lop_end = self.game.get_lop_end()

        # List will contain tuples: ((tile_num, pos), score)
        move_scores = []

        for i, tile in enumerate(self.tiles):
            tile_number = i + 1

            move = ((tile_number, self.game.LOP_END),
                    self.calc_move_score(tile, lop_end, lop_stats, lop_size))
            move_scores.append(move)
            move = ((tile_number, self.game.LOP_START),
                    self.calc_move_score(tile, lop_start, lop_stats, lop_size))
            move_scores.append(move)
            move = ((tile_number, self.game.LOP_END),
                    self.calc_move_score(tile, lop_end, lop_stats, lop_size,
                                         match_high= True))
            move_scores.append(move)
            move = ((tile_number, self.game.LOP_START),
                    self.calc_move_score(tile, lop_start, lop_stats, lop_size,
                                         match_high= True))
            move_scores.append(move)

            move_scores.sort(key=lambda x: x[1]) # keeps original order when tied

        best_move_score = move_scores[0][1]
        
        if best_move_score > 2:
            self.draw_from_deck()
            return

        self.put_tile(*move_scores[0])
    