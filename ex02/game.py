"""
Game module - contains all the main logic of the domino game.
"""

# project imports
from tile import Tile, LOP, DoubleSix
from players import HumanPlayer, CompPlayerEasy, CompPlayerMedium

# Game start strings
WELCOME = "Welcome to Domino!"
GET_PATH = "'tile' file path: "
GET_N_PLAYERS = "number of players (1-4): "
GET_PLAYER_NAME = "player %s name: "
GET_IS_HUMAN = "Human player (y/n): "
GET_COMP_SKILL = "Computer skill: Easy (e), Medium (m): "

# Turn strings
TURN_STR = "Turn of %s to play, player %d:"
HAND_STR = "Hand :: %s"
LOP_STR = "LOP  :: %s"

# Game end strings
DRAW = "It's a draw!"
PLAYER_WON = "Player %s, %s wins!"

# Input chars
COMP_SKILL_EASY = 'e'
COMP_SKILL_MEDIUM = 'm'
YES = 'y'
NO = 'n'


class Game:
    """
    Class for the Domino game.
    Holds all the game info, and runs the game's logic
    """

    # Configurables
    LOP_START = 's'
    LOP_END = 'e'
    HAND_SIZE = 7
    DECK_SIZE = 28

    def __init__(self):
        """
        Initialize a new, empty game.
        :return:
        """
        self.n_players = 0
        self._players = {}
        self.lop = LOP()
        self.ds = DoubleSix([])

    def line_to_tiles(self, line):
        """
        Return a list of 3-tuples.
        Each tuple represents a Tile: position, left, right.
        Helper for parse_file()
        """
        tiles = []
        tile_strs = [x.strip() for x in line.split('-')]
        for ts in tile_strs:
            tints = [int(x) for x in ts.split(',')]
            tiles.append((tints[0], tints[1], tints[2]))
        return tiles

    def parse_file(self, file_path):
        """
        Parses the given *.tile file into a list of tiles.
        """
        lines = open(file_path).readlines()
        is_big_comment = False
        is_docstring = False
        res = []

        for line in lines:
            line = line.strip()
            # Handle single line
            new_line = ""
            while line:
                # Inside multiline comment
                if is_big_comment:
                    idx = line.find('*/')
                    if idx >= 0:
                        line = line[idx + 2:]
                        is_big_comment = False
                    else:
                        break

                # Inside docstring
                elif is_docstring:
                    idx = line.find('"""')
                    if idx >= 0:
                        line = line[idx + 3:]
                        is_docstring = False
                    else:
                        break

                # Check for multiline comment
                elif line.startswith(('/**', '/*')):
                    is_big_comment = True

                # Check for docstring
                elif line.startswith('"""'):
                    line = line[3:]
                    is_docstring = True

                # Check for single line comments
                elif line.startswith(('//', '#')):
                    break

                # line starts with actual data, get data until next comment
                else:
                    com_start = {line.find('#'), line.find('//'),
                                 line.find('/*'), line.find('/**'),
                                 line.find('"""')}
                    com_start.remove(-1)
                    if com_start:
                        idx = min(com_start)
                        new_line += line[:idx]
                        line = line[idx:]
                    else:
                        new_line = line
                        line = ""

            # Add the new line
            new_line = new_line.strip()
            if new_line:
                res.append(new_line)
                # end handle single line

        # Turn line to actual tiles
        tiles = []
        for line in res:
            tiles += self.line_to_tiles(line)

        return tiles

    def can_put_tile_at_pos(self, tile, pos):
        """
        Returns True iff it is legal to put the given tile
        in position pos of the LOP.
        """
        return self.can_put_num_at_pos(tile.left, pos) \
               or self.can_put_num_at_pos(tile.right, pos)

    def can_put_num_at_pos(self, num, pos):
        """
        Returns True iff it is legal to put the given number
         in position pos of the LOP
        """
        if self.lop.empty():
            return True
        elif pos == self.LOP_START:
            return self.lop.get_start() == num
        elif pos == self.LOP_END:
            return self.lop.get_end() == num

    def add_tile_at_pos(self, tile, pos):
        """
        Adds the given tile in position pos of the LOP
        """
        if pos == self.LOP_START:
            self.lop.add_at_start(tile)
        elif pos == self.LOP_END:
            self.lop.add_at_end(tile)

    def get_lop_stats(self):
        """
        Returns the LOP statistics
        """
        return self.lop.get_stats()

    def get_lop_size(self):
        """
        Returns the LOP size
        """
        return self.lop.get_size()

    def get_lop_start(self):
        """
        Returns the LOP starting number
        """
        return self.lop.get_start()

    def get_lop_end(self):
        """
        Returns the LOP ending number
        """
        return self.lop.get_end()

    def add_player(self, pid, name, is_human, skill, tiles):
        """
        Adds the player with id pid and given name to the game.
        is_human specifies human/computer player, skill is easy or medium
        (for computer players) and tiles is the the player's initial tiles.
        """
        if is_human:
            self._players[pid] = HumanPlayer(pid, name, tiles, self)
        elif skill == COMP_SKILL_EASY:
            self._players[pid] = CompPlayerEasy(pid, name, tiles, self)
        elif skill == COMP_SKILL_MEDIUM:
            self._players[pid] = CompPlayerMedium(pid, name, tiles, self)
        self.n_players += 1

    def draw_from_deck(self):
        """
        Draws a tile from the DoubleSix deck.
        """
        return self.ds.draw()

    def get_pids(self):
        """
        Returns a list of the players' pids
        """
        return [pid for pid in self._players]

    def get_player(self, pid):
        """
        Returns the player whose id is pid.
        """
        return self._players[pid]

    def player_won(self, pid):
        """
        Returns True iff player pid has won the game.
        """
        p = self.get_player(pid)
        return len(p.tiles) == 0

    def can_play(self, pid):
        """
        Returns True iff player pid has any legal moves.
        :param pid:
        :return:
        """
        p = self.get_player(pid)
        for tile in p.tiles:
            if self.can_put_tile_at_pos(tile, self.LOP_START) \
                    or self.can_put_tile_at_pos(tile, self.LOP_END):
                return True
        return not self.ds.empty()

    def step(self, pid, is_first_move):
        """
        Performs one step of the game, with player pid.
        is_first_move specifies to use the first move behavior
        of the player.
        """
        p = self.get_player(pid)
        print
        print TURN_STR % (p.name, pid)
        print HAND_STR % p.hand_str()
        print LOP_STR % str(self.lop)
        print
        if is_first_move:
            p.first_move()
        else:
            p.move()

    def chose_first_player(self):
        """
        Returns the pid of the player that will start the game,
        Acoording to the ordering specified in the game description
        :return:
        """
        player_tiles = {pid: self.get_player(pid).get_tile_tups() for pid in
                        self.get_pids()}

        # Choose player with highest double
        for i in range(6, -1, -1):
            for pid, tiles in player_tiles.items():
                if (i, i) in tiles:
                    return pid

        # Choose player with highest sum
        player_max_tile_sum = {pid: max([sum(t) for t in player_tiles[pid]])
                               for
                               pid in player_tiles}
        candidates = []
        cur_max = -1

        for pid, tsum in player_max_tile_sum.items():
            if tsum > cur_max:
                candidates = [pid]
            elif tsum == cur_max:
                candidates.append(pid)

        # Break ties using player names
        cand_names = [(pid, self.get_player(pid).name) for pid in candidates]
        cand_names.sort(key=lambda c: c[1])
        return cand_names[0][0]

    def player_iter(self):
        """
        Iterates the players by pid, and yields each player that can play.
        Exits when
        :return:
        """
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
                print PLAYER_WON % (str(pid), self.get_player(pid).name)
                return
        # If no player won and iteration ended,
        # It means no player can play, i.e draw
        print DRAW

    def setup(self):
        print WELCOME
        file_path = raw_input(GET_PATH)

        # In this case, file_parser() should return iterable data structure
        # (later we will access tiles[i])
        tiles = self.parse_file(file_path)

        num_of_players = raw_input(GET_N_PLAYERS)

        for i in xrange(int(num_of_players)):
            pid = i + 1
            player_name, is_human = raw_input(
                GET_PLAYER_NAME % str(pid)), raw_input(GET_IS_HUMAN).lower()
            p_tiles = tiles[i * self.HAND_SIZE:(i + 1) * self.HAND_SIZE]
            p_tiles.sort(key=lambda t: t[0])
            player_tiles = [Tile(t[1], t[2]) for t in p_tiles]
            self.add_player(pid, player_name,
                            True if is_human == YES else False,
                            raw_input(GET_COMP_SKILL).lower()
                            if is_human == NO else "",
                            player_tiles)
        self.ds = DoubleSix(
            [Tile(t[1], t[2]) for t in tiles[(i + 1) * self.HAND_SIZE:]])
