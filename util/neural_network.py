import numpy as np
import math
import random
import arcade
from enum import Enum
from typing import List, Tuple
from environments.environment import *
from actors.actions import Actions

NEURON_DIST = 50
VERBOSE_NEURON_SPACING_X = 60
VERBOSE_NEURON_SPACING_Y = 18
VERBOSE_NEURON_RADIUS = 8
VERBOSE_NEURON_TEXT_SIZE = 5
VERBOSE_MAX_SYNAPSE_THICKNESS = 2
NETWORK_CENTER_HEIGHT = SCREEN_HEIGHT / 4

REACTION_THRESHOLD = 0.7

DRAW_NEURON_LABELS = True

INPUT_NEURON_LABELS = [
    'Laser Distance',
    'Angle to Laser',
    'Enemy Distance',
    'Angle to Enemy',
    'Current Angle'
]

# Reason for redefinition: __dict__ is not constant ordering
ACTION_LIST = [
    Actions.MOVE_LEFT,
    Actions.MOVE_RIGHT,
    Actions.MOVE_UP,
    Actions.MOVE_DOWN,

    Actions.LOOK_LEFT,
    Actions.LOOK_RIGHT,

    Actions.USE_SHIELD,

    Actions.LONG_ATTACK,
    Actions.SHORT_ATTACK
]

OUTPUT_NEURON_LABELS = [a.name for a in ACTION_LIST]
print(OUTPUT_NEURON_LABELS)


class ActivationType(Enum):
    RELU = 0
    SIGMOID = 1
    TANH = 2


ACTIVATION = ActivationType.TANH


class NeuralNetwork:
    layer_weights: list
    neuron_weights: list = None  # Stored here for verbose
    neuron_screen_locations: list = None

    def __init__(
        self,
        dimensions: Tuple[int] = None,
        layer_weights: list = None
    ):
        """
        Randomly initialize a Neural Network with the given dimensions.

        len(dimensions) = layer count.
        dimensions[i] = neurons at layer i.
        """

        assert dimensions != None or layer_weights != None, 'Neural Network must be initialized with either dimensions or weights'

        if dimensions:
            self.layer_weights = []

            for i in range(len(dimensions)-1):
                variance = 2/(dimensions[i] + dimensions[i+1])
                stddev = math.sqrt(variance)

                layer = np.random.normal(
                    loc=0,
                    scale=stddev,
                    size=(dimensions[i], dimensions[i+1])
                )

                self.layer_weights.append(
                    layer
                )
            return

        self.layer_weights = list(layer_weights)

    def sigmoid(self, x, derivative=False):
        return x*(1-x) if derivative else 1/(1+np.exp(-x))

    def ReLU(self, x):
        return x * (x > 0)

    def softmax(self, x):
        return np.exp(x) / np.sum(np.exp(x), axis=0)

    def activate_layer(self, layer: list):
        for x in np.nditer(layer, op_flags=['readwrite']):
            if ACTIVATION == ActivationType.RELU:
                x[...] = self.ReLU(x)
            elif ACTIVATION == ActivationType.SIGMOID:
                x[...] = self.sigmoid(x)
            elif ACTIVATION == ActivationType.TANH:
                x[...] = np.tanh(x)

    def output(self, inputs: list):
        """Calculates the output for the given inputs."""

        # Column matrix
        # inputs = np.reshape(inputs, (len(inputs), 1))

        self.neuron_weights = []
        self.neuron_weights.append(np.array((inputs)))
        output = inputs

        if ACTIVATION == ActivationType.RELU:

            for i, weight_layer in enumerate(self.layer_weights):
                output = np.dot(output, weight_layer)

                if i < len(self.layer_weights)-1:
                    self.activate_layer(output)
                    self.neuron_weights.append(output)
                else:
                    break

            # Output layer should be activated using softmax when using ReLU
            output = self.softmax(output)
            self.neuron_weights.append(output)

        else:

            for weight_layer in self.layer_weights:
                output = np.matmul(output, weight_layer)
                self.activate_layer(output)
                self.neuron_weights.append(output)

        return output

    def draw_neurons(self, offset_x=-70, offset_y=0):
        if self.neuron_weights == None:
            return

        x = SCREEN_WIDTH - len(self.neuron_weights) * \
            VERBOSE_NEURON_SPACING_X + offset_x

        self.neuron_screen_locations = []

        for i, layer in enumerate(self.neuron_weights):
            y = NETWORK_CENTER_HEIGHT - \
                ((len(layer) / 2) * VERBOSE_NEURON_SPACING_Y) + offset_y

            self.neuron_screen_locations.append([])

            # All weights will be normalized. Use radial representation.
            for j, weight in enumerate(np.nditer(layer, op_flags=['readwrite'])):
                if DRAW_NEURON_LABELS:
                    if i == 0:  # input layer
                        text = INPUT_NEURON_LABELS[j]
                        arcade.draw_text(
                            text,
                            x-VERBOSE_NEURON_RADIUS * 2.5 -
                            len(text) * (VERBOSE_NEURON_TEXT_SIZE/2.5),
                            y,
                            arcade.color.WHITE,
                            font_size=VERBOSE_NEURON_TEXT_SIZE*1.5,
                            align='center',
                            anchor_x='center',
                            anchor_y='center'
                        )
                    elif i == len(self.neuron_weights) - 1:  # output layer
                        text = OUTPUT_NEURON_LABELS[j]
                        arcade.draw_text(
                            text,
                            x+VERBOSE_NEURON_RADIUS * 2.5,
                            y,
                            arcade.color.WHITE,
                            font_size=VERBOSE_NEURON_TEXT_SIZE*1.5,
                            anchor_y='center'
                        )

                self.neuron_screen_locations[i].append((x, y))

                arcade.draw_circle_filled(
                    x,
                    y,
                    VERBOSE_NEURON_RADIUS,
                    arcade.color.WHITE if i < len(
                        self.neuron_weights)-1 or weight < REACTION_THRESHOLD else arcade.color.GREEN
                )

                arcade.draw_text(
                    '%.1f' % weight, x, y,
                    arcade.color.BLACK,
                    font_size=VERBOSE_NEURON_TEXT_SIZE,
                    align='center',
                    anchor_x='center',
                    anchor_y='center')

                y += VERBOSE_NEURON_SPACING_Y

            x += VERBOSE_NEURON_SPACING_X

    def draw_weights(self):
        if self.neuron_screen_locations == None:
            return

        for i, layer_weight_set in enumerate(self.layer_weights):
            layer1_neuron_locations = self.neuron_screen_locations[i]
            layer2_neuron_locations = self.neuron_screen_locations[i+1]

            for j, weight_layer in enumerate(layer_weight_set):
                neuron1 = layer1_neuron_locations[j]

                for k, weight in enumerate(layer_weight_set[j]):
                    neuron2 = layer2_neuron_locations[k]

                    arcade.draw_line(
                        neuron1[0],
                        neuron1[1],
                        neuron2[0],
                        neuron2[1],
                        arcade.color.WHITE,
                        border_width=max(
                            0.1, VERBOSE_MAX_SYNAPSE_THICKNESS * weight)
                    )

    def save_to_file(self, path: str):
        """
        Args:
            path (str): Extension not required. (.npy)
        """

        np.save(path, self.layer_weights)

    def load_from_file(path: str):
        return NeuralNetwork(layer_weights=np.load(path))


if __name__ == '__main__':
    nn1 = NeuralNetwork(dimensions=(5, 2, 3))
    out1 = nn1.output([1, 2, 3, 4, 5])

    nn2 = NeuralNetwork(layer_weights=nn1.layer_weights)
    out2 = nn2.output([1, 2, 3, 4, 5])

    assert np.array_equal(out1, out2), 'Outputs MUST be the same.'
