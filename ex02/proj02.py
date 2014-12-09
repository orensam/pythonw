CHOOSE_ACTION = "Choose action: Tile (t) or Draw (d): "
ILLEGAL_MOVE = "Error: Illegal move"


class Tile:
        
    def __init__(self, pos, right, left):
        self.pos = pos
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        return self.pos < other.pos
        
class DoubleSix:    
    def __init__(self, tiles):
        self.tiles = tiles[:]
        
class LOP:
    
    def __init__(self):
        self._tiles = []
    
    def get_start(self):
        return self._tiles[0]
    
    def get_end(self):
        return self._tiles[-1]

class Player(object):
    
    def __init__(self, pid, name, tiles):
        self._id = pid
        self._name = name
        self.tiles = tiles
        tiles.sort()

class HumanPlayer(Player):    
    def __init__(self, pid, name, skill, tiles):
        super(HumanPlayer, self).__init__(pid, name, tiles)
    
class CompPlayer(Player):    
    def __init__(self, pid, name, tiles):
        super(HumanPlayer, self).__init__(pid, name, tiles)

class CompPlayerEasy(CompPlayer):
    def __init__(self, pid, name, tiles):
        super(CompPlayerEasy, self).__init__(pid, name, tiles)

class CompPlayerMedium(CompPlayer):
    def __init__(self, pid, name, tiles):
        super(CompPlayerMedium, self).__init__(pid, name, tiles)    
        
        
class Game:
    
    def __init__(self):
        self.n_players = 0
        self._players = {}
    
    def line_to_tiles(self, line):
        tiles = []
        tile_strs = [x.strip() for x in line.split('-')]
        for ts in tile_strs:
            tints = ts.split(',')
            tiles.append(Tile(tints[0], tints[1], tints[2]))
            
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
        
               

    def add_player(self, pid, name, is_human, skill, tiles):
        if is_human:
            self.players[pid] = HumanPlayer(pid, name, tiles)
        elif skill == 'e':
            self.players[pid] = CompPlayerEasy(pid, name, tiles)
        else:
            self.players[pid] = CompPlayerMedium(pid, name, tiles)
        self.n_players += 1
    
    def game_over(self):
        pass
    
    def play(self):
        
        for player in self._players:
            if self.game_over():
                break
            if not self.can_play(player.pid):
                continue
            
            
            
        
    def setup(self):
        print "Welcome to Domino!"
    
        file_path = raw_input("'tile' file path: ")
    
        # In this case, file_parser() should return iterable data structure (later we will access tiles[i])
        tiles = self.parse_file(file_path)
    
        num_of_players = raw_input("number of players (1-4): ")
    
        for i in xrange(int(num_of_players)):
            pid = i + 1
            player_name, is_human = raw_input("player " + str(pid) + "name: "), raw_input("Human player (y/n): ")
            self.add_player(pid, player_name, is_human,
                            raw_input("Computer skill: Easy (e), Medium (m): ") if is_human == 'n' else "", tiles[i * 7:(i + 1) * 7])
        
        self.deck = DoubleSix(tiles[(i + 1) * 7:])
            
def print_choose_tile(tiles_num):
    print "Choose tile (1-" + tiles_num + "), and place (Start - s, End - e): "


def print_win(player_id, player_name):
    print "Player " + str(player_id) + ", " + player_name + " wins!"


def print_draw():
    print "It's a draw!"


def print_step(player_id, player_name, player_hand, lop):
    print "\nTurn of " + player_name + " to play, player " + str(player_id) + ":"
    print "Hand :: "  # + "[firstTileLow:firstTileHigh] [secondTileLow:secondTileHigh] ..."
    print "LOP  :: "  # + "[startEdgeTile:startEdgeTile] ... [endEdgeTile:endEdgeTile]"




def main():
    game = Game()
    game.setup()
    

if __name__ == "__main__":
    main()
