"""
Working with Lackenby"s taut ideal triangulations as described in

http://arxiv.org/abs/math/0003132

A taut ideal triangulation gives an angle structure where all the angles are 0 or pi.
Such an angle structure gives instructions on how to turn the 2-skeleton of the ideal triangulation into a branched surface.
When this branched surface is orientable, one has a taut ideal triangulation in the sense of Lackenby's paper.

Based on code joint with Nathan M Dunfield.
"""

from collections import Counter, namedtuple
from itertools import groupby

import networkx as nx
import snappy
import snappy.snap.t3mlite as t3m
from snappy.snap.t3mlite.simplex import E01, E02, E03, E12, E13, E23, F0
from snappy.snap.t3mlite.simplex import VerticesOfFaceCounterclockwise as VerticesOfFace

import flipper

EdgeToQuad = {E01: 2, E02: 1, E03: 0, E12: 0, E13: 1, E23: 2}
VerticesOfFaceIndex = dict(((face, vertex), index) for face, vertices in VerticesOfFace.items() for index, vertex in enumerate(vertices))
Compose = dict(
    ((face, vertex), (VerticesOfFace[face][VerticesOfFaceIndex[face, vertex] - 2], VerticesOfFace[face][VerticesOfFaceIndex[face, vertex] - 1]))
    for face, vertex in VerticesOfFaceIndex
    )

def walk(arrow, end=None):
    """ Yield all of  the arrows around an edge in turn (until end is reached). """

    arrow = arrow.copy()
    for _ in range(arrow.axis().valence()):
        yield arrow.copy()
        arrow.next()
        if arrow == end: return

t3m.Edge.arrows_around = lambda self: walk(self.get_arrow())
t3m.Arrow.face_index = lambda self: self.Tetrahedron.Class[self.Face].Index
t3m.Arrow.oriented_face = lambda self: (self.Tetrahedron.Index, self.Face)

class Surface(object):
    """ An oriented surface carried by the branched surface associated to a taut structure. """

    def __init__(self, taut_str, weights):
        self.taut_str = taut_str
        self.weights = weights
        self.euler_characteristic = -sum(self.weights) // 2

    def __repr__(self):
        return "<Surface: %s>" % self.weights

    def __eq__(self, other):
        if isinstance(other, Surface):
            return self.taut_str == other.taut_str and self.weights == other.weights

        return NotImplemented

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(tuple(self.weights))

    def __add__(self, other):
        if isinstance(other, Surface):
            assert self.taut_str == other.taut_str
            weights = [a + b for a, b in zip(self.weights, other.weights)]
            return Surface(self.taut_str, weights)

        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def triangulation_data(self):
        """ Return a list of namedtuples:
            (triangle name, side, edge name, sign along locus)
        where triangle name is the pari: (sector index, sheet index)
        and edge_name is the pair: (locus index, sheet at locus)
        """

        Data = namedtuple("Data", ["triangle_name", "side", "edge_name", "sign"])

        data = []
        for index, sides in enumerate(self.taut_str.branch_loci):
            for side in sides:
                i = 0
                for arrow in side:
                    sect_index = arrow.face_index()
                    weight = self.weights[sect_index]
                    triangle_side = VerticesOfFaceIndex[arrow.Face, arrow.Face ^ arrow.Edge]
                    sign = arrow.Tetrahedron.get_orientation_of_edge(*Compose[arrow.Face, arrow.Face ^ arrow.Edge])
                    for w in range(weight):
                        data.append(Data((sect_index, w), triangle_side, (index, i + w), sign))
                    i += weight

        return sorted(data)

    def flipper_triangulation(self):
        """ Return this surface as a flipper triangulation. """

        data = self.triangulation_data()

        edges = sorted({d.edge_name for d in data})  # Remove duplicates.
        edge_lookup = dict((edge, index) for index, edge in enumerate(edges))

        ans = [tuple(edge_lookup[datum.edge_name] if datum.sign == +1 else ~edge_lookup[datum.edge_name] for datum in x) for x in zip(data[::3], data[1::3], data[2::3])]
        return flipper.create_triangulation(ans)

    def connected_component(self):
        """ Return a connected subsurface together with the sorted list of edges used. """

        data = self.triangulation_data()

        G = nx.MultiGraph()
        G.add_nodes_from(datum.triangle_name for datum in data)  # Triangle_name = (sector index, sheet index).
        for edge, triangles in groupby(sorted(data, key=lambda d: d.edge_name), lambda d: d.edge_name):
            A, B = triangles  # Have to unpack the generator.
            G.add_edge(A.triangle_name, B.triangle_name, label=edge)

        component = nx.algorithms.components.node_connected_component(G, next(iter(G)))
        edges = sorted({x[2] for y in component for x in G.edges(y, data='label')})  # Get the edge_names.

        counts = Counter(section for section, _ in component)
        weights = [counts[i] for i in range(len(self.weights))]
        return Surface(self.taut_str, weights), edges

    def has_full_support(self):
        """ Return whether this surface has full support, that is, meets all faces of the TautStructure. """

        return min(self.weights) > 0


class TautStructure(object):
    """ Represents a taut structure on a triangulation.

    This is specified by a collection of SnapPy.Arrows which define a dihedral of a Tetrahedron.
    These are produced in branch_loci blocks which, for each edge of the triangulation, is a pair of lists of arrows.
    """
    def __init__(self, manifold, angle_vector):
        self.manifold = manifold
        self.angle_vector = angle_vector
        self.pi_quads = [i % 3 for i, a in enumerate(angle_vector[:-1]) if a == 1]

        pi_arrows = [[parrow for arrow in edge.arrows_around() for parrow in [arrow, arrow.copy().reverse()] if self.angle_is_pi(parrow)] for edge in self.manifold.Edges]
        blocks = [(list(walk(S0, E0)), list(walk(S1, E1)), list(walk(E0, S0)), list(walk(E1, S1))) for S0, S1, E0, E1 in pi_arrows]

        G = nx.Graph()
        G.add_nodes_from(arrow.oriented_face() for sides in blocks for side in sides for arrow in side)  # Add a node for every arrow in the triangulation.
        G.add_edges_from((a1.oriented_face(), a2.oriented_face()) for A, B, C, D in blocks for S0, S1 in [(A, B), (C, D)] for a1, a2 in zip(S0 + S1, (S0 + S1)[1:]))

        num_components = nx.algorithms.components.number_connected_components(G)
        if num_components == 1:
            raise ValueError("Branched surface is not orientable")
        assert num_components == 2
        an_orientation = nx.algorithms.components.node_connected_component(G, (0, F0))

        # These are all indexed according their edge's Index.
        self.branch_loci = [[side for side in sides if (side[0].Tetrahedron.Index, side[0].Face) in an_orientation] for sides in blocks]
        self.tops = [[side[0].copy() for side in locus] for locus in self.branch_loci]
        self.bottoms = [[side[-1].copy().next() for side in locus] for locus in self.branch_loci]

        self.surface = self.surface_with_maximal_support()
        if not self.surface.has_full_support():
            raise ValueError("Maximal surface does not have full support")

    @classmethod
    def from_manifold(cls, manifold, N=100, restarts=5):
        """ Return a TautStructure on some triangulation of the given manifold. """

        M0 = manifold.without_hyperbolic_structure()
        M0 = M0.filled_triangulation()
        ans = []
        for _ in range(restarts):
            M = M0.copy()
            for _ in range(N):
                M.randomize()
                if M not in ans:
                    ans.append(M.copy())
        ans = sorted(ans, key=lambda X: X.num_tetrahedra())
        manifolds = [manifold] + [M.with_hyperbolic_structure() for M in ans]
        for M in manifolds:
            try:
                return cls.from_triangulation(M)
            except ValueError:
                pass

        raise ValueError("Could not find taut structure on manifold")

    @classmethod
    def from_triangulation(cls, triangulation):
        """ Return a TautStructure on this triangulation. """

        triangulation = t3m.Mcomplex(triangulation)
        # Write down the angle equations. these are normally inhomogeneous, with:
        #  * sum(angles around edge) = 2pi, and
        #  * sum(angles in triangle) = pi
        # So we add an extra dummy variable (essentially "pi") to make them homogeneous.
        ntets, nedges = len(triangulation.Tetrahedra), len(triangulation.Edges)
        angle_matrix = t3m.linalg.Matrix(nedges + ntets, 3*ntets + 1)

        for i, edge in enumerate(triangulation.Edges):  # Edge equations.
            for arrow in edge.arrows_around():
                t = arrow.Tetrahedron.Index
                q = EdgeToQuad[arrow.Edge]
                angle_matrix[i, 3*t + q] += 1
            angle_matrix[i, 3*ntets] = -2

        for t in range(ntets):  # Triangle equations.
            for q in range(3):
                angle_matrix[nedges + t, 3*t + q] += 1
            angle_matrix[nedges + t, 3*ntets] = -1

        xrays = snappy.FXrays.find_Xrays(angle_matrix.nrows(), angle_matrix.ncols(), angle_matrix.entries(), filtering=True, print_progress=False)
        for xray in xrays:
            try:
                return cls(triangulation, xray)
            except ValueError:
                pass

        raise ValueError("Could not find taut structure on triangulation")

    def __repr__(self):
        return "<TautStructure: %s>" % self.pi_quads

    def angle_is_pi(self, arrow):
        """ Return whether the dihedral angle defined by this arrow is pi. """

        return self.pi_quads[arrow.Tetrahedron.Index] == EdgeToQuad[arrow.Edge]

    def empty_surface(self):
        """ Return the empty surface on this TautStructure. """

        return Surface(self, [0] * 2 * len(self.manifold.Tetrahedra))

    def surfaces(self):
        """ Return a list of extremal surface supported by this TautStructure. """

        W = t3m.linalg.Matrix(len(self.manifold.Edges), len(self.manifold.Faces))
        for i, sides in enumerate(self.branch_loci):
            for j, side in enumerate(sides):
                for arrow in side:
                    W[i, arrow.face_index()] += (-1)**j

        xrays = snappy.FXrays.find_Xrays(W.nrows(), W.ncols(), W.entries(), filtering=False, print_progress=False)
        return [Surface(self, xray) for xray in xrays]

    def surface_with_maximal_support(self):
        """ A reasonably small surface with maximal support """

        return sum(self.surfaces(), self.empty_surface())

    def flipper_bundle_data(self):
        """ Return the flipper triangulation, flip sequence and edge closer defined by following this TautStructure. """

        # How to wrap from the bottom edge back to the top.
        top = dict((arrow.Tetrahedron.Index, index) for index, starts in enumerate(self.tops) for arrow in starts)
        bottom = dict((arrow.Tetrahedron.Index, index) for index, ends in enumerate(self.bottoms) for arrow in ends)
        edge_advance = dict(((loci, sum(self.surface.weights[arrow.face_index()] for arrow in self.branch_loci[loci][0]) - 1), (top[tet], 0)) for tet, loci in bottom.items())

        S0, E0 = self.surface.connected_component()  # Get a component and its edges.
        E_curr = E0
        flips = []
        while True:
            flips += [i for i, edge in enumerate(E_curr) if edge in edge_advance]  # Find the edges where we are not moving directly across.
            E_curr = [edge_advance.get((loci, sheet), (loci, sheet+1)) for loci, sheet in E_curr]  # Move across.
            if sorted(E_curr) == E0:
                break

        F = S0.flipper_triangulation()
        M0 = self.manifold.snappy_manifold()
        image_edge = E0.index(E_curr[0])
        for edge in [image_edge, ~image_edge]:
            try:
                h = F.encode_flips_and_close(flips, 0, edge)
                B = h.bundle(veering=False, _safety=False)
                if M0.is_isometric_to(snappy.Manifold(B)):
                    return F, flips, edge
            except (flipper.AssumptionError, AssertionError):
                pass

        raise RuntimeError("Neither sister triangulations are the starting triangulation")

    def monodromy(self):
        """ Return the flipper encoding defined by this TautStructure. """

        F, flips, edge = self.flipper_bundle_data()
        return F.encode_flips_and_close(flips, 0, edge)

    def flipper_bundle(self, veering=True):
        """ Return the flipper Bundle of the monodromy defined by this TautStructure. """

        return self.monodromy().bundle(veering=veering)

def monodromy_from_bundle(manifold):
    """ Attempt to find a TautStructure on the given manifold and return its monodromy.

    Raises a ValueError if a triangulation with a TautStructure defined on it cannot be found. """

    return TautStructure.from_manifold(manifold).monodromy()

