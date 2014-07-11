class Event:
    def format(self):
        return ''

class PlayerDeadEvent(Event):
    def format(self):
        return 'You have died!'

class PlayerSlainByEvent(PlayerDeadEvent):
    def __init__(self, monster):
        self.slayer = monster

    def format(self):
        return 'You have been slain by a {}!'.format(self.slayer.name)

class MonsterAttackEvent(Event):
    def __init__(self, monster):
        self.monster = monster

    def format(self):
        return 'The {} attacks you for {} damage!'.format(self.monster.name, self.monster.attack)

class SlainMonsterEvent(Event):
    def __init__(self, monster):
        self.monster = monster

    def format(self):
        return 'You have slain the {}!'.format(self.monster.name)

