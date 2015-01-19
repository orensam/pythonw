__author__ = 'orensam'


class ShotResult(object):

    HIT = 'H'
    MISS = 'X'
    SUNK = 'S'


class Ship(object):

    def __init__(self, positions, board_size):
        self.positions = {pos: True for pos in positions}
        self.board_size = board_size
        self.perimeter = set()
        self.set_perimeter()

    def has_pos(self, row, col):
        return row, col in self.positions

    def hit_pos(self, row, col):
        self.positions[(row, col)] = False

    def is_sunk(self):
        return True not in self.positions.values()

    @staticmethod
    def area_cells(row, col):
        return [(row - 1, col - 1), (row - 1, col), (row - 1, col + 1),
                (row, col - 1), (row, col + 1),
                (row + 1, col - 1), (row + 1, col), (row + 1, col + 1)]

    def set_perimeter(self):
        for row, col in self.positions:
            for arow, acol in Ship.area_cells(row, col):
                if (arow, acol) not in self.positions \
                    and 0 <= arow < self.board_size \
                        and 0 <= acol < self.board_size:
                        self.perimeter.add((arow, acol))

    def get_perimeter(self):
        return self.perimeter


class Board(object):

    SHIP = '0'
    HIT = 'H'
    MISS = 'X'
    EMPTY = '*'

    def __init__(self, size):
        self.size = size
        self.places = [[Board.EMPTY] * self.size for i in range(self.size)]

    def __getitem__(self, pos):
        row, col = pos
        return self.places[row][col]

    def __setitem__(self, pos, char):
        row, col = pos
        self.places[row][col] = char

    def add_ship(self, positions):
        ship = Ship(positions, self.size)
        self.ships.append(ship)
        for row, col in positions:
            self[row, col] = Board.SHIP

    def add_hit(self, row, col):
        self[row, col] = Board.HIT

    def add_miss(self, row, col):
        self[row, col] = Board.MISS

    def set_misses_around_ship(self, ship):
        for row, col in ship.get_perimeter():
            self.add_miss(row, col)


class PlayerBoard(Board):

    def __init__(self, size):
        super(PlayerBoard, self).__init__(size)
        self.ships = []

    def is_ship(self, row, col):
        return self[row, col] == Board.SHIP

    def enemy_shot(self, row, col):
        if self.is_ship(row, col):
            self.add_hit(row, col)
            for ship in self.ships:
                if ship.has_pos(row, col):
                    ship.hit_pos(row, col)
            return True
        else:
            self.add_miss(row, col)
            return False

    def pop_sunk_ship(self):
        for ship in self.ships:
            if ship.is_sunk():
                self.ships.remove(ship)
                self.set_misses_around_ship(ship)
                return list(ship.get_perimeter())

    def lost(self):
        return len(self.ships) == 0


class EnemyBoard(Board):

    def sunk_ship(self, ship_positions):
        dummy_ship = Ship(ship_positions)
        self.set_misses_around_ship(dummy_ship)
