CHOOSE_ACTION = "Choose action: Tile (t) or Draw (d): "
ILLEGAL_MOVE = "Error: Illegal move"

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
    
    def can_put(self, tile):
        if not self._tiles:
            return True
        if set((self.get_end(), self.get_start())).intersection(set((tile.left, tile.right))): 
            return True
        return False
    
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
        

class Player(object):
    
    def __init__(self, pid, name, tiles, game):
        self.id = pid
        self.name = name
        self.tiles = tiles
        self.game = game
    
    def hand_str(self):
        return ' '.join([t.str_reg() for t in self.tiles])
    
    def draw_drom_deck(self):
        tile = self.game.draw_from_deck()
        self.tiles.append(tile)
    
    def get_tile_tups(self):
        return [(t.left, t.right) for t in self.tiles]
    
    def put_tile(self, tile_number, lop_pos):
        self.game.put_tile(self.tiles[tile_number - 1], lop_pos)
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
        while not self.game.is_legal_move(tile, lop_pos):
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
            self.draw_drom_deck()
            
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
            if self.game.lop.can_put_at_pos(low, 'e'):
                self.put_tile(tile_number, 'e')
                return
            elif self.game.lop.can_put_at_pos(low, 's'):
                self.put_tile(tile_number, 's')
                return
            elif self.game.lop.can_put_at_pos(high, 'e'):
                self.put_tile(tile_number, 'e')
                return
            elif self.game.lop.can_put_at_pos(high, 's'):
                self.put_tile(tile_number, 's')
                return
        self.draw_drom_deck()
              

class CompPlayerMedium(CompPlayer):
    def __init__(self, pid, name, tiles, game):
        super(CompPlayerMedium, self).__init__(pid, name, tiles, game)    
        
        
class Game:
    
    def __init__(self):
        self.n_players = 0
        self._players = {}
        self.lop = LOP()
        self.ds = DoubleSix([])
    
    def line_to_tiles(self, line):
        """
        Return a list of 3-tuples.
        Each tuple represents a Tile: position, left, right.
        """
        tiles = []
        tile_strs = [x.strip() for x in line.split('-')]
        for ts in tile_strs:
            tints = [int(x) for x in ts.split(',')]
            tiles.append((tints[0], tints[1], tints[2]))
        return tiles
            
    def parse_file(self, file_path):
        lines = open(file_path).readlines()
        is_big_comment = False
        is_docstring = False
        res = []
        
        for line in lines:
            # Handle single line
            new_line = ""
            while line:                
                # Handle big comments
                if is_big_comment:
                    idx = line.find('*/')
                    if idx >= 0:
                        line = line[idx+2:] 
                        is_big_comment = False
                    else:
                        break

                elif is_docstring:
                    idx = line[3:].find('"""')
                    if idx >= 0:
                        line = line[idx+3:]
                        is_docstring = False
                    else:
                        break

                elif line.startswith(('/**', '/*')):
                    is_big_comment = True     
                
                elif line.startswith('"""'):
                    line = line[3:]
                    is_docstring = True
                
                elif line.startswith('//'):
                    break
                
                elif line.startswith('#'):
                    break
                
                else:                    
                    com_start = set([line.find('#'), line.find('//'), line.find('/*'), line.find('/**'), line.find('"""')])
                    com_start.remove(-1)
                    if com_start:
                        idx = min(com_start)
                        new_line += line[:idx]
                        line = line[idx:]
                    else:
                        new_line = line
                        line = ""
                        
            new_line = new_line.strip()
            if new_line:
                res.append(new_line)
            # end handle single line
        
        tiles = []
        for line in res:
            tiles += self.line_to_tiles(line)
            
        return tiles
    
    def is_legal_move(self, tile, lop_pos):
        return self.lop.can_put_at_pos(tile.left, lop_pos) or self.lop.can_put_at_pos(tile.right, lop_pos) 
    
    def put_tile(self, tile, lop_pos):
        self.lop.put_tile(tile, lop_pos)
        
    def add_player(self, pid, name, is_human, skill, tiles):
        if is_human:
            self._players[pid] = HumanPlayer(pid, name, tiles, self)
        elif skill == 'e':
            self._players[pid] = CompPlayerEasy(pid, name, tiles, self)
        else:
            self._players[pid] = CompPlayerMedium(pid, name, tiles, self)
        self.n_players += 1
    
    def draw_from_deck(self):
        return self.ds.draw()
    
    def get_pids(self):
        return [pid for pid in self._players]
    
    def get_player(self, pid):
        return self._players[pid]
    
    def player_won(self, pid):
        p = self.get_player(pid)
        return len(p.tiles) == 0
    
    def can_play(self, pid):
        p = self.get_player(pid)
        for t in p.tiles:
            if self.lop.can_put(t):
                return True
        
        if not self.ds.is_empty():
            return True
        
        return False
    
    def step(self, pid):
        p = self.get_player(pid)
        print "Turn of " + p.name + " to play, player " + str(pid) + ":"
        print "Hand :: " + p.hand_str()
        print "LOP  :: " + str(self.lop)
        p.move()
    
    def chose_first_player(self):
        player_tiles = {pid:self.get_player(pid).get_tile_tups() for pid in self.get_pids()}
        
        for i in range(6,0,-1):
            for pid, tiles in player_tiles.items():
                if (i,i) in tiles:
                    return pid
        
        player_max_tile_sum = {pid:max([sum(t) for t in player_tiles[pid]]) for pid in player_tiles}
        candidates = []
        cur_max = -1
        
        for pid, tsum in player_max_tile_sum.items():
            if tsum > cur_max:
                candidates = [pid]
            elif tsum == cur_max:
                candidates.append(pid)
        
        cand_names = [(pid, self.get_player(pid).name) for pid in candidates]
        cand_names.sort(key = lambda c : c[1])
        return cand_names[0][0]
            
         
    def player_iter(self):
        first = self.chose_first_player()
        cur_pid = first
        cant_play_count = 0
        while cant_play_count < len(self._players):
            if cur_pid == first:
                cant_play_count = 0
            if self.can_play(cur_pid):
                yield cur_pid
            else:
                cant_play_count += 1
            cur_pid = (cur_pid % self.n_players) + 1
            
            
    def play(self):
        for pid in self.player_iter():
            self.step(pid)
            if self.player_won(pid):
                print "Player " + str(pid) + ", " + self.get_player(pid).name + " wins!"
                return
        # If no player won and iteration ended,
        # It means no player can play, i.e draw
        print "It's a draw!"
                
    def setup(self):
        print "Welcome to Domino!"
    
        file_path = raw_input("'tile' file path: ")
    
        # In this case, file_parser() should return iterable data structure (later we will access tiles[i])
        tiles = self.parse_file(file_path)
    
        num_of_players = raw_input("number of players (1-4): ")
    
        for i in xrange(int(num_of_players)):
            pid = i + 1
            player_name, is_human = raw_input("player " + str(pid) + " name: "), raw_input("Human player (y/n): ")
            p_tiles = tiles[i * 7:(i + 1) * 7]
            p_tiles.sort(key = lambda t : t[0])
            player_tiles = [Tile(t[1], t[2]) for t in p_tiles]
            self.add_player(pid, player_name, True if is_human == 'y' else False,
                            raw_input("Computer skill: Easy (e), Medium (m): ") if is_human == 'n' else "", player_tiles)
        self.ds = DoubleSix([Tile(t[1], t[2]) for t in tiles[(i + 1) * 7:]])
            
def main():
    game = Game()
    game.setup()
    game.play()
    

if __name__ == "__main__":
    main()
