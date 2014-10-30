#! /usr/bin/python

from cards import Card, Deck

class Tableau(object):
        
    point_dict = {17:2, 18:3, 19:4, 20:5, 21:7}
    point_dict.update({i:1 for i in xrange(17)})
    
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
        self.t[pos] = card
    
    #def __getitem__(self, pos):
    #    return self.t[pos].get_card()
    
    def calc_score_simple(self):
        pass
    
    def calc_score_advanced(self):
        pass
    
    def calc_hand_score(self, hand):
        """ 
        Calculates the score of a given hand.
        A hand is a list of positions (ints)
        """
                
        hand_spots = [self[pos] for pos in hand]
        hand_len = sum(map(bool, hand_spots))                             
        hand_sum = sum([spot.get_card().get_value() for spot in hand_spots])
        
        if hand_sum > 21:
            return 0
        
        elif hand_sum == 21 and hand_len == 2:
            return 10
        
        return self.point_dict[hand_sum]
    
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
    
    #def get_card(self):
    #    return self.card
    
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
        
        print self.tableau

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