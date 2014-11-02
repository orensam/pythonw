#! /usr/bin/python

"""
This is a multi-blackjack game, where the player tries to create
blackjack hands worth as many points as possible on a board with
a special array of rows and colums.
"""

from cards import Deck

class Tableau(object):
    """
    This class represents the tableau - the game's playing board.
    Its interface allows getting and setting cards in the different positions,
    and calculate the simple and advanced score values.
    """
    
    # Board positions
    start = 1
    board_end = 16
    end = 20
    
    # Points and values
    __point_dict = {17:2, 18:3, 19:4, 20:5, 21:7}
    __point_dict.update({i:1 for i in xrange(17)})
    __bust_score = 0
    __blackjack_score = 10
    __blackjack_value = 21
    __ace_base_val = 1
    __ace_alt_val = 11
    __hands = ([1,2,3,4,5], [6,7,8,9,10], [11,12,13], [14,15,16], \
               [1,6], [2,7,11,14], [3,8,12,15], [4,9,13,16], [5,10])

    def __init__(self):
        """ Initialize an empty tableau """
        self._spots = [Spot(i) for i in xrange(self.start, self.end + 1)]
    
    def __str__(self):
        """ Print the tableau according to spec """
        s = ""
        s += "%4s %4s %4s %4s %4s" %tuple(self._spots[:5]) + '\n'
        s += "%4s %4s %4s %4s %4s" %tuple(self._spots[5:10]) + '\n'
        s += "%9s %4s %4s"%tuple(self._spots[10:13]) + '\n'
        s += "%9s %4s %4s"%tuple(self._spots[13:16])
        return s

    def __getitem__(self, pos):
        """ Return the wanted tableau position(s) """
        if isinstance(pos, slice):
            return self._spots[pos.start - 1 : pos.stop - 1]
        return self._spots[pos - 1]
    
    def __setitem__(self, pos, card):
        """ Set position pos to given card """
        self._spots[pos - 1] = card
    
    def calc_score_simple(self):
        """ Calculate the simple score """
        return sum([self._calc_hand_score_simple(hand) for hand in self.__hands])
    
    def _get_hand_values(self, hand, values):
        """ Get the card values of the hand, from the given value list"""
        return [values[i-1] for i in hand]
        
    def _calc_hand_score_simple(self, hand):
        """ Hand score calculation for use in the simple algorithm """
        
        hand_values = self._get_hand_values(hand, self._to_values())
        regular_score = self._calc_score_from_values(hand_values)        
        ace_bonus_score = 0
        
        if self.__ace_base_val in hand_values:
            # We'd want no more than one ace in the hand to count as 11.
            # Therefore if there's an ace, we want to try and switch it to 11 and re-calculate. 
            pos = hand_values.index(self.__ace_base_val)        
            hand_values[pos] = self.__ace_alt_val
            ace_bonus_score = self._calc_score_from_values(hand_values)
            
        return max(regular_score, ace_bonus_score)

    def calc_score_advanced(self):
        """ Calculate the advanced score """
        
        possible_scores = []        
        for values_option in self._gen_value_options(self._to_values()):
            # Iterate the possible value arrays, and return the maximum possible.
            score = sum([self._calc_hand_score_advanced(hand, values_option) for hand in self.__hands])
            possible_scores.append(score)
        return max(possible_scores)
        
    def _calc_hand_score_advanced(self, hand, values):        
        """
        Given a value list and a hand (positions in the value list),
        calculate the score of the hand, for the advanced algorithm.
        """
        hand_values = self._get_hand_values(hand, values)
        return self._calc_score_from_values(hand_values)        

    def _gen_value_options(self, values):
        """
        Generates the possible value arrays from the given value list.
        i.e genrates all the combinations of value lists for the two ace values.
        e.g if values is [1,3,1], the output will be [ [1,3,1], [1,3,11], [11,3,1], [11,3,11] ]
        """
        if len(values) == 0:
            yield []
        else:
            for val in self._gen_value_options(values[1:]):
                yield [values[0]] + val
                if values[0] == self.__ace_base_val:
                    yield [self.__ace_alt_val] + val
        
    def _calc_score_from_values(self, values):
        """ Given a list of values, calculate the resulting score """
        tot = sum(values)
        if tot > self.__blackjack_value:
            return self.__bust_score
        elif tot == self.__blackjack_value and len(values) == 2:
            return self.__blackjack_score
        else:
            return self.__point_dict[tot]
    
    def _to_values(self):
        """ Return the list of (base) values of the tableau """
        return [self[i].get_value() for i in xrange(self.start, self.board_end + 1)]

    def pos_full(self, pos):
        """ Return True iff position pos is occupied """
        return bool(self[pos])
    
    def is_full(self):
        for i in xrange(self.start, self.board_end + 1):
            if not self.pos_full(i):
                return False
        return True
                
            
class Spot(object):
    """ Represents a spot on the tableau """
    
    def __init__(self, pos, card = None):
        """ Initializes the spot with position pos and given card (None for empty spot) """
        self.pos = pos
        self.card = card

    def __str__(self):
        """ Returns the string representation of the spot """
        if self.card:
            return str(self.card)
        return str(self.pos)
    
    def __nonzero__(self):
        """ Returns True iff the spot is occupied """
        return self.card is not None
    
    def get_value(self):
        """ Returns the value at this spot (0 for no card) """
        if self.card:
            return self.card.get_value()
        return 0
        
class Game(object):
    """
    Handler for the game progress.
    """
    
    # Messages
    __str_cards = "Tableau:\n%s\n\nDiscards: %4s %4s %4s %4s\n"
    __str_option_draw = "d - draw a card"
    __str_option_simple = "s - simple calculation"
    __str_option_advanced = "a - advanced calculation"
    __str_option_quit = "q - quit"
    __str_choose = "Choose an option"
    __str_options_all =  "%s: %s, %s, %s, %s: " % (__str_choose, __str_option_draw, __str_option_simple, \
                                                   __str_option_advanced, __str_option_quit)
    __str_options_short = "%s: %s, %s, %s: " % (__str_choose, __str_option_simple, __str_option_advanced, \
                                                __str_option_quit)

    __str_calc_simple = "The total score (simple algorithm) is: %2s"
    __str_calc_advanced = "The total score (advanced algorithm) is: %2s"
    __str_card_dealt = "Card dealt: %4s"
    __str_choose_loc = "Choose location (1 - 20) to place the new card: "
    
    # Error messages
    __str_err_nint = "Error: input is not an integer"
    __str_err_oor = "Error: input is out of range"
    __str_err_pos_full = "Error: a card was already placed in this spot"
    __str_err_invalid_choice = "Error: an invalid choice was made"
    
    # Options for the player
    __option_quit = "Qq"
    __option_deal = "Dd"
    __option_calc_simple = "Ss"
    __option_calc_advanced = "Aa"
    
    def __init__(self):
        """ Initializes the game """
        self._deck = Deck()
        self._deck.shuffle()
        self._tableau = Tableau()

    def play(self):
        """ Starts the game """
        
        self._print_cards()
        
        while True:
            
            # Ask user what to do
            if self._tableau.is_full():
                inp = raw_input(self.__str_options_short)
            else:
                inp = raw_input(self.__str_options_all)
            
            if len(inp) == 0:
                print self.__str_err_invalid_choice
            elif inp in self.__option_quit:
                break;
            elif inp in self.__option_deal:
                self._play_step()
                print
                self._print_cards()
            elif inp in self.__option_calc_simple:
                print self.__str_calc_simple % self._tableau.calc_score_simple()
            elif inp in self.__option_calc_advanced:
                print self.__str_calc_advanced % self._tableau.calc_score_advanced()
            else:
                print self.__str_err_invalid_choice
    
    def _print_cards(self):
        """ Prints the game board and discards """
        discards = tuple(self._tableau[self._tableau.board_end + 1 : self._tableau.end + 1])
        print self.__str_cards % ((self._tableau,) + discards)
    
    def _play_step(self):
        """ One step of the game - deal card and place it """
        card = self._deck.deal()
        print self.__str_card_dealt % card
        pos = self._get_pos_from_user()
        self._tableau[pos] = card

    def _get_pos_from_user(self):
        """ Get a (valid) board position from the user """
        
        while True:
            # Iterate until value is valid
            inp = raw_input(self.__str_choose_loc)

            try:
                pos = int(inp)
            except ValueError:
                print self.__str_err_nint
                continue

            if pos < self._tableau.start or pos > self._tableau.end:
                print self.__str_err_oor
                continue

            if self._tableau.pos_full(pos):
                print self.__str_err_pos_full 
                continue

            return pos

if __name__=="__main__":
    g = Game()
    g.play()
    
    