__author__ = 'Alon Ben-Shimol'

import socket
import select
import sys
import Protocol
from Board import PlayerBoard, EnemyBoard, Ship

EXIT_ERROR = 1
EXIT_OK = 0
BOARD_SIZE = 10

SHOOT_PREFIX = "SHOOT|"
HIT_PREFIX = "HIT|"
MISS_PREFIX = "MISS|"
SINK_PREFIX = "SINK|"
SINKLOST_PREFIX = "SINKLOST|"
OP_DISC_PREFIX = "OPDISC|"
CLOSE_PREFIX = "CLOSE|"
QUIT_PREFIX = "QUIT|"


class Client:

    def __init__(self, s_name, s_port, player_name, ships_file_name):

        self.server_name = s_name
        self.server_port = s_port

        self.player_name = player_name
        self.opponent_name = ""

        self.socket_to_server = None

        self.all_sockets = []

        self.board = PlayerBoard(BOARD_SIZE)
        self.enemy_board = EnemyBoard(BOARD_SIZE)

        self.parse_ships(ships_file_name)
        self.sent_row = 0
        self.sent_col = 0

        self.all_sockets.append(sys.stdin)  # DO NOT CHANGE

    def parse_ships(self, fn):
        with open(fn) as f:
            for line in f.readlines():
                self.board.add_ship(Client.coords_to_nums_list(line, ','))

    @staticmethod
    def coord_to_nums(s, with_space=False):
        if with_space:
            slist = s.split()
        else:
            slist = [s[0], s[1:]]
        return ord(slist[0]) - 65, int(slist[1]) - 1

    @staticmethod
    def nums_to_coord(row, col):
        return '%s %d' % (chr(row + 65), col + 1)

    @staticmethod
    def nums_list_to_coords(positions, sep='|'):
        return sep.join([Client.nums_to_coord(row, col)
                         for row, col in positions])

    @staticmethod
    def coords_to_nums_list(coords, sep='|'):
        return [Client.coord_to_nums(s) for s in coords.split(sep)]

    def connect_to_server(self):

        # Create a TCP/IP socket_to_server
        try:
            self.socket_to_server = socket.socket(socket.AF_INET,
                                                  socket.SOCK_STREAM)
        except socket.error as msg:

            self.socket_to_server = None
            sys.stderr.write(repr(msg) + '\n')
            exit(EXIT_ERROR)

        server_address = (self.server_name, int(self.server_port))
        try:
            self.socket_to_server.connect(server_address)
            # this will allow us to use Select System-call
            self.all_sockets.append(self.socket_to_server)

        except socket.error as msg:
            self.socket_to_server.close()
            self.socket_to_server = None
            sys.stderr.write(repr(msg) + '\n')
            exit(EXIT_ERROR)

        # we wait to get ok from server to know we can send our name
        self.rcv_from_server()

        # send our name to server
        self.send_to_server(self.player_name)

        print "*** Connected to server on %s ***" % server_address[0]
        print
        print "Waiting for an opponent..."
        print

    def close_client(self, code):
        self.socket_to_server.shutdown(socket.SHUT_RDWR)
        self.socket_to_server.close()
        print
        print "*** Goodbye... ***"
        exit(code)

    def __handle_standard_input(self):

        msg = sys.stdin.readline().strip().upper()

        if msg == 'EXIT':  # user wants to quit
            self.send_quit()
            self.close_client(EXIT_OK)

        else:
            # Send letter and number
            self.send_shoot(msg)
            self.sent_row, self.sent_col = Client.coord_to_nums(msg)

    def __handle_server_request(self):

        msg = self.rcv_from_server()

        if msg.startswith('start'):
            self.__start_game(msg)

        # Other player's turn - recieve shot, return shot result
        elif msg.startswith(SHOOT_PREFIX):

            coord = msg[len(SHOOT_PREFIX):]
            print "%s plays: %s" % (self.opponent_name, coord)

            row, col = Client.coord_to_nums(coord)

            is_hit = self.board.enemy_shot(row, col)

            if is_hit:
                sunk_ship_perimeter = self.board.pop_sunk_ship()
                if sunk_ship_perimeter:
                    is_lost = self.board.lost()
                    self.send_sink(sunk_ship_perimeter, is_lost)
                    if is_lost:
                        self.print_board()
                        print "You lost :("
                        self.close_client(EXIT_OK)
                else:
                    self.send_hit()
            else:
                self.board.add_miss(row, col)
                self.send_miss()

            self.print_board()
            print "It's your turn..."

        elif msg.startswith(HIT_PREFIX):
            # Enemy confirmed hit, put it on my representation of his board
            self.enemy_board.add_hit(self.sent_row, self.sent_col)
            self.print_board()

        elif msg.startswith(MISS_PREFIX):
            # Enemy confirmed miss, put it on my representation of his board
            self.enemy_board.add_miss(self.sent_row, self.sent_col)
            self.print_board()

        elif msg.startswith(SINK_PREFIX):
            # Enemy confirmed hit and sunk ship.
            # Put hit on my representation of his board, and add the sent
            # perimeter positions as misses
            coords = msg[len(SINK_PREFIX):]
            self.enemy_board.add_hit(self.sent_row, self.sent_col)
            for row, col in Client.coords_to_nums_list(coords):
                self.enemy_board.add_miss(row, col)
            self.print_board()

        elif msg.startswith(SINKLOST_PREFIX):
            coords = msg[len(SINKLOST_PREFIX):]
            self.enemy_board.add_hit(self.sent_row, self.sent_col)
            for row, col in Client.coords_to_nums_list(coords):
                self.enemy_board.add_miss(row, col)
            self.print_board()
            print "You won!"
            self.close_client(EXIT_OK)

        elif msg.startswith(OP_DISC_PREFIX):
            print "Your opponent has disconnected. You win!"
            self.close_client(EXIT_OK)

    def rcv_from_server(self):

        err_num, msg = Protocol.recv_all(self.socket_to_server)

        if err_num == Protocol.NetworkErrorCodes.FAILURE:
            sys.stderr.write(msg)
            self.close_client(EXIT_ERROR)

        elif err_num == Protocol.NetworkErrorCodes.DISCONNECTED:
            print "Server has closed connection."
            self.close_client(EXIT_OK)

        else:
            return msg

    def send_to_server(self, msg):

        err_num, err_msg = Protocol.send_all(self.socket_to_server, msg)

        if err_num == Protocol.NetworkErrorCodes.FAILURE:
            print err_msg
            self.close_client(EXIT_ERROR)

        if err_num == Protocol.NetworkErrorCodes.DISCONNECTED:
            print "Server has closed connection."
            self.close_client(EXIT_OK)

    def send_hit(self):
        self.send_to_server(HIT_PREFIX)

    def send_miss(self):
        self.send_to_server(MISS_PREFIX)

    def send_shoot(self, coord):
        self.send_to_server(SHOOT_PREFIX + coord)

    def send_sink(self, positions, is_lost):
        prefix = SINK_PREFIX
        if is_lost:
            prefix = SINKLOST_PREFIX
        positions_str = Client.nums_list_to_coords(positions)
        self.send_to_server(prefix + positions_str)

    def send_quit(self):
        self.send_to_server(QUIT_PREFIX)

    def __start_game(self, msg):
        print "Welcome " + self.player_name + "!"
        self.opponent_name = msg.split('|')[2]
        print "You're playing against: " + self.opponent_name + ".\n"
        self.print_board()
        if "not_turn" in msg:
            return
        print "It's your turn..."

    letters = list(map(chr, range(65, 65 + BOARD_SIZE)))

    def print_board(self):
        """
        Prints the boards of the player and the oponent.
        """
        print
        print "%s %56s" % ("My Board:", self.opponent_name + "'s Board:"),

        print
        print "%-3s" % "",
        for i in range(BOARD_SIZE):
            print "%-3s" % str(i+1),

        print(" |||   "),
        print "%-3s" % "",
        for i in range(BOARD_SIZE):
            print "%-3s" % str(i+1),

        print

        for i in range(BOARD_SIZE):
            print "%-3s" % Client.letters[i],
            for j in range(BOARD_SIZE):
                print "%-3s" % self.board[i, j],

            print(" |||   "),
            print "%-3s" % Client.letters[i],
            for j in range(BOARD_SIZE):
                print "%-3s" % self.enemy_board[i, j],
            print

        print

    def run_client(self):
        while True:
            # We won't use writable and exceptional sockets
            r_sockets = select.select(self.all_sockets, [], [])[0]
            if sys.stdin in r_sockets:
                self.__handle_standard_input()
            elif self.socket_to_server in r_sockets:
                self.__handle_server_request()


def main():
    client = Client(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])
    client.connect_to_server()
    client.run_client()

if __name__ == "__main__":
    main()
