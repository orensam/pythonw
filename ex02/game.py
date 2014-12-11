from tile import Tile, LOP, DoubleSix
from players import HumanPlayer, CompPlayerEasy, CompPlayerMedium

WELCOME = "Welcome to Domino!"
GET_PATH = "'tile' file path: "
GET_N_PLAYERS = "number of players (1-4): "
DRAW = "It's a draw!"
GET_COMP_SKILL = "Computer skill: Easy (e), Medium (m): "
GET_PLAYER_NAME = "player %s name: "
GET_IS_HUMAN = "Human player (y/n): "
PLAYER_WON = "Player %s, %s wins!"
YES = 'y'
NO = 'n'


HAND_SIZE = 7
DECK_SIZE = 28


class Game:

    LOP_START = 's'
    LOP_END = 'e'

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

    def can_put_tile_at_pos(self, tile, pos):
        if self.lop.empty():
            return True
        elif pos == self.LOP_START:
            return self.lop.get_start() in (tile.left, tile.right)
        elif pos == self.LOP_END:
            return self.lop.get_end() in (tile.left, tile.right)

    def can_put_num_at_pos(self, num, pos):
        if self.lop.empty():
            return True
        elif pos == self.LOP_START:
            return self.lop.get_start() == num
        elif pos == self.LOP_END:
            return self.lop.get_end() == num

    def add_tile_at_pos(self, tile, pos):
        if pos == self.LOP_START:
            self.lop.add_at_start(tile)
        elif pos == self.LOP_END:
            self.lop.add_at_end(tile)
    
    def get_lop_stats(self):
        return self.lop.get_stats()

    def get_lop_size(self):
        return self.lop.get_len()

    def get_lop_start(self):
        return self.lop.get_start()

    def get_lop_end(self):
        return self.lop.get_end()
    
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
            if self.can_put_tile_at_start(t) or self.can_put_tile_at_end(t):
                return True
        return not self.ds.empty()

    def step(self, pid, is_first_move):
        p = self.get_player(pid)
        if is_first_move:
            p.first_move()
        else:
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
        is_first_move = True
        for pid in self.player_iter():
            self.step(pid, is_first_move)
            is_first_move = False
            if self.player_won(pid):
                print
                print PLAYER_WON %(str(pid), self.get_player(pid).name)
                return
        # If no player won and iteration ended,
        # It means no player can play, i.e draw
        print DRAW


    
    def setup(self):
        print WELCOME

        file_path = raw_input(GET_PATH)

        # In this case, file_parser() should return iterable data structure (later we will access tiles[i])
        tiles = self.parse_file(file_path)

        num_of_players = raw_input(GET_N_PLAYERS)

        for i in xrange(int(num_of_players)):
            pid = i + 1
            player_name, is_human = raw_input(GET_PLAYER_NAME %str(pid)), raw_input(GET_IS_HUMAN).lower()
            p_tiles = tiles[i * HAND_SIZE:(i + 1) * HAND_SIZE]
            p_tiles.sort(key = lambda t : t[0])
            player_tiles = [Tile(t[1], t[2]) for t in p_tiles]
            self.add_player(pid, player_name, True if is_human == YES else False,
                            raw_input(GET_COMP_SKILL) if is_human == NO else "", player_tiles)
        self.ds = DoubleSix([Tile(t[1], t[2]) for t in tiles[(i + 1) * HAND_SIZE:]])
