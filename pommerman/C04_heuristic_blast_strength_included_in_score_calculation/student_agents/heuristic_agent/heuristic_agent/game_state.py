import numpy as np


from pommerman import agents
from pommerman import constants
from pommerman import characters


# we have to create a game state from the observations
# in this example we only use an approximation of the game state, this can be improved
# approximations are:
#  - flames: initialized with 2 ticks (might be 1) > fixed to 1
#  - agents: initialized with ammo=2 (might be more or less)
#  - bombs: do not consider, which agent placed the bomb,
#           after explosion this would increase the agent's ammo again
#  - items: we do not know if an item is placed below a removable tile
def game_state_from_obs(obs):
    # TODO: think about removing some of the approximations and replacing them
    #   with exact values (e.g. tracking own and opponent's ammo and using exact flame life)
    game_state = [
        obs["board"],
        convert_agents(obs["board"], obs["ammo"]),
        convert_bombs(np.array(obs["bomb_blast_strength"]), np.array(obs["bomb_life"])),
        convert_items(obs["board"]),
        convert_flames(obs["board"])
    ]
    return game_state


def convert_bombs(strength_map, life_map):
    """ converts bomb matrices into bomb object list that can be fed to the forward model """
    ret = []
    locations = np.where(strength_map > 0)
    for r, c in zip(locations[0], locations[1]):
        ret.append(
            {'position': (r, c), 'blast_strength': int(strength_map[(r, c)]), 'bomb_life': int(life_map[(r, c)]),
             'moving_direction': None})
    return make_bomb_items(ret)


def make_bomb_items(ret):
    bomb_obj_list = []

    for i in ret:
        bomber = agents.player_agent
        bomber = characters.Bomber()  # dummy bomber is used here instead of the actual agent
        bomb_obj_list.append(
            characters.Bomb(bomber, i['position'], i['bomb_life'], i['blast_strength'],
                            i['moving_direction']))
    return bomb_obj_list


def convert_agents(board, ammo):
    """ creates two 'clones' of the actual agents """
    ret = []
    # agent board ids are 10 and 11 in two-player games
    for aid in [10, 11]:
        locations = np.where(board == aid)
        agt = agents.DummyAgent()
        agt.init_agent(aid, constants.GameType.FFA)
        if len(locations[0]) != 0:
            agt.set_start_position((locations[0][0], locations[1][0]))
        else:
            agt.set_start_position((0, 0))
            agt.is_alive = False
        agt.reset(is_alive=agt.is_alive)
        agt.agent_id = aid - 10
        ret.append(agt)
    return ret


def convert_items(board):
    """ converts all visible items to a dictionary """
    ret = {}
    for r in range(board.shape[0]):
        for c in range(board.shape[1]):
            v = board[r][c]
            if v in [constants.Item.ExtraBomb.value,
                     constants.Item.IncrRange.value,
                     constants.Item.Kick.value]:
                ret[(r, c)] = v
    return ret


def convert_flames(board):
    """ creates a list of flame objects - initialized with flame_life=1 """
    ret = []
    locations = np.where(board == constants.Item.Flames.value)
    for r, c in zip(locations[0], locations[1]):
        ret.append(characters.Flame((r, c), life=1))
    return ret
