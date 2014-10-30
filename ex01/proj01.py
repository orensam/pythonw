#! /usr/bin/python

from cards import Card, Deck

class Tableau(object):
        
    point_dict = {17:2, 18:3, 19:4, 20:5, 21:7}
    point_dict.update({i:1 for i in xrange(17)})
    hands = ([1,2,3,4,5], [6,7,8,9,10], [11,12,13], [14,15,16], [1,6], [2,7,11,14], [3,8,12,15], [4,9,13,16], [5,10])

    
    def __init__(self):
        self.t = [Spot(i) for i in xrange(1,17)]
    
    def __str__(self):
        s = ""
        s += "%4s %4s %4s %4s %4s" %tuple(self.t[:5]) + '\n'
        s += "%4s %4s %4s %4s %4s" %tuple(self.t[5:10]) + '\n'
        s += "%9s %4s %4s"%tuple(self.t[10:13]) + '\n'
        s += "%9s %4s %4s"%tuple(self.t[13:16])
        return s
    
    def __setitem__(self, pos, card):
        self.t[pos - 1] = card
    
    def calc_score_simple(self):        
        return sum([self.calc_hand_score_simple(hand) for hand in self.hands])
    
    def get_hand_values(self, hand, values):
        return [values[i-1] for i in hand]
        
    def calc_hand_score_simple(self, hand):
        hand_values = self.get_hand_values(hand, self.to_values())
        regular_score = self.calc_score_from_values(hand_values)        
        ace_bonus_score = 0
        
        if 1 in hand_values:
            pos = hand_values.index(1)        
            hand_values[pos] = 11
            ace_bonus_score = self.calc_score_from_values(hand_values)
            
        return max(regular_score, ace_bonus_score)

    def calc_score_advanced(self):
        values = self.to_values()
        possible_scores = []
        for values_option in self.gen_value_options(self.to_values()):
            score = sum([self.calc_hand_score_advanced(hand, values_option) for hand in self.hands])
            possible_scores.append(score)
        return max(possible_scores)
        
    def calc_hand_score_advanced(self, hand, values):        
        """
        Given a value list (of length 16) and a hand (positions in the value list),
        calculate the score of the hand.
        """
        hand_values = self.get_hand_values(hand, values)
        return self.calc_score_from_values(hand_values)        

    def gen_value_options(self, values):
       	if len(values) == 0:
            yield []
        else:
            for val in self.gen_value_options(values[1:]):
                yield [values[0]] + val
                if values[0] == 1:
                    yield [11] + val
        
    def calc_score_from_values(self, values):        
        tot = sum(values)
        if tot > 21:
            return 0
        elif tot == 21 and len(values) == 2:
            return 10
        else:
            return self.point_dict[tot]
    
    def to_values(self):
        return [self.t[i].get_value() for i in xrange(len(self.t))]   

            
                                                      
            
class Spot(object):
    
    def __init__(self, pos, card = None):
        self.pos = pos
        self.card = card

    def __str__(self):
        if self.card:
            return str(self.card)
        return str(self.pos)
    
    def __nonzero__(self):
        return self.card is not None
    
    def get_value(self):
        if self.card:
            return self.card.get_value()
        return 0
        
class Game(object):

    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.tableau = Tableau()

    def play(self):
        
        self.tableau[1] = Card(1,'s')
        self.tableau[2] = Card(8,'h')
        self.tableau[6] = Card(1,'h')
        self.tableau[7] = Card(8,'d')
        print self.tableau.calc_score_simple()
        print self.tableau.calc_score_advanced()

        while True:
            break
            stop = self.step()
            if stop:
                break
    
    def step(self):
        pass    
            

if __name__=="__main__":
    g = Game()
    g.play()
    
    