
# Based on code by William Worden.

import flipper
from itertools import combinations

def LP(genus, num_punctures):
    g = int(genus)
    n = int(num_punctures)
    
    # The following functions make edge labelling easier.
    # In the picture of the triangulation in documentation, some edges are labelled with colored numbers.
    # The below function convert these coloured numbers to indices.
    # For example, if an edge of the triangulation is labelled 5 and colored green then its index is 5+2*g (or 2 if g = 1).
    
    green = lambda m: m + 2*g if g > 1 else 2
    pink = lambda m: m + 4*g if g > 2 else 8
    blue = lambda m: m + 5*g
    orange = lambda m: m + 6*g - 3
    
    empty_lam = lambda: [0 for i in range(6*g+3*n-6)]
    
    if g == 0:
        triangles = [(3*i, 3*i+2, ~(3*((i+1) % (n-2)))) for i in range(n-2)] + [(3*i+1, ~(3*((i+1) % (n-2))+1), ~(3*i+2)) for i in range(n-2)]
        
        lams = dict()
        for i in range(n):
            lams['q'+str(i)] = empty_lam()
        for j in range(3, 3*n-8, 3) + [1, 2, 3*n-7]:
            lams['q0'][j] += 1
        for j in range(3, 6) + [0, 1, 3*n-7]:
            lams['q1'][j] += 1
        for i in range(0, n-4):
            for j in range(3*i+2, 3*i+5) + range(3*i+6, 3*i+9):
                lams['q'+str(i+2)][j] += 1
        for j in range(1, 3*n-8, 3) + [3*n-10, 3*n-9, 3*n-7]:
            lams['q'+str(n-2)][j] += 1
        for j in range(1, 3*n-7, 3) + range(0, 3*n-8, 3)+[3*n-7, 3*n-7]:
            lams['q'+str(n-1)][j] += 1
    else:
        if g >= 1:
            triangles = [(k, k+1, green(k)) for k in range(0, 2*g-1, 2)] + [(~k, ~(k+1), ~green(k+1)) for k in range(0, 2*g-1, 2)]
        if g > 2:
            triangles += [(~green(k), green(k+1), ~pink(k/2)) for k in range(0, 2*g-1, 2)]
        if g == 2:
            triangles += [(~green(0), green(1), ~pink(0)), (~green(2), green(3), pink(0))]
        if g == 3:
            triangles += [(pink(0), pink(1), pink(2))]
        if g > 3:
            triangles += [(blue(k), pink(k+2), ~blue(k+1)) for k in range(0, g-4)] + [(pink(0), pink(1), ~blue(0)), (pink(g-2), pink(g-1), blue(g-4))]
        
        if n == 2:  # For n == 2 we need a certain triangulation, so we can more easily compute the halftwist in terms of flips later.
            triangles.remove((2*g-2, 2*g-1, green(2*g-2)))
            triangles += [(orange(0), ~orange(2), orange(2)), (2*g-2, ~orange(0), orange(1)), (green(2*g-2), ~orange(1), 2*g-1)]
        if n > 2:
            triangles.remove((2*g-2, 2*g-1, green(2*g-2)))
            triangles += [(2*g-2, orange(0), orange(1)), (green(2*g-2), ~orange(3*n-5), orange(3*n-4)), (2*g-1, ~orange(3*n-4), ~orange(3*n-6))]
            triangles += [(~orange(k), orange(k+3), ~orange(k+2)) for k in range(0, 3*n-8, 3)] + [(~orange(k+1), orange(k+2), orange(k+4)) for k in range(0, 3*n-8, 3)]
        
        lams = dict()
        if g == 1:
            lams['a0'] = empty_lam()
            lams['a0'][1] += 1
            lams['a0'][green(0)] += 1
            lams['b0'] = empty_lam()
            lams['b0'][0] += 1
            lams['b0'][green(0)] += 1
        elif g > 1:
            for i in [0, 1]:
                lams['a'+str(i)] = empty_lam()
                for j in [2*i+1, green(2*i), green(2*i+1)]:
                    lams['a'+str(i)][j] += 1
            for i in range(g):
                lams['b'+str(i)] = empty_lam()
                for j in [2*i, green(2*i), green(2*i+1)]:
                    lams['b'+str(i)][j] += 1
        if g == 2:
            lams['c0'] = empty_lam()
            for j in [1, green(0), pink(0), green(2), 2, green(3), green(2), 3, 2, green(2), pink(0), green(1)]:
                lams['c0'][j] += 1
        elif g > 2:
            for i in range(g-1):
                lams['c'+str(i)] = empty_lam()
                for j in [2*i+1, green(2*i), pink(i), pink(i+1), green(2*i+2), 2*i+2, green(2*i+3), green(2*i+2), 2*i+3, 2*i+2, green(2*i+2), pink(i+1), pink(i), green(2*i+1)]:
                    lams['c'+str(i)][j] += 1
            for i in range(1, g-2):
                lams['c'+str(i)][blue(i-1)] += 2
        if n == 2:
            lams['b'+str(g-1)][orange(1)] += 1
            if 'c'+str(g-2) in lams.keys():
                lams['c'+str(g-2)][orange(1)] += 2
            lams['p0'] = empty_lam()
            for j in [2*g-1, green(2*g-1), green(2*g-2), orange(0), orange(0), orange(1), orange(1), orange(2)]:
                lams['p0'][j] += 1
            if g == 1:
                for i in range(n-1):
                    lams['p'+str(i)][green(2*g-1)] -= 1
            lams['q0'] = [2 for i in range(6*g+3*n-6)]
            lams['q0'][orange(0)] -= 2
            lams['q0'][orange(2)] -= 2
        if n > 2:
            if 'a'+str(g-1) in lams.keys():
                lams['a'+str(g-1)][orange(3*n-4)] += 1
            for j in [orange(3*k+1) for k in range(n-1)]:
                lams['b'+str(g-1)][j] += 1
            if 'c'+str(g-2) in lams.keys():
                for j in [orange(3*n-4)] + [orange(3*k+1) for k in range(n-1)] + [orange(3*k+1) for k in range(n-1)]:
                    lams['c'+str(g-2)][j] += 1
            lams['p0'] = empty_lam()
            for j in [2*g-1, green(2*g-1), green(2*g-2)]+[orange(3*k) for k in range(n-1)]+[orange(3*k+1) for k in range(n-1)]:
                lams['p0'][j] += 1
            for i in range(1, n-1):
                lams['p'+str(i)] = empty_lam()
                for j in [2*g-1, green(2*g-1), green(2*g-2), orange(3*i-1)] + [orange(3*k) for k in range(i, n-1)] + [orange(3*k+1) for k in range(i, n-1)]:
                    lams['p'+str(i)][j] += 1
            if g == 1:
                for i in range(n-1):
                    lams['p'+str(i)][green(2*g-1)] -= 1
            
            lams['q0'] = [2 for i in range(6*g+3*n-6)]
            for j in [orange(3*k+2) for k in range(1, n-2)]+[orange(0)]:
                lams['q0'][j] -= 2
            for j in [orange(3*k) for k in range(1, n-1)]+[orange(3*k+1) for k in range(1, n-1)]+[orange(2), orange(3*n-4)]:
                lams['q0'][j] -= 1
            
            lams['q1'] = empty_lam()
            for j in [orange(0), orange(1), orange(3), orange(4), orange(5)]:
                lams['q1'][j] += 1
            for i in range(2, n-1):
                lams['q'+str(i)] = empty_lam()
                for j in [orange(3*(i-1)-1), orange(3*(i-1)), orange(3*(i-1)+1), orange(3*(i-1)+3), orange(3*(i-1)+4), orange(3*(i-1)+5)]:
                    lams['q'+str(i)][j] += 1
    
    triangulation = flipper.create_triangulation(triangles)
    
    # Below we compute the halftwist around the isolating curve bounding the two punctures, for the n == 2 case, in terms of flips.
    # We then relable the edges, and re-create the triangulation, since we have altered the original one in the process of finding the flips.
    if n == 2:
        def _edges_around_vert(t, vert):
            """ Return the cyclically ordered list of edges around the given vertex.
            
            Vertex is input as an int corresponding to its index.
            That is, for vertex "Puncture 0", do edges_around_vert(t, 0). """
            
            crns = t.corner_class_of_vertex(t.vertices[vert])
            edges = [crns[i].edges[1].label for i in range(len(crns))]
            edges.reverse()
            return edges
        
        t = triangulation
        seq = []
        vert = 0 if len(_edges_around_vert(t, 0)) > 1 else 1
        edges = _edges_around_vert(t, vert)
        fixed_edge = orange(2) if orange(2) in edges else ~orange(2)
        ind = edges.index(fixed_edge)
        edges_0 = [edges[(ind+i) % len(edges)] for i in range(len(edges))]
        while len(edges) > 1:
            ind = (edges.index(fixed_edge) + 1) % len(edges)
            seq.append(edges[ind])
            t = t.flip_edge(edges[ind])
            edges = _edges_around_vert(t, vert)
        edges = _edges_around_vert(t, (vert+1) % 2)
        ind = edges.index(~fixed_edge)
        edges = [edges[(ind + i) % len(edges)] for i in range(len(edges))]
        isom = dict(zip(edges, edges_0))
        seq.append(isom)
        seq.reverse()
        triangulation = flipper.create_triangulation(triangles)
        isolating_halftwist = triangulation.encode(seq)
    
    laminations = dict([(key, triangulation.lamination(value)) for key, value in lams.items()])
    
    twists = dict()
    halftwists = dict()
    
    # If n == 2 then we have to add the halftwist (created above from flips) seperately.
    # It seems that the halftwist computed above is actually the right Dehn twist (based on the check below using chain relation).
    # So it is called 'Q0' and its inverse is 'q0' (lower case indicates left twists, upper case right twists).
    if n == 2:
        # halftwists['Q0'] = isolating_halftwist
        halftwists['q0'] = isolating_halftwist.inverse()
    
    for key in lams.keys():
        if key == 'q0' and n == 2:
            pass
        elif key[0] == 'q':
            halftwists[key] = laminations[key].encode_halftwist(1)
            # halftwists[key.upper()] = laminations[key].encode_halftwist(-1)
        else:
            twists[key] = laminations[key].encode_twist(1)
            # twists[key.upper()] = laminations[key].encode_twist(-1)
    all_twists = dict([(key, value) for key, value in twists.items()] + [(key, value) for key, value in halftwists.items()])
    
    return flipper.kernel.EquippedTriangulation(triangulation, laminations, all_twists)


def _check(surface):
    # Check to make sure the MCG generator curves have the correct geometric intersection properties.
    # This was used as a test to make sure there were no errors in the code above that creates the laminations.
    # This of course is not sufficient to guarantee that there are no errors, but its a good start.
    # Surfaces S_{g, n} for 1 <= g <= 5 and 1 <= n <= 20 have been checked.
    
    if surface.triangulation.num_vertices == 2:
        # Check the square of the halftwist against the chain relation.
        # This confirms that the computation of the halftwists in terms of flips was successful.
        # All surfaces S_{g, 2} for g < 23 have been tested.
        g = surface.triangulation.genus
        chain = surface.mapping_class('a0.b0.' + '.'.join('c%d.b%d' % (i, i+1) for i in range(g-1)))
        assert(chain**(4*g+2) == surface.mapping_class('q0.q0'))
    
    def intersection(l1, l2):
        return surface.lamination(l1).geometric_intersection(surface.lamination(l2))
    keys = sorted(surface.laminations.keys())
    intersections = dict([(tuple(sorted([l1, l2])), intersection(l1, l2)) for l1, l2 in combinations(keys, 2) if intersection(l1, l2) != 0])
    if surface.triangulation.genus == 1:
        expected = dict(
            [(('a0', 'b0'), 1)]
            + [(('b0', 'p{}'.format(i)), 1) for i in range(surface.triangulation.num_vertices-1)]
            + [(('p{}'.format(i), 'q{}'.format(i)), 2) for i in range(surface.triangulation.num_vertices-1)]
            + [(tuple(sorted(['q{}'.format(i), 'q{}'.format(i+1)])), 2) for i in range(surface.triangulation.num_vertices-2)]
            )
    else:
        expected = dict(
            [(('a0', 'b0'), 1), (('a1', 'b1'), 1), (('b0', 'c0'), 1)] +
            + [(('b{}'.format(i), 'c{}'.format(i-1)), 1) for i in range(1, surface.triangulation.genus)]
            + [(('b{}'.format(i), 'c{}'.format(i)), 1) for i in range(1, surface.triangulation.genus-1)]
            + [(('b{}'.format(surface.triangulation.genus-1), 'p{}'.format(i)), 1) for i in range(surface. triangulation.num_vertices-1)]
            + [(('p{}'.format(i), 'q{}'.format(i)), 2) for i in range(surface.triangulation.num_vertices-1)]
            + [(tuple(sorted(['q{}'.format(i), 'q{}'.format(i+1)])), 2) for i in range(surface.triangulation.num_vertices-2)]
            )
    return expected == intersections

