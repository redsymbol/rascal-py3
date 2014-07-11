from .view import View
from .actors import Player

def main(args):
    player = Player('Aaron')
    View(player).run_forever()
    
