CHOOSE_ACTION = "Choose action: Tile (t) or Draw (d): "
ILLEGAL_MOVE = "Error: Illegal move"


class Tile:
    
    def __init__(self, pos, right, left):
        self.pos = pos
        self.right = right
        self.left = left
        
    


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
        self.tiles = sorted(tiles, key = lambda tile : tile.pos)
        

class HumanPlayer(Player):
    
    def __init__(self, pid, name, skill, tiles):
        super(HumanPlayer, self).__init__(pid, name, tiles)
    
class CompPlayer(Player):
    
    def __init__(self, pid, name, tiles, skill):
        super(HumanPlayer, self).__init__(pid, name, tiles)
        self._skill = skill
        
        
class Game:
    def __init__(self):
        self._players = {}

    def parse_file(self, file_path):
        lines = open(file_path).readlines()
        
        is_big_comment = False
        is_docstring = False
        res = []
        
        for line in lines:
            
            new_line = ""
            
            while line:                
                
                # Handle big comments
                if is_big_comment:
                    idx = line.find('*/')
                    if idx >= 0:
                        line = line[idx+2:] 
                        is_big_comment = False
                    else:
                        new_line = ""

                elif is_docstring:
                    idx = line[3:].find('"""')
                    if idx >= 0:
                        line = line[idx+3:]
                        is_docstring = False
                    else:
                        new_line = ""

                elif line.startswith('/**', '/*'):
                    is_big_comment = True     
                
                elif line.startswith('"""'):
                    line = line[3:]
                    is_docstring = True
                
                else:                    
                    # Handle regular comments
                    c = line.find('#')
                    if c >= 0:
                        new_line = line[:c]
                        line = ""
                    
                    c = line.find('//')
                    if c >= 0:
                        new_line = line[:c]
                        line = ""
                
                    new_line = line
                
            if new_line:
                res.append(new_line)
               

    def add_player(self, pid, name, is_human, skill, tiles):
        if is_human:
            self.players[pid] = HumanPlayer(pid, name, tiles)
        else:
            self.players[pid] = CompPlayer(pid, name, tiles, skill)
        

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
