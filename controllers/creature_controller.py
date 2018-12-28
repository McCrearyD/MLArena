from controllers.controller import *
from actors.pawns.pawn import *
from util.neural_network import *
from util.match_up import *
from actors.actions import *

NETWORK_DIMENSIONS = (
    5,
    6,
    len(ACTION_LIST)
)

MAX_DIST = math.sqrt(SCREEN_WIDTH ** 2 + SCREEN_HEIGHT ** 2)
MAX_ANGLE = math.pi * 2


class CreatureController(Controller):

    pawn: Pawn
    neural_network: NeuralNetwork

    inputs: list
    outputs: list

    def __init__(self, pawn: Pawn, neural_network=None):
        super().__init__(pawn)
        self.pawn = pawn

        if neural_network == None:

            self.neural_network = NeuralNetwork(NETWORK_DIMENSIONS)

        else:
            self.neural_network = neural_network

    def look(self, match_up: MatchUp):
        """Create neural net inputs"""
        p: Pawn = self.pawn

        imminent: Laser = match_up.get_most_imminent_laser(p)
        enemy: Pawn = match_up.get_closest_opponent(p)

        self.inputs = [
            math.sqrt(p.dist_squared(actor=imminent)) /
            MAX_DIST if imminent != None else 1,
            p.angle_to(actor=imminent)/MAX_ANGLE if imminent != None else 1,

            math.sqrt(p.dist_squared(actor=enemy)) /
            MAX_DIST if enemy != None else 1,
            p.angle_to(actor=enemy)/MAX_ANGLE if enemy != None else 1,

            p.get_direc()/MAX_ANGLE
        ]

    def think(self):
        self.outputs = self.neural_network.output(self.inputs)

    def act(self):
        """React to neural network outputs"""
        for i, action in enumerate(ACTION_LIST):
            if self.outputs[i] > REACTION_THRESHOLD:
                self.submit_action(action)
            else:
                if action == Actions.MOVE_LEFT:
                    if Actions.MOVE_RIGHT not in self.active_actions:
                        self.undo_action(action)

                elif action == Actions.MOVE_RIGHT:
                    if Actions.MOVE_LEFT not in self.active_actions:
                        self.undo_action(action)

                elif action == Actions.MOVE_UP:
                    if Actions.MOVE_DOWN not in self.active_actions:
                        self.undo_action(action)

                elif action == Actions.MOVE_DOWN:
                    if Actions.MOVE_UP not in self.active_actions:
                        self.undo_action(action)

                elif action == Actions.LOOK_LEFT:
                    if Actions.LOOK_RIGHT not in self.active_actions:
                        self.undo_action(action)

                elif action == Actions.LOOK_RIGHT:
                    if Actions.LOOK_LEFT not in self.active_actions:
                        self.undo_action(action)

                else:
                    self.undo_action(action)
