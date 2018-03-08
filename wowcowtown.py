import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from random import randint

def rc(iterator):
    return iterator[randint(0,len(iterator)-1)]



class Town:

    def __init__(self, size=10, cows=10):

        self.size = size

        self.delay = 0.1

        self._cmapcolors = ['white', 'goldenrod', 'gold', 'yellow', 'lightgreen', 'green', 'darkgreen']
        self.cmap  = matplotlib.colors.ListedColormap(self._cmapcolors)
        self.fig, self.ax = plt.subplots()
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        plt.ion()
        plt.xlim(0,self.size)
        plt.ylim(0,self.size)
        plt.axis('off')

        self.grid = [[self.Tile(self,(x,y),((x*size)+y))
                     for y in range(size)]
                     for x in range(size)]

        self.tiles = []
        for line in self.grid:
            for t in line:
                self.tiles.append(t)

        
        self._cid = 0
        self.cows = []
        for loc in range(size):
            self.makeCow(self.grid[loc][loc])
        


    def __getitem__(self, key):
        return self.grid[key]

    def __repr__(self):
        return "<cowtown>"


    @property
    def cid(self):
        self._cid += 1
        return self._cid


    def sim(self, count=1000, updateInterval=1):
        for i in range(0, count, updateInterval):
            self.step(updateInterval)
            self.disp()


    def step(self, count=1):
        for _ in range(count):
            
            for cow in self.cows:
                choice = self.passMoves(cow)
                choice.enterCow(cow)

            for cow in self.cows:
                cow.tick()

            for tile in self.tiles:
                tile.tick()


    def disp(self):
        plt.clf()          

        plt.pcolormesh([[y.food for y in x] for x in self.grid], cmap=self.cmap)        
        plt.scatter([c.tile.xy[1]+0.5 for c in self.cows], [c.tile.xy[0]+0.5 for c in self.cows], color='black')

        plt.pause(self.delay)


    def makeCow(self, tile):
        cow = self.Cow(self, self.cid)
        self.cows.append(cow)
        tile.enterCow(cow)
        print("Cow %s Made (%s)"  % (cow, len(self.cows)))

    def dieCow(self, cow):
        cow.tile.leaveCow(cow)
        cow.isDead = True
        self.cows.remove(cow)
        print("Cow %s died (%s)" % (cow, len(self.cows)))

    def passMoves(self, cow):
        ct = cow.tile
        x,y = ct.xy

        lowerx = 1
        upperx = 2
        lowery = 1
        uppery = 2

        #Perception Modifiers should go HERE
        

        #Ensure axis minus modifier is never less than 0
        if (x-lowerx) < 0:
            lowerx += (x-lowerx)
        if (y-lowery) < 0:
            lowery += (y-lowery)
            

        options = []
        for section in self.grid[x-lowerx:x+upperx]:
            options += section[y-lowery:y+uppery]

            #Use this to not share tile cow currently is on
            #options += [ t for t in section[y-lowery:y+uppery] if t!=ct ]

        choice = cow.think(options)
        return choice
            

        
        


    class Tile:
        def __init__(self, town, xy, name):
            self.town = town
            self.xy = xy
            self.nid = name
            self.cows = set()
            self.food = self.maxFood = 100
            self.foodRegen = self.foodRegenDelay = 30

        def __repr__(self):
            return "t%s" % (self.nid)

        def tick(self):
            self.foodRegen -= 1
            if self.foodRegen < 0:
                if self.food < self.maxFood:
                    self.food += 1
        

        def enterCow(self, cow):
            if cow.tile:
                cow.tile.leaveCow(cow)
            self.cows.add(cow)
            cow.tile = self
            self.enterEffect(cow)
            
        def leaveCow(self, cow):
            self.cows.remove(cow)
            cow.tile = None
            self.leaveEffect(cow)


        def enterEffect(self, cow):
            if cow.food < cow.maxFood:
                diff = cow.maxFood - cow.food

                
                if self.food > diff:
                    self.food -= diff
                    cow.food += diff
                elif self.food <= diff:
                    cow.food += self.food
                    self.food = 0
                    self.foodRegen = self.foodRegenDelay
                

                
                
            

                
            if self.food > (cow.maxFood - cow.food):
                self.food = 0
                cow.food = cow.maxFood
            

        def leaveEffect(self, cow):
            pass
        

    class Cow:
        def __init__(self, town, name):
            self.town = town
            self.nid = name
            self.tile = None
            self.isDead = False
            self.age = 0

            
            self.food = self.maxFood = 30
            self.mateTimeout = self.maxMateTimeout = 100

        def __repr__(self):
            return "c%s" % (self.nid)

        def think(self, options):
            return rc(options) #Temporary AI == Random


        def selectMate(self, mates):
            if len(mates) > 0:
                c = rc(mates)
                self.mateTimeout = self.maxMateTimeout
                c.mateTimeout = c.maxMateTimeout
                for _ in range(randint(1,4)):
                    self.town.makeCow(self.tile)

        def tick(self):            
            self.food -= 1
            if self.food < 1:
                self.town.dieCow(self)

            self.mateTimeout -= 1


            if self.tile:
                if len(self.tile.cows) > 2:
                    if self.mateTimeout < 0:
                        self.selectMate(list(filter( lambda x:x.mateTimeout<0, [ c for c in self.tile.cows if c!=self])))
                
                





t = Town(50)
t.delay = 0.1
t.sim(100000,1)

while True:
    t.step(100)
    print(len(t.cows))

