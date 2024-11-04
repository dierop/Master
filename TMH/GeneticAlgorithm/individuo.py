import math
import pickle
import random

from binarytree import Node

OPERATORS = ["+", "-", "*", "/"]
SIZE = 10


class Tree:
    root: Node

    def __init__(self, root: Node = None):
        self.root = root

    def _duplicates(self):

        tree_list = self.root.values

        dic = {}
        for i in tree_list:
            if i in list(range(SIZE)) and tree_list.count(i) > 1:
                dic[i] = tree_list.count(i)

        return dic

    def is_valid_tree(self):

        def is_valid_node(node: Node, ok: bool = True):
            if not ok:
                return False
            if node.value in OPERATORS:
                if node.left is None or node.right is None:
                    return False
                ok = is_valid_node(node.left, ok)
                ok = is_valid_node(node.right, ok)
            return ok

        return not self._duplicates() and is_valid_node(self.root)

    def get_unused_numbers(self):
        return list(set(range(SIZE)) - set(self.root.values))

    def curate_tree(self, trials: int = 3):
        if self.is_valid_tree():
            return True

        def curate_node(node: Node, possible_numbers: list[int]):
            ## if the node value is a duplicate
            if node is not None and node.value in duplicates.keys():
                if duplicates[node.value] > 2:
                    duplicates[node.value] -= 1
                    if len(possible_numbers) == 0:
                        node.value = random.choice(OPERATORS)
                    else:
                        node.value = possible_numbers.pop()
                else:
                    duplicates.pop(node.value)
                    if len(possible_numbers) == 0:
                        node.value = random.choice(OPERATORS)
                    else:
                        node.value = possible_numbers.pop()

            if node is None:
                if len(possible_numbers) == 0:
                    node = None
                else:
                    node.value = possible_numbers.pop()

            elif node.value in OPERATORS:

                if node.left is None and node.right is None:
                    if len(possible_numbers) == 0:
                        node = None
                    else:
                        node.value = possible_numbers.pop()
                else:
                    if node.left is None and node.right is not None:
                        if len(possible_numbers) > 0:
                            node.left = Node(possible_numbers.pop())
                            curate_node(node.right, possible_numbers)
                        else:
                            node = node.right
                            curate_node(node, possible_numbers)
                    elif node.right is None and node.left is not None:
                        if len(possible_numbers) > 0:
                            node.right = Node(possible_numbers.pop())
                            curate_node(node.left, possible_numbers)
                        else:
                            node = node.left
                            curate_node(node, possible_numbers)
                    else:
                        curate_node(node.left, possible_numbers)
                        curate_node(node.right, possible_numbers)
            elif (
                node.value in numbers
                and node.right is not None
                or node.left is not None
            ):

                if node.right is None:
                    possible_numbers += list(set(numbers) & set(node.left.values))
                    node.left = None
                elif node.left is None:
                    possible_numbers += list(set(numbers) & set(node.right.values))
                    node.right = None
                else:
                    possible_numbers.append(node.value)
                    node.value = random.choice(OPERATORS)
                    curate_node(node.left, possible_numbers)
                    curate_node(node.right, possible_numbers)

            return node

        numbers = list(range(SIZE))
        for _ in range(trials):
            possible_numbers = self.get_unused_numbers()

            duplicates = self._duplicates()

            self.root = curate_node(self.root, possible_numbers)

            if self.is_valid_tree():
                return True

        return False


class RandomTree(Tree):
    numbers: list[int]
    root: Node
    min_operations: int
    number_operations: int

    def __init__(self, len_numbers: int = SIZE, min_operations: int = 2):
        self.numbers = list(range(len_numbers))
        random.shuffle(self.numbers)
        self.min_operations = min_operations
        self.generate_random_tree()

    def generate_random_node(self, node: Node):
        choice = random.random()
        if self.number_operations < self.min_operations:
            node.value = random.choice(OPERATORS)
            self.number_operations += 1
            if choice <= 0.5:
                node.left = self.generate_random_node(Node(0))
                node.right = self.generate_random_node(Node(0))
            else:
                node.right = self.generate_random_node(Node(0))
                node.left = self.generate_random_node(Node(0))
        elif choice <= 0.5 and self.number_operations < SIZE - 1:
            node.value = random.choice(OPERATORS)
            self.number_operations += 1
            if random.random() <= 0.5:
                node.left = self.generate_random_node(Node(0))
                node.right = self.generate_random_node(Node(0))
            else:
                node.right = self.generate_random_node(Node(0))
                node.left = self.generate_random_node(Node(0))
        else:
            node.value = self.numbers.pop()
        return node

    def generate_random_tree(self):
        self.number_operations = 0
        root = Node(0)

        self.root = self.generate_random_node(root)
        if not self.curate_tree():
            self.generate_random_tree()


class Fenotype:
    left_tree: Tree
    right_tree: Tree
    lnumbers: list[float]
    rnumbers: list[float]

    def __init__(
        self,
        lnumbers: list[float] = None,
        rnumbers: list[float] = None,
        left_tree: Tree = None,
        right_tree: Tree = None,
        name: str = None,
    ):
        if name:
            f = self.load_fjson(name)
            self.left_tree = f.left_tree
            self.right_tree = f.right_tree
            self.lnumbers = f.lnumbers
            self.rnumbers = f.rnumbers
        else:
            self.lnumbers = lnumbers
            self.rnumbers = rnumbers
            if not left_tree or not right_tree:
                self.left_tree = RandomTree(SIZE)
                self.right_tree = RandomTree(SIZE)
            else:
                self.left_tree = left_tree
                self.right_tree = right_tree

    def compute_value(self, node: Node, numbers: list[float]):
        if node.value in OPERATORS:
            left = self.compute_value(node.left, numbers)
            right = self.compute_value(node.right, numbers)
            return eval(f"{left}{node.value}{right}")
        else:
            return numbers[node.value]

    def compute_distance(self):
        if not self.left_tree.is_valid_tree() or not self.right_tree.is_valid_tree():
            return math.inf
        try:
            left_value = self.compute_value(self.left_tree.root, self.lnumbers)
            right_value = self.compute_value(self.right_tree.root, self.rnumbers)
            return abs(left_value - right_value)
        except Exception:
            return math.inf

    def store_fenotype(self, name: str):
        with open(name, "wb") as f:
            pickle.dump(self, f)

    def load_fjson(self, name: str):
        with open(name, "rb") as f:
            return pickle.load(f)


def visualize_individuo(ind: Fenotype):

    def replace_values(node: Node, values: list[float]):
        if node.value in OPERATORS:
            node.left = replace_values(node.left, values)
            node.right = replace_values(node.right, values)
        else:
            node.value = values[node.value]
        return node

    left = replace_values(ind.left_tree.root, ind.lnumbers)
    right = replace_values(ind.right_tree.root, ind.rnumbers)
    print(f"Left tree: {left}")
    print(f"Right tree: {right}")
