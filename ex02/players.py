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

class HumanPlayer(Player):
    def __init__(self, pid, name, tiles, game):
        super(HumanPlayer, self).__init__(pid, name, tiles, game)

    def get_input(self):
        inp = raw_input(CHOOSE_TILE % len(self.tiles))
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
    
    def move(self):

        lop = self.game.get_lop_tiles()
        
        # A move is consists of a tile number (1-T) and a position (s/e).
        # This 'default value' is for clarification only
        move_scores = {}
        
        # best_move = (0, '')  
        # best_move_score = float('inf')
        
        for i, t in enumerate(self.tiles):
            tile_number = i + 1
            low = min([t.right, t.left])
            high = max([t.right, t.left])
            move_scores[(tile_number, )]

            m = (tile_number, 'e')
            if self.game.can_put_num_at_end(low):
                move_scores[m] = self.calc_move_score(m)
            else
                move_scores[m] = ILLEGAL_MOVE_SCORE    
            
            m = (tile_number, 's')
            if self.game.can_put_num_at_start(low):
                move_scores[m] = self.calc_move_score(m)
            
            
            
            
            elif self.game.can_put_num_at_start(low):
                m = (tile_number, 's')
                move_scores[m] = self.calc_move_score(m)                
            elif self.game.can_put_num_at_end(high):
                m = (tile_number, 'e')
                return self.put_tile(tile_number, 'e')
            elif self.game.can_put_num_at_start(high):
                return self.put_tile(tile_number, 's')
            
        
        
        if best_move_score > 2:
            self.draw_from_deck()
            return
    
    
    
    
    
    
    
    
    