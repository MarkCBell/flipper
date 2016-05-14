__author__ = 'shannonhorrigan'

import flipper

from sage.all import *


class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __str__(self):
        return "{}, {}".format(self.x, self.y)

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __add__(self, point):
        return Point(self.x + point.x, self.y + point.y)

    def __sub__(self, point):
        return self + -point

    def __mul__(self, scalar):
        return Point(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        return self * scalar

    def vector(self):
        return vector([self.x, self.y])


def create_flat_structure(self):

    assert(self.is_mapping_class())

    stable_lamination = self.splitting_sequence().lamination
    unstable_lamination = self.splitting_sequence().mapping_class.inverse().invariant_lamination()
    periodic_triangulation = self.splitting_sequence().triangulation

    # The list of edges whose vectors are decided. We fix an edge to start the procedure
    known_edges = {periodic_triangulation.edges[0],
                   periodic_triangulation.edge_lookup[~periodic_triangulation.edges[0].label]}

    # The list of edges whose vectors are decided but whose triangles (the unique triangle that the edge is in)
    # we have not inspected.
    pending_edges = {periodic_triangulation.edges[0],
                     periodic_triangulation.edge_lookup[~periodic_triangulation.edges[0].label]}

    # A dictionary in whose keys are edges values are the corresponding vectors.
    # Choose a vector for the edge chosen above.
    edge_vectors = {periodic_triangulation.edges[0]:
                    Point(stable_lamination.geometric[periodic_triangulation.edges[0].index],
                          unstable_lamination.geometric[periodic_triangulation.edges[0].index])}
    edge_vectors[periodic_triangulation.edges[0].reversed_edge] = -edge_vectors[periodic_triangulation.edges[0]]

    while len(known_edges) < len(periodic_triangulation.edges):

        # We are about to inspect edge_1 's triangle so it should no longer be 'pending'
        edge_1 = pending_edges.pop()

        # moving anticlockwise around the triangle from edge_1 brings you to edge_2 then edge_3
        #
        #          /\
        #         /  \
        #        /    \
        #  e_3  v      ^   e_2
        #      /        \
        #     /          \
        #     ------>-----
        #         e_1
        #
        current_triangle = periodic_triangulation.triangle_lookup[edge_1.label]
        edge_2 = current_triangle.edges[current_triangle.edges.index(edge_1) - 2]
        edge_3 = current_triangle.edges[current_triangle.edges.index(edge_1) - 1]

        # If all edges are known then we do nothing.
        if edge_2 in known_edges and edge_3 in known_edges:
            pending_edges = pending_edges - {edge_3, edge_2}
            continue

        # if two of the edges are known we can calculate the third using the formula:
        # edge_1  + edge_2  + edge_3  = 0
        if edge_2 in known_edges:
            pending_edges.remove(edge_2)
            edge_vectors[edge_3] = -(edge_vectors[edge_1] + edge_vectors[edge_2])
            edge_vectors[edge_3.reversed_edge] = -edge_vectors[edge_3]
            known_edges = known_edges | {edge_3, edge_3.reversed_edge}
            pending_edges.add(edge_3.reversed_edge)
            continue

        if edge_3 in known_edges:
            pending_edges.remove(edge_3)
            edge_vectors[edge_2] = -(edge_vectors[edge_1] + edge_vectors[edge_3])
            edge_vectors[edge_2.reversed_edge] = -edge_vectors[edge_2]
            known_edges = known_edges | {edge_2, edge_2.reversed_edge}
            pending_edges.add(edge_2.reversed_edge)
            continue

        # if edge_2 and edge_3 are both unknown:
        else:
            # Here we just choose positive signs in anticipation of changing them later if need be
            e_2 = Point(stable_lamination.geometric[edge_2.index], unstable_lamination.geometric[edge_2.index])
            e_3 = Point(stable_lamination.geometric[edge_3.index], unstable_lamination.geometric[edge_3.index])

            # We will only need the absolute value of the coordinates in edge_1 so we do this:
            e_1 = Point(edge_vectors[edge_1].x, edge_vectors[edge_1].y)
            if e_1.x < 0:
                e_1.x *= -1
            if e_1.y < 0:
                e_1.y *= -1

            # first we take care of the x coordinate
            if e_1.x == e_2.x + e_3.x:
                e_2.x *= -1
                e_3.x *= -1
            elif e_2.x == e_1.x + e_3.x:
                e_2.x *= -1
            elif e_3.x == e_1.x + e_2.x:
                e_3.x *= -1

            # then the y coordinate
            if e_1.y == e_2.y + e_3.y:
                e_2.y *= -1
                e_3.y *= -1
            elif e_2.y == e_1.y + e_3.y:
                e_2.y *= -1
            elif e_3.y == e_1.y + e_2.y:
                e_3.y *= -1

            if edge_vectors[edge_1].x < 0:
                # reflect in the x axis
                e_2.x *= -1
                e_3.x *= -1

            if edge_vectors[edge_1].y < 0:
                # reflect in the y axis
                e_2.y *= -1
                e_3.y *= -1

            edge_vectors[edge_2] = e_2
            edge_vectors[edge_2.reversed_edge] = -e_2
            edge_vectors[edge_3] = e_3
            edge_vectors[edge_3.reversed_edge] = -e_3
            known_edges = known_edges | {edge_2, edge_2.reversed_edge, edge_3, edge_3.reversed_edge}
            pending_edges = pending_edges | {edge_2.reversed_edge, edge_3.reversed_edge}

    for key, val in edge_vectors.items():
        print key, "=>", val

    # check that we do indeed have triangles:
    for current_triangle in periodic_triangulation:
        assert(edge_vectors[current_triangle.edges[0]].x +
               edge_vectors[current_triangle.edges[1]].x +
               edge_vectors[current_triangle.edges[2]].x == 0)
        assert(edge_vectors[current_triangle.edges[0]].y +
               edge_vectors[current_triangle.edges[1]].y +
               edge_vectors[current_triangle.edges[2]].y == 0)

    return edge_vectors


def flipper_to_sage_number_field(self):

    new = NumberField(QQ['x'](self.polynomial.coefficients), 'x')

    x = [0, 1]
    for i in range(self.degree - 2):
        x.append(0)
    # i.e x = 0 + 1*x + 0*x^2 + . . . + 0*x^(self.degree)

    interval = self.polynomial_root.interval

    # below we are finding the place that flipper was using from the list of possible ones that Sage given
    for f in new.places(prec=interval.precision * log(10, 2) + 10):
        if interval.lower <= f(x) * 10**interval.precision <= interval.upper:
            return new, f


def flipper_to_sage_number_field_element(self):

    num_field = NumberField(QQ['x'](self.number_field.polynomial.coefficients), 'x')
    new = num_field(self.linear_combination)

    return new


def build_input(self):
    new = {}
    num_field = flipper_to_sage_number_field(self.items()[0][1].x.number_field)
    for key, val in self.items():
        new[key.label] = vector([flipper_to_sage_number_field_element(val.x),
                                 flipper_to_sage_number_field_element(val.y)])
    return new, num_field
