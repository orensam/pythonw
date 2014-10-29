#! /usr/bin/python

from cards import Card, Deck

class Tableau(object):

    def __init__(self):
        self.t = [str(i) for i in xrange(1,17)]
    
    def __str__(self):
        s = ""
        s += "%4s %4s %4s %4s %4s" %tuple(self.t[:5]) + '\n'
        s += "%4s %4s %4s %4s %4s" %tuple(self.t[5:10]) + '\n'
        s += "%9s %4s %4s"%tuple(self.t[10:13]) + '\n'
        s += "%9s %4s %4s"%tuple(self.t[13:16])
        return s
    
    def put_card(self, card, pos):
        self.t[pos] = card
    
    def calc_score_simple(self):
        pass
    
    def calc_score_advanced(self):
        pass
    
    def calc_hand_score(self):
        pass


class Game(object):
    
    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.tableau = Tableau()

    def start(self):
        
        print self.tableau

    
    



if __name__=="__main__":
    g = Game()
    g.start()