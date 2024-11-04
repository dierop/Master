import copy
import random

from binarytree import Node

from GeneticAlgorithm.individuo import OPERATORS, Fenotype


class Cross:
    parent1: Node
    parent2: Node
    probability: float

    def __init__(self, parent1, parent2, probability=0.5):
        self.parent1 = parent1
        self.parent2 = parent2
        self.probability = probability

    def layer_left_cross(self):
        child1 = copy.deepcopy(self.parent1)
        child1.root.left = self.parent2.root.left
        child2 = copy.deepcopy(self.parent2)
        child2.root.left = self.parent1.root.left
        return child1, child2

    def layer_right_cross(self):
        child1 = copy.deepcopy(self.parent1)
        child1.root.right = self.parent2.root.right
        child2 = copy.deepcopy(self.parent2)
        child2.root.right = self.parent1.root.right
        return child1, child2

    def _random_cross(self, node1, node2):
        if random.random() < self.probability:
            node1.value = node2.value
        if node1.left and node2.left:
            self._random_cross(node1.left, node2.left)
        if node1.right and node2.right:
            self._random_cross(node1.right, node2.right)
        return node1

    def uniform_1_random_cross(self):
        child = copy.deepcopy(self.parent1)
        child.root = self._random_cross(child.root, self.parent2.root)
        return child

    def uniform_2_random_cross(self):

        child = copy.deepcopy(self.parent2)
        child.root = self._random_cross(child.root, self.parent1.root)
        return child


class Mutation:
    probability: float

    def __init__(self, probability):
        self.probability = probability

    def mutation_left_rigth(self, child: Node):
        if random.random() < self.probability:
            child.left, child.right = child.right, child.left

        return child

    def mutation_left_rigth_values(self, node: Node):
        if random.random() < self.probability:
            node.left.value, node.right.value = node.right.value, node.left.value
        return node

    def mutation_node(self, child: Node, unused_numbers):
        if random.random() < self.probability:
            if random.random() < 0.5 and len(unused_numbers) > 0:
                child.value = random.choice(unused_numbers)
            else:
                child.value = random.choice(OPERATORS)

        return child


class ChildGeneration:
    parent1: Fenotype
    parent2: Fenotype
    probability: float
    cross_types: list[int]
    mutation_types: list[int]

    def __init__(self, parent1, parent2, probability, cross_types, mutation_types):
        self.parent1 = parent1
        self.parent2 = parent2
        self.probability = probability
        self.cross_types = cross_types
        self.mutation_types = mutation_types

    def direct_tree_cross(self):
        child1 = copy.deepcopy(self.parent1)
        child2 = copy.deepcopy(self.parent2)
        child1.left_tree.root, child2.left_tree.root = (
            child2.left_tree.root,
            child1.left_tree.root,
        )
        return child1, child2

    def generate_child(self):
        cross_l = Cross(self.parent1.left_tree, self.parent2.left_tree)
        cross_r = Cross(self.parent1.right_tree, self.parent2.right_tree)
        mutation = Mutation(self.probability)
        children = []
        for cross_type in self.cross_types:
            if cross_type == 1:
                c1l, c2l = cross_l.layer_left_cross()
                c1r, c2r = cross_r.layer_left_cross()
                children.append(
                    Fenotype(
                        lnumbers=self.parent1.lnumbers,
                        rnumbers=self.parent1.rnumbers,
                        left_tree=c1l,
                        right_tree=c1r,
                    )
                )
                children.append(
                    Fenotype(
                        lnumbers=self.parent1.lnumbers,
                        rnumbers=self.parent1.rnumbers,
                        left_tree=c2l,
                        right_tree=c2r,
                    )
                )
            elif cross_type == 2:
                c1l, c2l = cross_l.layer_right_cross()
                c1r, c2r = cross_r.layer_right_cross()
                children.append(
                    Fenotype(
                        lnumbers=self.parent1.lnumbers,
                        rnumbers=self.parent1.rnumbers,
                        left_tree=c1l,
                        right_tree=c1r,
                    )
                )
                children.append(
                    Fenotype(
                        lnumbers=self.parent1.lnumbers,
                        rnumbers=self.parent1.rnumbers,
                        left_tree=c2l,
                        right_tree=c2r,
                    )
                )
            elif cross_type == 3:
                children.append(
                    Fenotype(
                        lnumbers=self.parent1.lnumbers,
                        rnumbers=self.parent1.rnumbers,
                        left_tree=cross_l.uniform_1_random_cross(),
                        right_tree=cross_r.uniform_1_random_cross(),
                    )
                )
            elif cross_type == 4:
                children.append(
                    Fenotype(
                        lnumbers=self.parent1.lnumbers,
                        rnumbers=self.parent1.rnumbers,
                        left_tree=cross_l.uniform_2_random_cross(),
                        right_tree=cross_r.uniform_2_random_cross(),
                    )
                )
            elif cross_type == 5:
                c1, c2 = self.direct_tree_cross()
                children.append(c1)
                children.append(c2)

        for child in children:
            select_mutation = random.choice(self.mutation_types)
            if select_mutation == 1:
                child.left_tree.root = mutation.mutation_left_rigth(
                    child.left_tree.root
                )
                child.right_tree.root = mutation.mutation_left_rigth(
                    child.right_tree.root
                )
            elif select_mutation == 2:
                child.left_tree.root = mutation.mutation_left_rigth_values(
                    child.left_tree.root
                )
                child.right_tree.root = mutation.mutation_left_rigth_values(
                    child.right_tree.root
                )
            elif select_mutation == 3:
                child.left_tree.root = mutation.mutation_node(
                    child.left_tree.root, child.left_tree.get_unused_numbers()
                )
                child.right_tree.root = mutation.mutation_node(
                    child.right_tree.root, child.right_tree.get_unused_numbers()
                )

        return self.curate_children(children)

    def curate_children(self, children):
        good_children = []
        for child in children:
            if child.left_tree.curate_tree() and child.right_tree.curate_tree():
                good_children.append(child)

        return good_children


class GenerateNextGeneration:
    parent_list: list[Fenotype]
    probability: float
    cross_types: list[int]
    mutation_types: list[int]
    quantity: int

    def __init__(self, parent_list, probability, cross_types, mutation_types, quantity):
        self.parent_list = copy.deepcopy(parent_list)
        self.parent_list.reverse()
        self.probability = probability
        self.cross_types = cross_types
        self.mutation_types = mutation_types
        self.quantity = quantity

    def generate_children(self):
        children = []
        aux_list = self.parent_list.copy()
        while len(children) < self.quantity:
            parent1 = self.parent_list.pop()
            parent2 = self.parent_list.pop()
            cg = ChildGeneration(
                parent1,
                parent2,
                self.probability,
                self.cross_types,
                self.mutation_types,
            )
            children += cg.generate_child()
            if len(self.parent_list) <= 1:
                random.shuffle(aux_list)
                self.parent_list = aux_list.copy()
        return children[: self.quantity]
