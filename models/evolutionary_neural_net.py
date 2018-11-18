import numpy as np
import random
import math


class EvolutionaryNN:
    def __init__(self, inputs, hidden, outputs):
        """
        Args:
            inputs (int): Number of input nodes.
            hidden (int): Number of hidden nodes.
            outputs (int): Number of output nodes.
        """

        # Generate random weight values for all layers
        # (bias included)
        self.inputs_to_hidden = self.randomize(
            np.zeros(shape=(hidden, inputs + 1)))
        self.hidden_to_hidden = self.randomize(
            np.zeros(shape=(hidden, hidden + 1)))
        self.hidden_to_output = self.randomize(
            np.zeros(shape=(outputs, hidden + 1)))

    def output(self, inputs):
        """
        Calculates the output for this NN.

        Args:
            inputs (list): A 1-Dimensional array containing all input values.

        Returns:
            Returns a 1-D array with a value for each output node.
        """

        # Reshape inputs & add bias
        inputs = np.reshape(inputs, (len(inputs), 1))
        inputs = self.add_bias(inputs)

        # Calculate layer 1 outputs
        hidden_outputs = np.dot(self.inputs_to_hidden, inputs)
        hidden_outputs = self.activate(hidden_outputs)
        hidden_outputs = self.add_bias(hidden_outputs)

        # Calculate layer 2 outputs
        hidden_outputs = np.dot(self.hidden_to_hidden, hidden_outputs)
        hidden_outputs = self.activate(hidden_outputs)
        hidden_outputs = self.add_bias(hidden_outputs)

        # Calculate layer 3 (final for this model) outputs
        outputs = np.dot(self.hidden_to_output, hidden_outputs)
        outputs = self.activate(outputs)

        # Flatten to 1-D array and return.
        return np.ndarray.flatten(outputs)

    def mutate(self, matrix, mr):
        """
        Mutates the given matrix with the given rate.

        Args:
            matrix (np.array): Matrix to be mutated.
            mr (float): Mutation Rate, the probability of mutation for each weight.
        """

        for i, _ in enumerate(matrix):
            for j, val in enumerate(_):
                if np.random.random() < mr:
                    matrix[i, j] = self.clamp1(val + np.random.normal() / 5)

    def clamp1(self, num):
        """
        Asserts that the given value is between -1 and 1.
        """

        return -1 if num < -1 else 1 if num > 1 else num

    def randomize(self, matrix):
        """
        Randomize all values in the given matrix.
        """

        for i, _ in enumerate(matrix):
            for j, val in enumerate(_):
                matrix[i, j] = random.uniform(-1, 1)

        return matrix

    def activate(self, matrix):
        """
        Uses sigmoid as the activateion function.

        Returns:
            Returns a new matrix 
        """

        out = np.zeros(shape=(len(matrix), len(matrix[0])))

        for i, _ in enumerate(matrix):
            for j, val in enumerate(_):
                out[i, j] = self.sigmoid(matrix[i, j])

        return out

    def sigmoid(self, x):
        return 1 / (1 + pow(math.e, -x))

    def crossover(self, matrix1, matrix2):
        """
        Generate a random ratio and create a 'child' matrix that has that ratio of parent1 'genes' - parent2 'genes'.

        ### Both parents MUST be the same n-dimensional. ###

        Ex. 0.3:
            0.3 genes from parent 1.
            0.7 genes from parent 2.

        Args:
            matrix1 (np.array): Parent1
            matrix2 (np.array): Parent2
        """

        rows = len(matrix1)
        assert rows == len(
            matrix2), "Both parents MUST be the same n-dimensional."
        assert rows > 0, "Minimum row count is 1."

        cols = len(matrix1[0])
        assert cols == len(matrix2[0])
        assert cols > 0, "Minimum column count is 1."

        cutoff = (
            np.random.randint(0, high=rows),
            np.random.randint(0, high=cols)
        )

        new = np.zeros((rows, cols))

        for i in range(rows):
            for j in range(cols):

                # This will copy all nodes from parent 1 until the cutoff is reached,
                # then it will switch over to parent 2.

                if i < cutoff[0] or (i == cutoff[0] and j <= cutoff[1]):
                    new[i, j] = matrix1[i, j]
                else:
                    new[i, j] = matrix2[i, j]

        return new

    def add_bias(self, matrix):
        """
        Adds a column to the given matrix & sets it's value to [1].
        """

        rows = len(matrix) + 1
        cols = len(matrix[0])
        new = np.zeros((rows, cols))

        for i, _ in enumerate(matrix):
            for j, val in enumerate(_):
                new[i, j] = val

        new[rows-1] = [1]
        return new

    def clone(self, matrix):
        out = np.zeros(shape=(len(matrix), len(matrix[0])))

        for i, _ in enumerate(matrix):
            for j, val in enumerate(_):
                out[i, j] = matrix[i, j]

        return out
