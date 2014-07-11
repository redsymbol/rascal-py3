class Actor:
    symbol = '?'
    name = '?'
    hitpoints = 0
    attack = 0
    def __init__(self):
        self.x = 0
        self.y = 0

    def draw(self, window):
        window.move(self.x, self.y)
        window.delch()
        window.insch(self.symbol)

    def adjacent_to(self, other : 'Actor'):
        diff_x = abs(self.x - other.x)
        diff_y = abs(self.y - other.y)
        return (diff_x <= 1) and (diff_y <= 1)

    def is_alive(self):
        return self.hitpoints > 0

class Player(Actor):
    symbol = '@'
    hitpoints = 10
    attack = 1
    def __init__(self, name):
        self.name = name
        super().__init__()

class Monster(Actor):
    pass

class Rat(Monster):
    symbol = 'r'
    name = 'rat'
    hitpoints = 1
    attack = 1

class GiantRat(Monster):
    symbol = 'R'
    name = 'giant rat'
    hitpoints = 2
    attack = 1

class Goblin(Monster):
    symbol = 'g'
    name = 'goblin'
    hitpoints = 1
    attack = 2

