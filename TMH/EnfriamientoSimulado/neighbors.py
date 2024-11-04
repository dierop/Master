import random
from copy import deepcopy
from typing import Union

from GeneticAlgorithm.individuo import OPERATORS, SIZE, Fenotype, Node, Tree


class TreeUpdate:

    tree: Tree

    def __init__(self, tree: Tree):
        self.tree = tree

    def _switch_node_value(
        self, node: Node, value_origin: Union[int, str], value_destiny: Union[int, str]
    ):
        if node.value == value_origin:
            node.value = value_destiny
            if type(value_origin) == str and random.random() < 0.5:
                self._switch_node_value(node.left, value_origin, value_destiny)
                self._switch_node_value(node.right, value_origin, value_destiny)
        elif node.left is not None and node.right is not None:
            self._switch_node_value(node.left, value_origin, value_destiny)
            self._switch_node_value(node.right, value_origin, value_destiny)

    def _in_tree(self, value: Union[int, str]):
        tree_list = self.tree.root.values
        return value in tree_list

    def switch_numbers(self):
        """Switches two numbers in the tree"""
        value_origin = random.randint(0, SIZE - 1)
        while not self._in_tree(value_origin):
            value_origin = random.randint(0, SIZE - 1)
        value_destiny = random.randint(0, SIZE - 1)
        while value_origin == value_destiny:
            value_destiny = random.randint(0, SIZE - 1)
        self._switch_node_value(self.tree.root, value_origin, -1)
        self._switch_node_value(self.tree.root, value_destiny, value_origin)
        self._switch_node_value(self.tree.root, -1, value_destiny)

    def switch_operators(self):
        """Switches two operators in the tree"""
        value_origin = random.choice(OPERATORS)
        while not self._in_tree(value_origin):
            value_origin = random.choice(OPERATORS)
        value_destiny = random.choice(OPERATORS)
        while value_origin == value_destiny:
            value_destiny = random.choice(OPERATORS)
        self._switch_node_value(self.tree.root, value_origin, value_destiny)

    def invert_node(self):
        """Inverts a random node in the tree"""

        def _invert_random_node(node: Node):
            """Inverts a random node"""
            if node.value in OPERATORS:
                if node.value in ["-", "/"] and random.random() < 0.5:
                    node.left, node.right = node.right, node.left
                if random.random() < 0.5:
                    node.left = _invert_random_node(node.left)
                else:
                    node.right = _invert_random_node(node.right)
            return node

        self.tree.root = _invert_random_node(self.tree.root)

    def switch_parent_child(self):
        """Switches parent and child of a random node"""

        def _switch_parent_child_operator(node: Node):
            if node.value in OPERATORS:
                prob = random.random()
                if node.left.value in OPERATORS and prob < 0.5:
                    n = deepcopy(node)
                    n.left = node.left.left
                    node = node.left
                    node.left = n
                elif node.right.value in OPERATORS and prob >= 0.5:
                    n = deepcopy(node)
                    n.right = node.right.right
                    node = node.right
                    node.right = n
                elif prob < 0.5:
                    node.left = _switch_parent_child_operator(node.left)
                else:
                    node.right = _switch_parent_child_operator(node.right)
            return node

        self.tree.root = _switch_parent_child_operator(self.tree.root)

    def insert_node_tree(self):

        def get_random_leaf_node(node: Node):
            if node.value not in OPERATORS:
                if random.random() < 0.5:
                    return node
                else:
                    return None

            else:
                if random.random() < 0.5:
                    ln = get_random_leaf_node(node.left)
                    ln = ln if ln is not None else get_random_leaf_node(node.right)
                    return ln
                else:
                    rn = get_random_leaf_node(node.right)
                    rn = rn if rn is not None else get_random_leaf_node(node.left)
                    return rn

        un = self.tree.get_unused_numbers()
        if len(un) == 0:
            return None
        node = get_random_leaf_node(self.tree.root)
        if node is None:
            return None
        un.append(node.value)
        node.value = random.choice(OPERATORS)
        random.shuffle(un)
        node.left = Node(un.pop())
        node.right = Node(un.pop())

    def delete_node_tree(self):

        def get_random_op_leaf_node(node: Node):
            if node.value in OPERATORS:
                if (
                    node.left.value not in OPERATORS
                    and node.right.value not in OPERATORS
                ):
                    return node
                elif node.left.value in OPERATORS and node.right.value in OPERATORS:
                    if random.random() < 0.5:
                        ln = get_random_op_leaf_node(node.left)
                        ln = (
                            ln
                            if ln is not None
                            else get_random_op_leaf_node(node.right)
                        )
                        return ln
                    else:
                        rn = get_random_op_leaf_node(node.right)
                        rn = (
                            rn if rn is not None else get_random_op_leaf_node(node.left)
                        )
                        return rn
                elif node.left.value in OPERATORS:
                    return get_random_op_leaf_node(node.left)
                else:
                    return get_random_op_leaf_node(node.right)
            return None

        node = get_random_op_leaf_node(self.tree.root)
        if node is None:
            return None
        node.left = None
        node.right = None
        node.value = random.choice(self.tree.get_unused_numbers())

    def get_updated_tree(self, type: int):
        """Updates the tree"""
        if type == 1:
            self.switch_numbers()
        elif type == 2:
            self.switch_operators()
        elif type == 3:
            self.invert_node()
        elif type == 4:
            self.switch_parent_child()
        elif type == 5:
            self.insert_node_tree()
        elif type == 6:
            self.delete_node_tree()
        else:
            # random type
            self.get_updated_tree(random.randint(1, 6))
        return self.tree


class Neighbor:
    fenotype: Fenotype

    def __init__(self, fenotype: Fenotype):
        self.fenotype = deepcopy(fenotype)

    def get_neighbor(self, type: int, tree_side: int):
        """Returns a neighbor of the fenotype"""
        if tree_side == 1:
            tree = self.fenotype.left_tree
        elif tree_side == 2:
            tree = self.fenotype.right_tree
        elif tree_side == 3:
            self.get_neighbor(type, 1)
            self.get_neighbor(type, 2)
            return self.fenotype
        else:
            random_tree = random.randint(1, 3)
            self.get_neighbor(type, random_tree)
            return self.fenotype
        tree_update = TreeUpdate(tree)
        tree = tree_update.get_updated_tree(type)
        if tree_side == 1:
            self.fenotype.left_tree = tree
        else:
            self.fenotype.right_tree = tree
        return self.fenotype


class Neighborhod:
    fenotype: Fenotype
    n_neighbors: int
    neighbors: list[Fenotype]

    def __init__(
        self, fenotype: Fenotype, n_neighbors: int, type: int = 0, tree_side: int = 0
    ):
        self.fenotype = fenotype
        self.n_neighbors = n_neighbors
        self.neighbors = self._get_neighbors(type, tree_side)

    def _get_neighbors(self, type: int = 0, tree_side: int = 0):
        """Returns a list of neighbors of the fenotype"""
        neighbors = []
        for _ in range(self.n_neighbors):
            neighbors.append(Neighbor(self.fenotype).get_neighbor(type, tree_side))
        return neighbors

    def get_random_neighbor(self):
        """Returns and pops random neighbor of the fenotype"""
        if len(self.neighbors) == 0:
            return self.fenotype
        return self.neighbors.pop(random.randint(0, len(self.neighbors) - 1))
