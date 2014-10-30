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
        tot = 0
        for hand in self.hands:
            print "calc score for hand: ", hand
            res = self.calc_score_from_values(self.get_hand_values(hand))
            print "res: ", res
            tot += res
        return tot
        #return sum([self.calc_score_from_values(self.get_hand_values(hand)) for hand in self.hands])
    
    def get_hand_values(self, hand):
        values = self.to_values()        
        return [values[i-1] for i in hand if values[i-1] > 0]
    
    def get_hand_score(self, hand): 
        values = self.get_hand_values()
        n_aces = values.count(1)
        
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
    
    def get_value_options(self):
        pass
    
    def calc_score_advanced(self):
        pass
                                                      
            
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
        
        self.tableau[1] = Card(13,'h')
        self.tableau.calc_score_simple()

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
    
    