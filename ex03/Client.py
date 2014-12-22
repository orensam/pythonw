__author__ = 'Alon Ben-Shimol'

import socket
import select
import sys
import Protocol
from Board import PlayerBoard, EnemyBoard, Ship

EXIT_ERROR = 1
BOARD_SIZE = 10

SHOOT_PREFIX = "SHOOT|"
HIT_PREFIX = "HIT|"
MISS_PREFIX = "MISS|"
SINK_PREFIX = "SINK|"
ILOST_PREFIX = "ILOST|"
YOUWON_PREFIX = "YOU_WON|"

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
        
        
        """
        DO NOT CHANGE
        If you want to run you program on windowns, you'll
        have to temporarily remove this line (but then you'll need
        to manually give input to your program). 
        """
        self.all_sockets.append(sys.stdin)  # DO NOT CHANGE
    
    def parse_ships(self, fn):
        with open(fn) as f:
            for line in f.readlines():
                self.board.add_ship(Client.coords_to_nums_list(line, ','))
                                
    @staticmethod
    def coord_to_nums(s, with_space = False):
        if with_space:
            slist = s.split()
        else:
            slist = [s[0], s[1:]]
        return ord(slist[0]) - 65, int(slist[1]) - 1
    
    @staticmethod
    def nums_to_coord(row, col):
        return '%s %d' %(chr(row + 65), )
    
    @staticmethod
    def nums_list_to_coords(positions, sep = '|'):
        return sep.join([Client.nums_to_coord(row, col) for row, col in positions])
    
    @staticmethod
    def coords_to_nums_list(coords, sep = '|'):
        return [Client.coord_to_nums(s) for s in coords.split(sep)]
    
    def connect_to_server(self):

        # Create a TCP/IP socket_to_server
        try:
            self.socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:

            self.socket_to_server = None
            print msg
            exit(EXIT_ERROR)

        server_address = (self.server_name, int(self.server_port))
        try:
            self.socket_to_server.connect(server_address)
            self.all_sockets.append(self.socket_to_server)  # this will allow us to use Select System-call

        except socket.error as msg:
            self.socket_to_server.close()
            self.socket_to_server = None
            print msg
            exit(EXIT_ERROR)

        # we wait to get ok from server to know we can send our name
        num, msg = Protocol.recv_all(self.socket_to_server)
        if num == Protocol.NetworkErrorCodes.FAILURE:
            print msg
            self.close_client()

        if num == Protocol.NetworkErrorCodes.DISCONNECTED:
            print "Server has closed connection."
            self.close_client()

        # send our name to server
        eNum, eMsg = Protocol.send_all(self.socket_to_server, sys.argv[3])
        if eNum:
            print eMsg
            self.close_client()

        # TODO - maybe the client should send more information to the server?
        # it is up to you. 

        print "*** Connected to server on %s ***" % server_address[0] 
        print
        print "Waiting for an opponent..."
        print


    def close_client(self):
        
        # TODO - implement 
        
        print
        print "*** Goodbye... ***"


    def __handle_standard_input(self):
        
        msg = sys.stdin.readline().strip().upper()
        
        if msg == 'EXIT':  # user wants to quit
            self.close_client()
                
        else:
            # Send letter and number
            self.send_shoot(msg)
            self.sent_row, self.sent_col = Client.coord_to_nums(msg)            

    def __handle_server_request(self):
        
        num, msg = Protocol.recv_all(self.socket_to_server)
        if num == Protocol.NetworkErrorCodes.FAILURE:
            print msg
            self.close_client()

        if num == Protocol.NetworkErrorCodes.DISCONNECTED:
            print "Server has closed connection."
            self.close_client()
            
            
        if msg.startswith('start'):
            self.__start_game(msg)
        
        #elif msg.startswith('game|turn'):
        #    print "It's your turn..."
        
        # Other player's turn - recieve shot, return shot result
        elif msg.startswith(SHOOT_PREFIX):
            
            coord = msg[len(SHOOT_PREFIX):]
            print "%s plays %s" %(self.opponent_name, coord)
            
            row, col = Client.coord_to_nums(coord)
            
            if self.board.is_ship(row, col):
                self.board.add_hit(row, col)
                sunk_ship_perimeter = self.board.pop_sunk_ship()
                if sunk_ship_perimeter:
                    self.send_sink(sunk_ship_perimeter)
                    if self.board.lost():                        
                        print "You lost :("                        
                        self.send_lost()
                        return
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

    
    def send_to_server(self, msg):
        Protocol.send_all(self.socket_to_server, msg)
        
    def send_hit(self):
        self.send_to_server(HIT_PREFIX)
    
    def send_miss(self):
        self.send_to_server(MISS_PREFIX)
        
    def send_shoot(self, coord):
        self.send_to_server(SHOOT_PREFIX + coord)
    
    def send_sink(self, positions):
        positions_str = Client.nums_list_to_coords(positions)
        self.send_to_server(SINK_PREFIX + positions_str)
    
    def send_lost(self):
        self.send_to_server(ILOST_PREFIX)
        
    def __start_game(self, msg):
        
        print "Welcome " + self.player_name + "!"
        
        self.opponent_name = msg.split('|')[2]
        print "You're playing against: " + self.opponent_name + ".\n"
        
        self.print_board()
        if "not_turn" in msg: return
        
        print "It's your turn..."
            
    letters = list(map(chr, range(65, 65 + BOARD_SIZE)))
        
    def print_board(self):
        """
        TODO: use this method for the prints of the board. You should figure
        out how to modify it in order to properly display the right boards.
        """
        print
        print "%s %59s" % ("My Board:", self.opponent_name + "'s Board:"),

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
                print "%-3s" % self.board[i,j],

            print(" |||   "),
            print "%-3s" % Client.letters[i],
            for j in range(BOARD_SIZE):
                print "%-3s" % self.enemy_board[i,j],

            print
        
        print
         




    def run_client(self):

        while True:

            r_sockets = select.select(self.all_sockets, [], [])[0]  # We won't use writable and exceptional sockets

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
