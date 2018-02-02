#!/usr/bin/env python3
"""
WowCowTown -

Simulation Cows

Cows Stats (Which Currently Do Nothing):

Strength: str
Perception: per
Endurance: end
Charisma: cha
Intelligence: int
Agility: agi
Luck: luc
"""

import sys
if sys.version_info.major != 3:
    print("Use Python3!")
    raise SystemExit



from random import randint
#from operator import itemgetter
from time import sleep
from statistics import *


def rand(m):
    return randint(0,m)

def nonneg(n):
    if n < 0:
        return 0
    else:
        return n

class town:

    def __init__(self, size=5, cowCount=5):
        self._cowidc = 0
        self._tick = 0

        self.grid = [ [ tile("%s/%s" % (x,y), x, y) for x in range(size) ] for y in range(size) ]
        self.cows = []
        self.deadCows = []

        self.tiles = []
        for y in self.grid:
            for t in y:
                self.tiles.append(t)


        for i in range(cowCount):
            cow = cowClass(self)
            self.cows.append(cow)
            self.grid[0][0].enter(cow)


    def disp(self):
        for line in self.grid:
            print(line)

    def play(self, count=10, stepcount=1, delay=2):
        for i in range(count):
            self.step(stepcount)
            self.disp()
            print("\n")
            sleep(delay)


    def graph(self, count=100000, stepcount=1, fixer=10):
        for i in range(count):
            self.step(stepcount)
            print("%s %s" % (len(self.cows), "="*int(len(self.cows)/fixer)))

    def step(self, count=1):
        for i in range(count):
            for cow in self.cows:
                if cow.alive:

                    x = cow.location.x
                    y = cow.location.y                    
                    localGrid = []
                    for yv in self.grid[nonneg(x-1):x+2]:
                        localGrid += yv[nonneg(y-1):y+2]    
                    choice = cow.think(localGrid)
                    if choice:
                        if choice != cow.location:
                            cow.location.exit(cow)
                            choice.enter(cow)
    
                    mateChoice = cow.selectMate(cow.location.cowsInside)
                    if mateChoice:
                        cow.mate(mateChoice)
    
                    cow.tick()                
                else:
                    self.deadCows.append(cow)
    
                    #"Garbage Collection" should go here, if added
        
                    self.cows.remove(cow)

            for t in self.tiles:
                t.tick()



    @property
    def nextCowID(self):
        self._cowidc += 1
        return self._cowidc

    @property
    def tickcount(self):
        self._tick += 1
        return self._tick


class tile:

    def __init__(self, name, x, y):

        self.name = str(name)
        self.cowsInside = []
        self.x = x
        self.y = y

        self.food = self.defaultfood = 20
        self.foodcounter = 0
        self.foodcountergoal = 200
        self.foodcounterregenchance = 20

        
    def enter(self, cow):
        self.cowsInside.append(cow)
        cow.location = self
        self.enterEffect(cow)

        
    def exit(self, cow):
        self.cowsInside.remove(cow)
        cow.location = None
        self.exitEffect(cow)

        
    def tick(self):
        self.foodcounter += 1
        if self.foodcounter > self.foodcountergoal:
            if rand(self.foodcounterregenchance) == 0:
                self.foodcounter = 0
                self.food = self.defaultfood
        

    def __repr__(self):
        if len(self.cowsInside) > 0:
            return ("%s" % (len(self.cowsInside))).rjust(3)
        else:
            return "   "


    ###Functions for users to add/modify should go below here

        
    
    def enterEffect(self, cow):
        """Programmable enter effects go here """
        #print("Cow %s entered tile %s" % (cow.name, self.name))
        pass

    def exitEffect(self, cow):
        """Programmable enter effects go here """
        pass




    
class cowClass:
    _defaultSpecial = {
        'str': 1,
        'per': 1,
        'end': 1,
        'cha': 1,
        'int': 1,
        'agi': 1,
        'luc': 1,       

        }

    def __init__(self, hometown, special={}, name="", gender=None):       
        self.name = str(name)
        self.cid = hometown.nextCowID
        self.alive = True
        self.location = None
        self.parents = set()
        self.hometown = hometown
        self.breather = 0
        self.hunger = self.maxhunger = 50

        #Cow's gender is selected randomly if not defined
        if gender!=None: self.gender = gender
        else: self.gender = rand(1)

        self.special = self._defaultSpecial.copy()
        self.special.update(special)

        hometown.cows.append(self)


    def __getitem__(self, key):
        return self.special[key]

    def __repr__(self):
        return "%s|%s" % (self.cid, self.gender)

    
    def tick(self):
        """
        Things tht happen to a cow every turn. 
        Currently some decisions go here, but in the future those will be removed
        """
        if self.breather > 0:
            self.breather -= 1

        if self.hunger < self.maxhunger:
            if self.location.food > 0:
                self.location.food -= 1
                self.hunger += 3

        self.hunger -= 1
        if self.hunger < 0:
            self.alive = False
            self.location.exit(self)
            #print("Cow %s died!" % (self.cid))
        

    def think(self, tilechoices):
        """This is where a cow selects which tile to move to"""
        if self.location.food <= 0:
            return tilechoices[rand(len(tilechoices)-1)]
        else:
            return None

    def mate(self, otherCow):
        self.breather = 50
        
        babyCow = cowClass(self.hometown)

        genome = [
            (k, [self.special.get(k,1), otherCow.special.get(k,1)])
            for k in self._defaultSpecial.keys() ]
        
        for k, a in genome:
            babyCow.special[k] = a[rand(1)]

        babyCow.parents = {self, otherCow}

        self.location.enter(babyCow)

        if rand(20) == 0:
            babyCow.special['cha'] += 1
        
        return babyCow


    def selectMate(self, localCows):
        if (self.gender != 0) or (self.breather > 0):
            return None
        else:
            localCows = [ c for c in localCows if ((c.gender != 0) and (c not in self.parents)) ]
            if len(localCows) > 0:
                return localCows[rand(len(localCows)-1)]



            
def checkstat(town, stat='cha'):
    """Return Dictionary showing number of all cows with a stat level

    Example:
    { 15: 2   # 2 cows have level 15
      50: 5   # 5 cows have level 50
    }

    """
    counter = {}
    for c in town.cows:
        counter[c[stat]] = counter.get(c[stat], 0)+1
    return counter



t = town(40, 40)  #Create a 40x40 grid with 40 cows


###Example commands###

#t.disp()   #display a representation of WowCowTown

###Remember that t.disp() does NOT move the simulation forward

#t.step()   #Simulate one "tick"

#t.graph()  #Automatically tick forward, and graph the amount of cows over time
















def demo(t):
    print("Running Demo...")
    print("Please ensure this window is at least 200 characters wide for best viewing")
    input("(Press Enter)")
    t.disp()

    print("Above we have represented the WowCow Town, each tile is blank unless it has cows,")
    print("in which case the number of cows on the tile is shown")
    input("(Press Enter)")
    t.step()
    t.disp()

    print("As you can see, some cows have moved. In this current version of WowCowTown movement is random,")
    print("however in the future maybe some more logic will be added")
    input("(Press Enter)")
    t.step()
    t.disp()


    print("Cows can appear slow when moving the simulation a single tick at a time.")
    print("We will not skip forward 100 ticks")
    input("(Press Enter)")
    t.step(100)
    t.disp()

    print("Hopefully they moved quite a bit more!")
    print("Now, after this we will \"graph\" the population of cows over time.")
    print("This won't automatically stop! (so Control-C or whatever you'd like to close")
    input("(Press Enter)")
    
    t.graph()


if __name__ == "__main__":
    demo(t)
