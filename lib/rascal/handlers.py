def handle_move_down(world):
    return world.move_player_to(1, 0)

def handle_move_up(world):
    return world.move_player_to(-1, 0)

def handle_move_left(world):
    return world.move_player_to(0, -1)

def handle_move_right(world):
    return world.move_player_to(0, 1)

def handle_rest(world):
    pass

def handle_quit(world):
    return True

handler_map = {
    'j' : handle_move_down,
    'k' : handle_move_up,
    'h' : handle_move_left,
    'l' : handle_move_right,
    '.' : handle_rest,
    'q' : handle_quit,
    }


